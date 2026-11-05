from pathlib import Path, PurePath
from uuid import uuid4

import aiofiles
from fastapi import UploadFile

from app.exceptions.custom_exceptions import (
    ImageStorageError,
    InvalidImageError,
)

UPLOAD_DIRECTORY = Path("uploads")
MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024
ALLOWED_IMAGE_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
}
CHUNK_SIZE = 1024 * 1024


def validate_image(upload_file: UploadFile) -> tuple[str, str]:
    """Validate image against the application's requirements.

        Raise or report an error when the value is not acceptable.
    """
    filename = upload_file.filename
    if not filename or filename != PurePath(filename).name:
        raise InvalidImageError("Invalid image filename")

    extension = Path(filename).suffix.casefold()
    content_type = (upload_file.content_type or "").casefold()
    if (
        extension not in ALLOWED_IMAGE_TYPES
        or content_type != ALLOWED_IMAGE_TYPES[extension]
    ):
        raise InvalidImageError("Only JPEG and PNG images are supported")
    return filename, content_type


async def save_image(upload_file: UploadFile) -> tuple[str, int]:
    """Validate and store an uploaded image file.

        The saved location is used when creating the ticket image record.
    """
    filename, _ = validate_image(upload_file)
    UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)
    file_path = UPLOAD_DIRECTORY / f"{uuid4().hex}{Path(filename).suffix.casefold()}"
    relative_path = file_path.as_posix()
    size_bytes = 0

    try:
        async with aiofiles.open(file_path, "wb") as output:
            while chunk := await upload_file.read(CHUNK_SIZE):
                size_bytes += len(chunk)
                if size_bytes > MAX_IMAGE_SIZE_BYTES:
                    raise InvalidImageError("Image exceeds the maximum size")
                await output.write(chunk)
    except InvalidImageError:
        await delete_image(relative_path)
        raise
    except OSError as exc:
        await delete_image(relative_path)
        raise ImageStorageError from exc

    return relative_path, size_bytes


async def delete_image(file_path: str) -> None:
    """Delete or remove image from the application.

        Related access and persistence rules are handled by this operation.
    """
    path = Path(file_path).resolve()
    upload_root = UPLOAD_DIRECTORY.resolve()
    if upload_root not in path.parents:
        raise InvalidImageError("Invalid image path")
    try:
        path.unlink(missing_ok=True)
    except OSError as exc:
        raise ImageStorageError from exc
