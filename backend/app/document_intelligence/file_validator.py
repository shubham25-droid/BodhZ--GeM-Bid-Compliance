import os
import hashlib
from typing import Tuple, Dict, Any

ALLOWED_EXTENSIONS = {
    ".pdf", ".docx", ".doc", ".xlsx", ".xls", ".csv",
    ".png", ".jpg", ".jpeg", ".txt", ".zip", ".rar"
}

MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50MB cap


class FileValidationError(Exception):
    """Custom exception raised when a file fails security or format validation."""
    pass


def compute_sha256(file_bytes: bytes) -> str:
    """Computes SHA-256 hash of raw file bytes for audit log integrity."""
    return hashlib.sha256(file_bytes).hexdigest()


class FileValidator:
    """
    Validates uploaded document files across all file extensions (.pdf, .docx, .xlsx, .jpg, .png, .txt, etc.).
    Computes SHA-256 hash, validates file size (max 50MB), and returns metadata dictionary.
    """
    @staticmethod
    def validate_file(file_bytes: bytes, filename: str) -> Dict[str, Any]:
        if not file_bytes:
            raise FileValidationError("Uploaded file is empty (0 bytes).")

        file_size = len(file_bytes)
        if file_size > MAX_FILE_SIZE_BYTES:
            raise FileValidationError(f"File size ({file_size / (1024*1024):.2f}MB) exceeds 50MB limit.")

        ext = os.path.splitext(filename)[1].lower()
        
        mime_type = "application/octet-stream"
        if ext == ".pdf":
            mime_type = "application/pdf"
        elif ext in [".docx", ".doc"]:
            mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif ext in [".png", ".jpg", ".jpeg"]:
            mime_type = "image/" + ext.replace(".", "")
        elif ext in [".xlsx", ".xls", ".csv"]:
            mime_type = "text/csv" if ext == ".csv" else "application/vnd.ms-excel"
        elif ext == ".txt":
            mime_type = "text/plain"

        sha256_hash = compute_sha256(file_bytes)

        return {
            "filename": filename,
            "extension": ext or ".bin",
            "mime_type": mime_type,
            "size_bytes": file_size,
            "sha256_hash": sha256_hash,
            "is_valid": True
        }

    @classmethod
    def validate_file_content(cls, file_bytes: bytes, filename: str) -> str:
        meta = cls.validate_file(file_bytes, filename)
        if meta["mime_type"] == "application/pdf":
            return "APPLICATION_PDF"
        elif meta["mime_type"].startswith("image/"):
            return "IMAGE"
        return "TEXT"

    @classmethod
    def calculate_sha256(cls, file_bytes: bytes) -> str:
        return compute_sha256(file_bytes)

    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        return os.path.basename(filename).replace(" ", "_").replace("..", "")


def validate_file(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    return FileValidator.validate_file(file_bytes, filename)
