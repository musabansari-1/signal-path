import re
import uuid
from io import BytesIO
from pathlib import Path

from docx import Document
from fastapi import HTTPException, UploadFile, status
from pypdf import PdfReader

from app.core.config import settings

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
    "text/markdown",
    "application/octet-stream",
}


def safe_filename(filename: str) -> str:
    base = Path(filename).name
    clean = re.sub(r"[^A-Za-z0-9._ -]", "_", base).strip(" .")
    return clean[:180] or "career-asset"


def read_validated_upload(upload: UploadFile) -> tuple[bytes, str, str]:
    name = safe_filename(upload.filename or "career-asset")
    extension = Path(name).suffix.lower()
    mime_type = (upload.content_type or "application/octet-stream").lower()
    if extension not in ALLOWED_EXTENSIONS or mime_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Upload a PDF, DOCX, TXT, or Markdown file",
        )
    data = upload.file.read(settings.max_upload_bytes + 1)
    if not data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The file is empty")
    if len(data) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Files must be smaller than {settings.max_upload_bytes // (1024 * 1024)} MB",
        )
    return data, name, mime_type


def extract_text(data: bytes, filename: str) -> str:
    extension = Path(filename).suffix.lower()
    try:
        if extension == ".pdf":
            text = "\n".join(page.extract_text() or "" for page in PdfReader(BytesIO(data)).pages)
        elif extension == ".docx":
            document = Document(BytesIO(data))
            text = "\n".join(paragraph.text for paragraph in document.paragraphs)
        else:
            text = data.decode("utf-8-sig")
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="We could not read this file. Check that it is not encrypted or corrupted.",
        ) from exc
    text = text.replace("\x00", "").strip()
    if not text:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No readable text was found in this file",
        )
    return text[:500_000]


def persist_upload(data: bytes, user_id: uuid.UUID, filename: str) -> str:
    root = Path(settings.local_upload_dir).resolve()
    user_dir = (root / str(user_id)).resolve()
    user_dir.mkdir(parents=True, exist_ok=True)
    stored_name = f"{uuid.uuid4().hex}{Path(filename).suffix.lower()}"
    destination = (user_dir / stored_name).resolve()
    if root not in destination.parents:
        raise RuntimeError("Invalid upload path")
    destination.write_bytes(data)
    return str(destination)


def remove_upload(file_path: str | None) -> None:
    if not file_path:
        return
    root = Path(settings.local_upload_dir).resolve()
    candidate = Path(file_path).resolve()
    if root in candidate.parents and candidate.is_file():
        candidate.unlink()

