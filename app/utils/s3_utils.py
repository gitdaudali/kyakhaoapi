import mimetypes
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

import boto3
from botocore.exceptions import ClientError
from fastapi import HTTPException, UploadFile, status

from app.core.config import settings


def get_s3_client():
    """Create and return an S3 client with the configured credentials."""
    return boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    )


def generate_s3_key(filename: str, folder: str = "avatars") -> Tuple[str, str]:
    """
    Generate a unique S3 key for the file.

    Args:
        filename: Original filename
        folder: Folder in the bucket to store the file

    Returns:
        Tuple of (file_key, content_type)
    """
    # Get file extension
    ext = Path(filename).suffix.lower()
    # Generate a unique filename
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    unique_filename = f"{timestamp}_{os.urandom(4).hex()}{ext}"

    # Generate S3 key
    file_key = f"{folder}/{unique_filename}"

    # Guess content type from extension
    content_type, _ = mimetypes.guess_type(filename)
    content_type = content_type or "application/octet-stream"

    return file_key, content_type


async def upload_file_to_s3(
    file: UploadFile,
    folder: str = "avatars",
    allowed_extensions: Optional[list] = None,
    max_size_mb: int = 5,
) -> str:
    """
    Upload a file to S3 and return the public URL.

    Args:
        file: FastAPI UploadFile object
        folder: Folder in the bucket to store the file
        allowed_extensions: List of allowed file extensions (e.g., ['.jpg', '.png'])
        max_size_mb: Maximum file size in MB

    Returns:
        Public URL of the uploaded file

    Raises:
        HTTPException: If file validation fails or upload fails
    """
    if allowed_extensions is None:
        allowed_extensions = settings.AVATAR_ALLOWED_FILE_TYPES

    max_size = max_size_mb * 1024 * 1024

    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max size is {max_size_mb}MB",
        )

    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {', '.join(allowed_extensions)}",
        )

    s3_client = get_s3_client()

    try:
        file_key, content_type = generate_s3_key(file.filename, folder)

        s3_client.upload_fileobj(
            file.file,
            settings.S3_BUCKET,
            file_key,
            ExtraArgs={"ContentType": content_type},
        )

        if settings.S3_CUSTOM_DOMAIN:
            # Cloudfront URL
            url = f"https://{settings.S3_CUSTOM_DOMAIN}/{file_key}"
        else:
            # Standard S3 URL
            url = f"https://{settings.S3_BUCKET}.s3.{settings.AWS_REGION}.amazonaws.com/{file_key}"

        return url

    except ClientError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading file to S3: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}",
        )


def delete_file_from_s3(file_url: str) -> bool:
    """
    Delete a file from S3 using its URL.

    Args:
        file_url: Public URL of the file to delete

    Returns:
        bool: True if deletion was successful, False otherwise
    """
    try:
        s3_client = get_s3_client()

        if settings.S3_CUSTOM_DOMAIN and settings.S3_CUSTOM_DOMAIN in file_url:
            key = file_url.split(f"{settings.S3_CUSTOM_DOMAIN}/", 1)[1]
        else:
            key = file_url.split(f"{settings.S3_BUCKET}", 1)[1].lstrip("/")

        s3_client.delete_object(Bucket=settings.S3_BUCKET, Key=key)
        return True
    except Exception as e:
        return False
