"""
Session Service - Manages user sessions and ChromaDB collections
Handles session-based vector store isolation
"""
import logging
import uuid
from typing import Optional, Dict, List
from datetime import datetime, timedelta

from config import config

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)


class SessionService:
    """Manages session state and collection lifecycle"""

    def __init__(self):
        self.sessions: Dict[str, dict] = {}
        self.timeout_minutes = config.SESSION_TIMEOUT_MINUTES

    def create_session(self) -> str:
        """Create new session and return session ID"""
        session_id = str(uuid.uuid4())
        collection_name = f"session_{session_id.replace('-', '_')}"

        self.sessions[session_id] = {
            "session_id": session_id,
            "collection_name": collection_name,
            "created_at": datetime.now(),
            "last_activity": datetime.now(),
            "document_count": 0,
            "query_count": 0,
            "uploaded_files": [],
        }

        logger.info(f"Session created: {session_id}")
        return session_id

    def get_session(self, session_id: str) -> Optional[dict]:
        """Get session data"""
        if session_id not in self.sessions:
            return None

        # Update last activity
        self.sessions[session_id]["last_activity"] = datetime.now()
        return self.sessions[session_id]

    def update_session(self, session_id: str, **kwargs):
        """Update session metadata"""
        if session_id in self.sessions:
            self.sessions[session_id].update(kwargs)
            self.sessions[session_id]["last_activity"] = datetime.now()

    def add_file_to_session(self, session_id: str, filename: str, doc_count: int):
        """Record uploaded file in session"""
        if session_id in self.sessions:
            self.sessions[session_id]["uploaded_files"].append({
                "filename": filename,
                "uploaded_at": datetime.now().isoformat(),
                "document_count": doc_count,
            })
            self.sessions[session_id]["document_count"] += doc_count
            logger.info(f"File added to session {session_id}: {filename} ({doc_count} chunks)")

    def increment_query_count(self, session_id: str):
        """Track query usage"""
        if session_id in self.sessions:
            self.sessions[session_id]["query_count"] += 1
            self.sessions[session_id]["last_activity"] = datetime.now()

    def is_session_expired(self, session_id: str) -> bool:
        """Check if session has expired"""
        if session_id not in self.sessions:
            return True

        last_activity = self.sessions[session_id]["last_activity"]
        timeout = timedelta(minutes=self.timeout_minutes)

        return datetime.now() - last_activity > timeout

    def cleanup_expired_sessions(self) -> List[str]:
        """Remove expired sessions"""
        expired = [
            sid for sid in self.sessions
            if self.is_session_expired(sid)
        ]

        for sid in expired:
            logger.info(f"Removing expired session: {sid}")
            del self.sessions[sid]

        return expired

    def get_collection_name(self, session_id: str) -> Optional[str]:
        """Get ChromaDB collection name for session"""
        session = self.get_session(session_id)
        return session["collection_name"] if session else None

    def get_session_stats(self, session_id: str) -> Optional[dict]:
        """Get session statistics"""
        session = self.get_session(session_id)
        if not session:
            return None

        return {
            "session_id": session_id,
            "created_at": session["created_at"].isoformat(),
            "last_activity": session["last_activity"].isoformat(),
            "document_count": session["document_count"],
            "query_count": session["query_count"],
            "files_uploaded": len(session["uploaded_files"]),
            "active": not self.is_session_expired(session_id),
        }

    def delete_session(self, session_id: str) -> bool:
        """Manually delete a session"""
        if session_id in self.sessions:
            logger.info(f"Session deleted: {session_id}")
            del self.sessions[session_id]
            return True
        return False
