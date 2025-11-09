"""
Document Service - Handles file upload, validation, and processing
Production-grade file handling with security and error management
"""
import logging
import re
import hashlib
import tempfile
from pathlib import Path
from typing import Optional, List, Tuple
from datetime import datetime
import shutil

from config import config

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)


class DocumentService:
    """Handles document upload, validation, and storage"""

    def __init__(self):
        self.upload_dir = config.UPLOAD_DIR
        self.max_size_bytes = config.MAX_FILE_SIZE_MB * 1024 * 1024
        self.allowed_extensions = config.ALLOWED_EXTENSIONS

    def validate_file(self, file_data, filename: str) -> Tuple[bool, Optional[str]]:
        """
        Validate uploaded file

        Returns:
            (is_valid, error_message)
        """
        # Check filename
        if not filename:
            return False, "Filename is empty"

        # Check extension
        file_ext = Path(filename).suffix.lower()
        if file_ext not in self.allowed_extensions:
            return False, f"File type {file_ext} not allowed. Allowed: {', '.join(self.allowed_extensions)}"

        # Check file size
        try:
            file_size = len(file_data.getvalue()) if hasattr(file_data, 'getvalue') else file_data.size
            if file_size == 0:
                return False, "File is empty"

            if file_size > self.max_size_bytes:
                max_mb = self.max_size_bytes / (1024 * 1024)
                actual_mb = file_size / (1024 * 1024)
                return False, f"File too large ({actual_mb:.1f}MB). Maximum: {max_mb:.0f}MB"
        except Exception as e:
            logger.error(f"Error checking file size: {e}")
            return False, "Unable to determine file size"

        # Check for suspicious content (basic security)
        if config.SANITIZE_FILENAMES:
            if self._is_suspicious_filename(filename):
                return False, "Filename contains suspicious characters"

        return True, None

    def _is_suspicious_filename(self, filename: str) -> bool:
        """Check for path traversal and other suspicious patterns"""
        suspicious_patterns = [
            r"\.\.",  # Path traversal
            r"[<>:\"|?*]",  # Invalid Windows chars
            r"^\.",  # Hidden files
            r"\.exe$|\.bat$|\.cmd$|\.sh$",  # Executables
        ]

        for pattern in suspicious_patterns:
            if re.search(pattern, filename, re.IGNORECASE):
                return True
        return False

    def sanitize_filename(self, filename: str) -> str:
        """Create safe filename"""
        # Remove path components
        filename = Path(filename).name

        # Remove special characters, keep alphanumeric, dots, dashes, underscores
        filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)

        # Limit length
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        if len(name) > 100:
            name = name[:100]

        return f"{name}.{ext}" if ext else name

    def save_uploaded_file(
        self,
        file_data,
        original_filename: str,
        session_id: str
    ) -> Tuple[Optional[Path], Optional[str]]:
        """
        Save uploaded file to temporary storage

        Args:
            file_data: File-like object from Streamlit
            original_filename: Original name of uploaded file
            session_id: Unique session identifier

        Returns:
            (file_path, error_message)
        """
        try:
            # Validate first
            is_valid, error = self.validate_file(file_data, original_filename)
            if not is_valid:
                logger.warning(f"File validation failed: {error}")
                return None, error

            # Create session directory
            session_dir = self.upload_dir / session_id
            session_dir.mkdir(parents=True, exist_ok=True)

            # Generate safe filename
            safe_filename = self.sanitize_filename(original_filename)

            # Add timestamp and hash to prevent collisions
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_hash = hashlib.md5(safe_filename.encode()).hexdigest()[:8]
            final_filename = f"{timestamp}_{file_hash}_{safe_filename}"

            file_path = session_dir / final_filename

            # Save file
            file_data.seek(0)  # Reset file pointer
            with open(file_path, "wb") as f:
                f.write(file_data.read())

            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            logger.info(f"File saved: {final_filename} ({file_size_mb:.2f}MB)")

            return file_path, None

        except Exception as e:
            error_msg = f"Error saving file: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return None, error_msg

    def cleanup_session_files(self, session_id: str) -> bool:
        """Delete all files for a session"""
        try:
            session_dir = self.upload_dir / session_id
            if session_dir.exists():
                shutil.rmtree(session_dir)
                logger.info(f"Cleaned up session directory: {session_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error cleaning up session {session_id}: {e}")
            return False

    def get_session_files(self, session_id: str) -> List[Path]:
        """Get all files for a session"""
        session_dir = self.upload_dir / session_id
        if not session_dir.exists():
            return []
        return list(session_dir.glob("*"))

    def get_file_metadata(self, file_path: Path) -> dict:
        """Extract metadata from saved file"""
        if not file_path.exists():
            return {}

        stat = file_path.stat()
        return {
            "filename": file_path.name,
            "size_bytes": stat.st_size,
            "size_mb": stat.st_size / (1024 * 1024),
            "uploaded_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "extension": file_path.suffix,
        }
