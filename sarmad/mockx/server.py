"""
MockX - Twitter/X Clone Social Media Platform
Backend API server running on port 8001
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
import json
import os
import sys

# Add parent directory to path to import from backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
from data_generator import generate_synthetic_dataset, get_volume_by_hour

app = FastAPI(
    title="MockX - Social Media Simulator",
    description="Twitter/X Clone for testing Sarmad",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global synthetic dataset
dataset: List[Dict[str, Any]] = []
users_index: Dict[str, Dict] = {}
trending: List[Dict] = []


class ReportRequest(BaseModel):
    tweet_id: str
    reason: str


@app.on_event("startup")
async def startup():
    """Generate dataset on startup."""
    global dataset, users_index, trending
    dataset = generate_synthetic_dataset()
    
    # Index users
    for tweet in dataset:
        author = tweet.get("author", {})
        user_id = author.get("id")
        if user_id and user_id not in users_index:
            users_index[user_id] = {
                "id": user_id,
                "username": author.get("username", "@user"),
                "name": author.get("name", "مستخدم"),
                "reliability_score": author.get("reliability_score", 0.5),
                "followers_count": hash(user_id) % 10000,
                "following_count": hash(user_id) % 1000,
                "tweet_count": 1,
                "verified": hash(user_id) % 10 == 0,
                "created_at": "2020-01-01T00:00:00Z"
            }
        elif user_id:
            users_index[user_id]["tweet_count"] += 1
    
    # Calculate trending
    hashtag_counts = {}
    for tweet in dataset:
        for ht in tweet.get("entities", {}).get("hashtags", []):
            tag = ht.get("tag", "")
            hashtag_counts[tag] = hashtag_counts.get(tag, 0) + 1
    
    trending = [
        {"tag": tag, "count": count, "rank": i+1}
        for i, (tag, count) in enumerate(
            sorted(hashtag_counts.items(), key=lambda x: -x[1])[:10]
        )
    ]
    
    print(f"✅ MockX: Generated {len(dataset)} tweets, {len(users_index)} users, {len(trending)} trending")


# ==================== API Endpoints ====================

@app.get("/")
async def root():
    """Serve frontend."""
    frontend_path = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path)
    return {"message": "MockX API running", "version": "1.0.0"}


@app.get("/api/v2/status")
async def get_status():
    """Get platform status (X API v2 style)."""
    return {
        "status": "online",
        "total_tweets": len(dataset),
        "total_users": len(users_index),
        "trending_count": len(trending)
    }


@app.get("/api/v2/tweets")
async def get_tweets(
    limit: int = 20,
    offset: int = 0,
    sort: str = "latest"
):
    """Get tweets timeline (X API v2 style)."""
    sorted_data = sorted(dataset, key=lambda x: x["created_at"], reverse=(sort == "latest"))
    tweets = sorted_data[offset:offset + limit]
    
    return {
        "data": tweets,
        "meta": {
            "result_count": len(tweets),
            "total_count": len(dataset),
            "next_offset": offset + limit if offset + limit < len(dataset) else None
        }
    }


@app.get("/api/v2/tweets/search")
async def search_tweets(
    query: str,
    start_time: str = None,
    end_time: str = None,
    limit: int = 100
):
    """Search tweets (X API v2 style)."""
    results = []
    
    for tweet in dataset:
        if query.lower() in tweet.get("text", "").lower():
            # Time filter
            if start_time:
                tweet_time = tweet.get("created_at", "")
                if tweet_time < start_time:
                    continue
            if end_time:
                tweet_time = tweet.get("created_at", "")
                if tweet_time > end_time:
                    continue
            
            results.append(tweet)
            if len(results) >= limit:
                break
    
    return {
        "data": results,
        "meta": {
            "result_count": len(results)
        }
    }


@app.get("/api/v2/tweets/{tweet_id}")
async def get_tweet(tweet_id: str):
    """Get single tweet by ID (X API v2 style)."""
    tweet = next((t for t in dataset if t["id"] == tweet_id), None)
    if not tweet:
        raise HTTPException(status_code=404, detail="Tweet not found")
    
    # Get replies
    conv_id = tweet.get("conversation_id")
    replies = [
        t for t in dataset 
        if t.get("conversation_id") == conv_id and t["id"] != tweet_id
    ][:20]
    
    return {
        "data": tweet,
        "includes": {
            "replies": replies,
            "users": [users_index.get(tweet.get("author_id"))]
        }
    }


@app.get("/api/v2/users/{user_id}")
async def get_user(user_id: str):
    """Get user profile (X API v2 style)."""
    user = users_index.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user's tweets
    user_tweets = [t for t in dataset if t.get("author_id") == user_id][:10]
    
    return {
        "data": user,
        "includes": {
            "tweets": user_tweets
        }
    }


@app.get("/api/v2/trends")
async def get_trends():
    """Get trending topics (X API v2 style)."""
    return {
        "data": trending,
        "meta": {
            "result_count": len(trending)
        }
    }


@app.get("/api/v2/volume")
async def get_tweet_volume():
    """Get tweet volume by hour."""
    return {
        "data": get_volume_by_hour(dataset)
    }


@app.post("/api/v2/reports")
async def report_tweet(report: ReportRequest):
    """Report a tweet (sends to Sarmad)."""
    tweet = next((t for t in dataset if t["id"] == report.tweet_id), None)
    if not tweet:
        raise HTTPException(status_code=404, detail="Tweet not found")
    
    return {
        "status": "reported",
        "tweet_id": report.tweet_id,
        "message": "تم استلام البلاغ وسيتم مراجعته",
        "redirect_url": f"http://localhost:8000/static/index.html?tweet={report.tweet_id}"
    }


@app.get("/api/v2/data/export")
async def export_data():
    """Export all data for Sarmad analysis."""
    return {
        "data": dataset,
        "users": list(users_index.values()),
        "trends": trending,
        "volume": get_volume_by_hour(dataset),
        "meta": {
            "exported_at": datetime.now().isoformat(),
            "total_tweets": len(dataset)
        }
    }


# Mount static files
static_dir = os.path.dirname(__file__)
pages_dir = os.path.join(static_dir, "pages")

if os.path.exists(pages_dir):
    app.mount("/pages", StaticFiles(directory=pages_dir, html=True), name="pages")

if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)

