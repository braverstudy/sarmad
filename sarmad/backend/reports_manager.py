"""
Reports Manager - إدارة البلاغات
Handles storage and retrieval of violation reports using JSON file storage.
"""

import json
import os
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class ReportStatus(str, Enum):
    PENDING = "pending"          # قيد الانتظار
    ACTIVE = "active"            # نشط (قيد التحليل)
    RESOLVED = "resolved"        # تم الضبط
    CANCELLED = "cancelled"      # ملغي


class CancelReason(str, Enum):
    NOT_VIOLATION = "not_violation"   # محتوى غير مخالف
    DELETED = "deleted"               # تم حذفه
    NOT_FOUND = "not_found"           # غير موجود


class ReportSource(str, Enum):
    PUBLIC = "public"            # بلاغ من العامة
    AUTO_MONITOR = "auto_monitor"  # بلاغ من الراصد الآلي


@dataclass
class Report:
    """نموذج البلاغ"""
    id: str
    tweet_url: str
    tweet_id: str
    description: str
    status: str
    source: str
    reporter_name: str
    reporter_phone: str
    reporter_id: Optional[str]
    created_at: str
    updated_at: str
    resolved_at: Optional[str]
    cancel_reason: Optional[str]
    source_tweet_id: Optional[str]
    analysis_result: Optional[Dict[str, Any]]
    
    @classmethod
    def create(cls, tweet_url: str, description: str, reporter_name: str, 
               reporter_phone: str, reporter_id: str = None, 
               source: str = ReportSource.PUBLIC.value):
        """Create a new report"""
        now = datetime.now().isoformat()
        # Extract tweet ID from URL
        tweet_id = extract_tweet_id(tweet_url)
        
        return cls(
            id=str(uuid.uuid4())[:8].upper(),
            tweet_url=tweet_url,
            tweet_id=tweet_id or "",
            description=description,
            status=ReportStatus.PENDING.value,
            source=source,
            reporter_name=reporter_name,
            reporter_phone=reporter_phone,
            reporter_id=reporter_id,
            created_at=now,
            updated_at=now,
            resolved_at=None,
            cancel_reason=None,
            source_tweet_id=None,
            analysis_result=None
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Report':
        return cls(**data)


def extract_tweet_id(url: str) -> Optional[str]:
    """Extract tweet ID from X/Twitter URL"""
    import re
    # Patterns: x.com/user/status/123, twitter.com/user/status/123
    pattern = r'(?:x\.com|twitter\.com)/\w+/status/(\d+)'
    match = re.search(pattern, url)
    return match.group(1) if match else None


class ReportsManager:
    """مدير البلاغات - JSON Storage"""
    
    def __init__(self, storage_path: str = None):
        if storage_path is None:
            storage_path = os.path.join(os.path.dirname(__file__), 'reports_data.json')
        self.storage_path = storage_path
        self._ensure_storage()
    
    def _ensure_storage(self):
        """Ensure storage file exists"""
        if not os.path.exists(self.storage_path):
            self._save_all([])
    
    def _load_all(self) -> List[Dict[str, Any]]:
        """Load all reports from JSON"""
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _save_all(self, reports: List[Dict[str, Any]]):
        """Save all reports to JSON"""
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(reports, f, ensure_ascii=False, indent=2)
    
    def create_report(self, tweet_url: str, description: str, 
                     reporter_name: str, reporter_phone: str,
                     reporter_id: str = None,
                     source: str = ReportSource.PUBLIC.value) -> Report:
        """Create and save a new report"""
        report = Report.create(
            tweet_url=tweet_url,
            description=description,
            reporter_name=reporter_name,
            reporter_phone=reporter_phone,
            reporter_id=reporter_id,
            source=source
        )
        
        reports = self._load_all()
        reports.append(report.to_dict())
        self._save_all(reports)
        
        return report
    
    def get_report(self, report_id: str) -> Optional[Report]:
        """Get a report by ID"""
        reports = self._load_all()
        for r in reports:
            if r['id'] == report_id:
                return Report.from_dict(r)
        return None
    
    def get_all_reports(self, status: str = None) -> List[Report]:
        """Get all reports, optionally filtered by status"""
        reports = self._load_all()
        if status:
            reports = [r for r in reports if r['status'] == status]
        return [Report.from_dict(r) for r in reports]
    
    def get_active_reports(self) -> List[Report]:
        """Get all active (under analysis) reports"""
        return self.get_all_reports(status=ReportStatus.ACTIVE.value)
    
    def get_pending_reports(self) -> List[Report]:
        """Get all pending reports"""
        return self.get_all_reports(status=ReportStatus.PENDING.value)
    
    def update_status(self, report_id: str, new_status: str, 
                      cancel_reason: str = None,
                      source_tweet_id: str = None,
                      analysis_result: Dict[str, Any] = None) -> Optional[Report]:
        """Update report status"""
        reports = self._load_all()
        updated = False
        
        for i, r in enumerate(reports):
            if r['id'] == report_id:
                r['status'] = new_status
                r['updated_at'] = datetime.now().isoformat()
                
                if new_status == ReportStatus.RESOLVED.value:
                    r['resolved_at'] = datetime.now().isoformat()
                    if source_tweet_id:
                        r['source_tweet_id'] = source_tweet_id
                
                if new_status == ReportStatus.CANCELLED.value and cancel_reason:
                    r['cancel_reason'] = cancel_reason
                
                if analysis_result:
                    r['analysis_result'] = analysis_result
                
                reports[i] = r
                updated = True
                break
        
        if updated:
            self._save_all(reports)
            return Report.from_dict(reports[i])
        return None
    
    def activate_report(self, report_id: str) -> Optional[Report]:
        """Activate a pending report for analysis"""
        return self.update_status(report_id, ReportStatus.ACTIVE.value)
    
    def resolve_report(self, report_id: str, source_tweet_id: str,
                       analysis_result: Dict[str, Any] = None) -> Optional[Report]:
        """Mark report as resolved with source found"""
        return self.update_status(
            report_id, 
            ReportStatus.RESOLVED.value,
            source_tweet_id=source_tweet_id,
            analysis_result=analysis_result
        )
    
    def cancel_report(self, report_id: str, reason: str) -> Optional[Report]:
        """Cancel a report with reason"""
        return self.update_status(
            report_id,
            ReportStatus.CANCELLED.value,
            cancel_reason=reason
        )
    
    def get_statistics(self) -> Dict[str, int]:
        """Get report statistics"""
        reports = self._load_all()
        stats = {
            'total': len(reports),
            'pending': 0,
            'active': 0,
            'resolved': 0,
            'cancelled': 0,
            'from_public': 0,
            'from_auto': 0
        }
        
        for r in reports:
            status = r.get('status', '')
            if status in stats:
                stats[status] += 1
            
            source = r.get('source', '')
            if source == ReportSource.PUBLIC.value:
                stats['from_public'] += 1
            elif source == ReportSource.AUTO_MONITOR.value:
                stats['from_auto'] += 1
        
        return stats


# Global instance
reports_manager = ReportsManager()


# Demo/Test
if __name__ == "__main__":
    manager = ReportsManager("test_reports.json")
    
    # Create a test report
    report = manager.create_report(
        tweet_url="https://x.com/testuser/status/1234567890",
        description="محتوى مخالف - تحريض",
        reporter_name="أحمد محمد",
        reporter_phone="0501234567"
    )
    
    print(f"Created report: {report.id}")
    print(f"Tweet ID: {report.tweet_id}")
    
    # Activate it
    manager.activate_report(report.id)
    
    # Get stats
    stats = manager.get_statistics()
    print(f"Stats: {stats}")
    
    # Clean up test file
    os.remove("test_reports.json")
