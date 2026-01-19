"""
Audit Log Service

Tracks key actions in the application for audit purposes.
Logs user actions like login, file uploads, and report generation.
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# In-memory storage for audit logs
# Format: List of dictionaries with id, user_id, action, details, created_at
_audit_logs: List[Dict] = []
_log_id_counter: int = 0

def log_action(user_id: str, action: str, details: Optional[str] = None) -> Dict:
    """
    Log an action to the audit log.
    
    Args:
        user_id: The ID/username of the user performing the action
        action: The action being performed (e.g., "user_login", "file_upload", "report_generation")
        details: Optional additional details about the action
        
    Returns:
        Dictionary representing the created audit log entry:
        {
            'id': int,
            'user_id': str,
            'action': str,
            'details': str or None,
            'created_at': str (ISO format)
        }
    """
    global _log_id_counter
    
    _log_id_counter += 1
    
    log_entry = {
        'id': _log_id_counter,
        'user_id': user_id,
        'action': action,
        'details': details,
        'created_at': datetime.now().isoformat()
    }
    
    _audit_logs.append(log_entry)
    
    # Keep only last 1000 entries to prevent memory issues
    if len(_audit_logs) > 1000:
        _audit_logs.pop(0)
    
    logging.info(f"Audit log: {user_id} - {action}" + (f" - {details}" if details else ""))
    
    return log_entry

def get_user_activity(user_id: str, limit: int = 5) -> List[Dict]:
    """
    Get recent activity for a specific user.
    
    Args:
        user_id: The ID/username of the user
        limit: Maximum number of entries to return (default: 5)
        
    Returns:
        List of audit log entries for the user, sorted by most recent first
    """
    user_logs = [log for log in _audit_logs if log['user_id'] == user_id]
    # Sort by created_at descending (most recent first)
    user_logs.sort(key=lambda x: x['created_at'], reverse=True)
    return user_logs[:limit]

def get_all_activity(limit: int = 100) -> List[Dict]:
    """
    Get all recent activity (for admin purposes, if needed later).
    
    Args:
        limit: Maximum number of entries to return (default: 100)
        
    Returns:
        List of audit log entries, sorted by most recent first
    """
    logs = sorted(_audit_logs, key=lambda x: x['created_at'], reverse=True)
    return logs[:limit]
