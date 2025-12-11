"""
Sarmad MVP - FastAPI Backend Server
Main entry point with WebSocket support for real-time updates.
Now connects to MockX platform for data.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
import json
import os
import sys

# Add current directory to path so we can import local modules
# regardless of where the script is run from
sys.path.append(os.path.dirname(__file__))
import httpx
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("SarmadBackend")

from nlp_engine import extract_semantic_fingerprint, find_tweets_with_keywords
from search_algorithm import find_patient_zero, SearchProgress, format_search_log

# MockX API URL
MOCKX_API_URL = os.environ.get("MOCKX_API_URL", "http://localhost:8001")

app = FastAPI(
    title="Sarmad MVP",
    description="Viral Content Source Detection System",
    version="1.0.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global dataset (fetched from MockX)
dataset: List[Dict[str, Any]] = []
mockx_connected: bool = False


class ReportRequest(BaseModel):
    """Request model for submitting a violation report."""
    tweet_url: str
    description: Optional[str] = None


class AnalysisResponse(BaseModel):
    """Response model for analysis results."""
    status: str
    keywords: List[str]
    source_tweet: Optional[Dict[str, Any]]
    total_tweets: int
    iterations: int


# ==================== API Endpoints ====================

async def fetch_from_mockx():
    """Fetch dataset from MockX platform."""
    global dataset, mockx_connected
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{MOCKX_API_URL}/api/v2/data/export")
            if response.status_code == 200:
                data = response.json()
                dataset = data.get("data", [])
                mockx_connected = True
                logger.info(f"✅ Connected to MockX: {len(dataset)} tweets fetched")
                return True
            else:
                logger.warning(f"⚠️ MockX returned status {response.status_code}")
    except Exception as e:
        logger.warning(f"⚠️ MockX not available: {e}. Starting in offline mode.")
        mockx_connected = False
    
    # Fallback: generate locally if MockX not available
    from data_generator import generate_synthetic_dataset
    dataset = generate_synthetic_dataset()
    logger.info(f"📊 Fallback: Generated {len(dataset)} local tweets")
    return False


@app.on_event("startup")
async def startup_event():
    """Fetch dataset from MockX on startup."""
    await fetch_from_mockx()





@app.get("/api/status")
async def get_status():
    """Get system status."""
    return {
        "status": "online",
        "total_tweets": len(dataset),
        "source_exists": any(t.get("is_source") for t in dataset)
    }


@app.get("/api/tweets")
async def get_tweets(limit: int = 50, offset: int = 0):
    """Get paginated tweet list."""
    return {
        "data": dataset[offset:offset + limit],
        "meta": {
            "total": len(dataset),
            "limit": limit,
            "offset": offset
        }
    }


@app.get("/api/volume")
async def get_volume():
    """Get tweet volume by hour for charting."""
    volume = {}
    for tweet in dataset:
        dt = datetime.fromisoformat(tweet["created_at"].replace("Z", ""))
        hour = dt.hour
        volume[hour] = volume.get(hour, 0) + 1
    return {"data": [{"hour": h, "count": volume.get(h, 0)} for h in range(24)]}


@app.post("/api/regenerate")
async def regenerate_dataset():
    """Regenerate synthetic dataset."""
    global dataset, mock_api
    dataset = generate_synthetic_dataset()
    mock_api = create_mock_api(dataset)
    return {
        "status": "success",
        "total_tweets": len(dataset)
    }


@app.get("/api/analyze/keywords")
async def analyze_keywords():
    """Extract semantic fingerprint from dataset."""
    fingerprint = extract_semantic_fingerprint(dataset)
    return {
        "top_keywords": fingerprint["top_keywords"],
        "top_bigrams": fingerprint["top_bigrams"],
        "hashtag_freq": fingerprint["hashtag_freq"],
        "total_analyzed": fingerprint["total_tweets_analyzed"]
    }


@app.get("/api/search/tweets")
async def search_tweets(
    query: str,
    start_hour: int = 0,
    end_hour: int = 24
):
    """Search tweets by keyword and time range."""
    results = []
    
    for tweet in dataset:
        if query.lower() in tweet.get("text", "").lower():
            tweet_time = datetime.fromisoformat(tweet["created_at"].replace("Z", ""))
            hour = tweet_time.hour
            if start_hour <= hour < end_hour:
                results.append(tweet)
    
    return {
        "data": results[:100],
        "meta": {"total": len(results)}
    }


# ==================== Reports Management API ====================

from reports_manager import ReportsManager, ReportStatus, CancelReason

reports_manager = ReportsManager()


class CreateReportRequest(BaseModel):
    """Request model for creating a new report."""
    tweet_url: str
    description: str
    reporter_name: str
    reporter_phone: str
    reporter_id: Optional[str] = None


class UpdateStatusRequest(BaseModel):
    """Request model for updating report status."""
    status: str
    cancel_reason: Optional[str] = None
    source_tweet_id: Optional[str] = None


@app.post("/api/reports")
async def create_report(request: CreateReportRequest):
    """Create a new violation report."""
    try:
        report = reports_manager.create_report(
            tweet_url=request.tweet_url,
            description=request.description,
            reporter_name=request.reporter_name,
            reporter_phone=request.reporter_phone,
            reporter_id=request.reporter_id
        )
        logger.info(f"📥 New report created: {report.id}")
        return {"id": report.id, "status": "created"}
    except Exception as e:
        logger.error(f"Error creating report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/reports")
async def get_reports(status: str = None):
    """Get all reports, optionally filtered by status."""
    reports = reports_manager.get_all_reports(status)
    stats = reports_manager.get_statistics()
    return {
        "reports": [r.to_dict() for r in reports],
        "stats": stats
    }


@app.get("/api/reports/{report_id}")
async def get_report(report_id: str):
    """Get a single report by ID."""
    report = reports_manager.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report.to_dict()


@app.post("/api/reports/{report_id}/activate")
async def activate_report(report_id: str):
    """Activate a report for analysis."""
    report = reports_manager.activate_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    logger.info(f"🔍 Report activated: {report_id}")
    return {"status": "activated"}


@app.post("/api/reports/{report_id}/resolve")
async def resolve_report(report_id: str, source_tweet_id: str):
    """Mark a report as resolved with source found."""
    report = reports_manager.resolve_report(report_id, source_tweet_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    logger.info(f"✅ Report resolved: {report_id}")
    return {"status": "resolved"}


@app.post("/api/reports/{report_id}/cancel")
async def cancel_report(report_id: str, reason: str):
    """Cancel a report with reason."""
    report = reports_manager.cancel_report(report_id, reason)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    logger.info(f"❌ Report cancelled: {report_id} - {reason}")
    return {"status": "cancelled"}


# ==================== WebSocket for Real-time Updates ====================

class ConnectionManager:
    """Manage WebSocket connections."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass


manager = ConnectionManager()


@app.websocket("/ws/analysis")
async def websocket_analysis(websocket: WebSocket):
    """
    WebSocket endpoint for real-time analysis.
    
    Message types:
    - start_analysis: Begin the full analysis pipeline
    - status: System status update
    - log: Console log message
    - nlp_result: NLP extraction results
    - search_progress: Binary search progress
    - source_found: Final source tweet found
    """
    await manager.connect(websocket)
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data.get("action") == "start_analysis":
                # Run the full analysis pipeline
                reported_tweet_id = data.get("tweet_id")
                await run_analysis_pipeline(websocket, reported_tweet_id)
            
            elif data.get("action") == "get_tweets":
                # Send tweet batch
                limit = data.get("limit", 50)
                offset = data.get("offset", 0)
                logger.info(f"WebSocket: Sending {min(limit, len(dataset))} tweets (offset={offset})")
                await websocket.send_json({
                    "type": "tweets",
                    "data": dataset[offset:offset + limit],
                    "total": len(dataset)
                })
            elif data.get("action") == "get_volume":
                # Send volume data
                volume = {}
                for t in dataset:
                    dt = datetime.fromisoformat(t["created_at"].replace("Z", ""))
                    volume[dt.hour] = volume.get(dt.hour, 0) + 1
                logger.info("WebSocket: Sending volume data")
                await websocket.send_json({
                    "type": "volume",
                    "data": [{"hour": h, "count": volume.get(h, 0)} for h in range(24)]
                })
    
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        manager.disconnect(websocket)


async def run_analysis_pipeline(websocket: WebSocket, reported_tweet_id: str = None):
    """
    Execute the full analysis pipeline with real-time updates.
    
    Pipeline:
    1. Status check
    2. NLP extraction (Crowd Echo)
    3. Binary search (Patient Zero) or Trace Conversation
    4. Source identification
    """
    from search_algorithm import find_source_from_report
    
    async def send_log(msg: str, level: str = "info"):
        # Log to console as well
        if level == "error":
            logger.error(f"Analysis: {msg}")
        elif level == "success":
            logger.info(f"Analysis: ✅ {msg}")
        else:
            logger.info(f"Analysis: {msg}")
            
        await websocket.send_json({
            "type": "log",
            "message": msg,
            "level": level,
            "timestamp": datetime.now().isoformat()
        })
    
    try:
        # ========== Phase 1: Initialization ==========
        await websocket.send_json({"type": "status", "status": "analyzing"})
        await send_log("🚀 بدء نظام الرصد والتحليل...")
        await asyncio.sleep(0.5)
        
        await send_log(f"📊 تحميل قاعدة البيانات: {len(dataset)} تغريدة")
        await asyncio.sleep(0.3)
        
        # Send initial volume data
        volume = {}
        for t in dataset:
            dt = datetime.fromisoformat(t["created_at"].replace("Z", ""))
            volume[dt.hour] = volume.get(dt.hour, 0) + 1
        await websocket.send_json({
            "type": "volume",
            "data": [{"hour": h, "count": volume.get(h, 0)} for h in range(24)]
        })
        
        # ========== Phase 2: NLP Extraction ==========
        await send_log("🔤 بدء خوارزمية استخراج البصمة الدلالية (Crowd Echo)...")
        await asyncio.sleep(0.8)
        
        await send_log("   → تجزئة النص العربي (Tokenization)")
        await asyncio.sleep(0.4)
        
        await send_log("   → إزالة كلمات التوقف (Stop-word Removal)")
        await asyncio.sleep(0.4)
        
        await send_log("   → حساب تكرار الكلمات (N-gram Frequency)")
        await asyncio.sleep(0.4)
        
        # Actually run NLP
        fingerprint = extract_semantic_fingerprint(dataset)
        keywords = fingerprint["top_keywords"]
        
        await websocket.send_json({
            "type": "nlp_result",
            "keywords": keywords,
            "bigrams": fingerprint["top_bigrams"],
            "hashtags": dict(list(fingerprint["hashtag_freq"].items())[:5]),
            "analyzed_count": fingerprint["total_tweets_analyzed"]
        })
        
        await send_log(f"✅ تم استخراج الكلمات المفتاحية: {keywords}", "success")
        await asyncio.sleep(0.5)
        
        # ========== Phase 3: Search Strategy ==========
        await websocket.send_json({"type": "status", "status": "searching"})
        
        result = None
        
        if reported_tweet_id:
            await send_log(f"🔍 تحليل تسلسل المحادثة للمنشور المبلغ عنه ({reported_tweet_id})...")
            result = await find_source_from_report(dataset, reported_tweet_id, keywords)
            
            if result.search_path and result.search_path[0].decision == "trace_conversation":
                await send_log("   → تتبع شجرة الردود للوصول للجذر")
                await asyncio.sleep(1.0)
        
        # Fallback to standard binary search if no result from tracing
        if not result or not result.found:
            await send_log("🔍 بدء خوارزمية البحث الزمني (Spatio-Temporal Binary Search)...")
            await asyncio.sleep(0.5)
            
            # Progress callback for binary search
            async def on_search_progress(progress: SearchProgress):
                await websocket.send_json({
                    "type": "search_progress",
                    "iteration": progress.iteration,
                    "low": progress.low.isoformat(),
                    "mid": progress.mid.isoformat(),
                    "high": progress.high.isoformat(),
                    "low_hour": progress.low.hour + progress.low.minute / 60,
                    "high_hour": progress.high.hour + progress.high.minute / 60,
                    "count": progress.count_in_range,
                    "decision": progress.decision,
                    "window_minutes": progress.window_size_minutes
                })
                
                log_msg = format_search_log(progress)
                await send_log(log_msg)
            
            # Run binary search
            result = await find_patient_zero(
                dataset, 
                keywords, 
                on_progress=on_search_progress,
                delay_ms=1000
            )
        
        # ========== Phase 4: Source Found ==========
        await websocket.send_json({"type": "status", "status": "found"})
        
        if result.found and result.source_tweet:
            await send_log(f"🎯 تم تحديد المصدر الأولي!", "success")
            await send_log(f"   المستخدم: {result.source_tweet['author']['username']}")
            await send_log(f"   الوقت: {result.source_tweet['created_at']}")
            
            await websocket.send_json({
                "type": "source_found",
                "tweet": result.source_tweet,
                "iterations": result.total_iterations,
                "final_window": {
                    "start": result.final_window_start.isoformat(),
                    "end": result.final_window_end.isoformat()
                }
            })
        else:
            await send_log("❌ لم يتم العثور على المصدر", "error")
        
        await websocket.send_json({"type": "analysis_complete"})
    
    except Exception as e:
        await send_log(f"❌ خطأ: {str(e)}", "error")
        logger.exception("Error in analysis pipeline")
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })


# ==================== Static Files ====================

# Serve different frontend directories
base_dir = os.path.dirname(os.path.dirname(__file__))

# Sarmad Dashboard
dashboard_dir = os.path.join(base_dir, "sarmad-dashboard")
if os.path.exists(dashboard_dir):
    app.mount("/dashboard", StaticFiles(directory=dashboard_dir, html=True), name="dashboard")

# Reports Portal
reports_dir = os.path.join(base_dir, "reports-portal")
if os.path.exists(reports_dir):
    app.mount("/reports", StaticFiles(directory=reports_dir, html=True), name="reports")

# Graphs Visualization
graphs_dir = os.path.join(base_dir, "graphs")
if os.path.exists(graphs_dir):
    app.mount("/graphs", StaticFiles(directory=graphs_dir, html=True), name="graphs")

# Frontend (main Sarmad analysis page) - must be last as it's the root
frontend_dir = os.path.join(base_dir, "frontend")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

