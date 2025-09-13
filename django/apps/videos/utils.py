import logging
import os
import uuid

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from django.conf import settings

logger = logging.getLogger(__name__)


class S3Service:
    """
    Service class for handling S3 operations.
    """

    def __init__(self):
        """Initialize S3 client."""
        try:
            self.s3_client = boto3.client(
                "s3",
                aws_access_key_id=getattr(settings, "AWS_ACCESS_KEY_ID", None),
                aws_secret_access_key=getattr(settings, "AWS_SECRET_ACCESS_KEY", None),
                region_name=getattr(settings, "AWS_S3_REGION_NAME", "us-east-1"),
            )
            self.bucket_name = getattr(
                settings, "AWS_S3_BUCKET_NAME", "your-bucket-name"
            )
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {str(e)}")
            self.s3_client = None

    def upload_file(self, file_obj, file_key=None, content_type=None):
        """
        Upload a file to S3.

        Args:
            file_obj: File object to upload
            file_key: S3 key for the file (optional, will generate if not provided)
            content_type: Content type of the file (optional)

        Returns:
            dict: Contains 'url', 'bucket', 'key', 'success'
        """
        if not self.s3_client:
            return {"success": False, "error": "S3 client not initialized"}

        try:
            # Generate file key if not provided
            if not file_key:
                file_extension = os.path.splitext(file_obj.name)[1]
                file_key = f"videos/{uuid.uuid4()}{file_extension}"

            # Prepare upload parameters
            upload_params = {
                "Bucket": self.bucket_name,
                "Key": file_key,
                "Body": file_obj,
                "ACL": "private",  # or 'public-read' if you want public access
            }

            # Add content type if provided
            if content_type:
                upload_params["ContentType"] = content_type

            # Upload file
            self.s3_client.upload_fileobj(**upload_params)

            # Generate URL
            file_url = f"https://{self.bucket_name}.s3.amazonaws.com/{file_key}"

            return {
                "success": True,
                "url": file_url,
                "bucket": self.bucket_name,
                "key": file_key,
            }

        except NoCredentialsError:
            logger.error("AWS credentials not found")
            return {"success": False, "error": "AWS credentials not found"}
        except ClientError as e:
            logger.error(f"S3 upload failed: {str(e)}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Unexpected error during S3 upload: {str(e)}")
            return {"success": False, "error": str(e)}

    def delete_file(self, file_key, bucket_name=None):
        """
        Delete a file from S3.

        Args:
            file_key: S3 key of the file to delete
            bucket_name: S3 bucket name (optional, uses default if not provided)

        Returns:
            dict: Contains 'success' and optional 'error'
        """
        if not self.s3_client:
            return {"success": False, "error": "S3 client not initialized"}

        try:
            bucket = bucket_name or self.bucket_name

            self.s3_client.delete_object(Bucket=bucket, Key=file_key)

            return {"success": True}

        except ClientError as e:
            logger.error(f"S3 delete failed: {str(e)}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Unexpected error during S3 delete: {str(e)}")
            return {"success": False, "error": str(e)}

    def generate_presigned_url(self, file_key, expiration=3600, operation="get_object"):
        """
        Generate a presigned URL for S3 operations.

        Args:
            file_key: S3 key of the file
            expiration: URL expiration time in seconds (default: 1 hour)
            operation: S3 operation ('get_object', 'put_object', etc.)

        Returns:
            dict: Contains 'url' and 'success'
        """
        if not self.s3_client:
            return {"success": False, "error": "S3 client not initialized"}

        try:
            url = self.s3_client.generate_presigned_url(
                operation,
                Params={"Bucket": self.bucket_name, "Key": file_key},
                ExpiresIn=expiration,
            )

            return {"success": True, "url": url}

        except ClientError as e:
            logger.error(f"Failed to generate presigned URL: {str(e)}")
            return {"success": False, "error": str(e)}

    def file_exists(self, file_key, bucket_name=None):
        """
        Check if a file exists in S3.

        Args:
            file_key: S3 key of the file
            bucket_name: S3 bucket name (optional, uses default if not provided)

        Returns:
            bool: True if file exists, False otherwise
        """
        if not self.s3_client:
            return False

        try:
            bucket = bucket_name or self.bucket_name

            self.s3_client.head_object(Bucket=bucket, Key=file_key)

            return True

        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            else:
                logger.error(f"Error checking file existence: {str(e)}")
                return False
        except Exception as e:
            logger.error(f"Unexpected error checking file existence: {str(e)}")
            return False


def get_s3_service():
    """
    Get an instance of S3Service.

    Returns:
        S3Service: S3 service instance
    """
    return S3Service()


def upload_video_to_s3(video_file, video_id=None):
    """
    Upload a video file to S3.

    Args:
        video_file: Video file object
        video_id: Video ID for generating unique key (optional)

    Returns:
        dict: Upload result
    """
    s3_service = get_s3_service()

    # Generate file key
    file_extension = os.path.splitext(video_file.name)[1]
    if video_id:
        file_key = f"videos/{video_id}{file_extension}"
    else:
        file_key = f"videos/{uuid.uuid4()}{file_extension}"

    # Determine content type
    content_type = "video/mp4"  # Default
    if file_extension.lower() in [".avi"]:
        content_type = "video/x-msvideo"
    elif file_extension.lower() in [".mov"]:
        content_type = "video/quicktime"
    elif file_extension.lower() in [".mkv"]:
        content_type = "video/x-matroska"
    elif file_extension.lower() in [".wmv"]:
        content_type = "video/x-ms-wmv"
    elif file_extension.lower() in [".flv"]:
        content_type = "video/x-flv"
    elif file_extension.lower() in [".webm"]:
        content_type = "video/webm"

    return s3_service.upload_file(video_file, file_key, content_type)


def delete_video_from_s3(bucket_name, file_key):
    """
    Delete a video file from S3.

    Args:
        bucket_name: S3 bucket name
        file_key: S3 key of the file

    Returns:
        dict: Delete result
    """
    s3_service = get_s3_service()
    return s3_service.delete_file(file_key, bucket_name)


def generate_video_stream_url(file_key, expiration=3600):
    """
    Generate a presigned URL for video streaming.

    Args:
        file_key: S3 key of the video file
        expiration: URL expiration time in seconds

    Returns:
        dict: URL generation result
    """
    s3_service = get_s3_service()
    return s3_service.generate_presigned_url(file_key, expiration, "get_object")
