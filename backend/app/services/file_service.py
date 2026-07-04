from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from app.core.config import settings


def save_upload(file: UploadFile, user_id: int) -> str:
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must have a filename",
        )

    storage_root = Path(settings.file_storage_path)
    user_dir = storage_root / str(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)

    original_name = Path(file.filename).name
    file_name = f"{uuid4().hex}_{original_name}"
    destination = user_dir / file_name

    with destination.open("wb") as output:
        while chunk := file.file.read(1024 * 1024):
            output.write(chunk)

    return str(destination)


def delete_file(file_url: str) -> None:
    path = Path(file_url)
    try:
        path.unlink(missing_ok=True)
    except OSError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not delete stored file",
        ) from exc
