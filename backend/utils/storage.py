import io
import logging
import uuid
from typing import Optional

from google.cloud import storage

from core.config import get_settings

logger = logging.getLogger("raptorflow.utils.storage")


async def upload_image_to_gcs(
    image_data: bytes,
    content_type: str = "image/png",
    bucket_name: Optional[str] = None,
) -> str:
    """
    Surgically uploads image data to Google Cloud Storage and returns the public URL.
    """
    settings = get_settings()
    bucket_name = bucket_name or settings.GCS_MUSE_CREATIVES_BUCKET

    try:
        client = storage.Client(project=settings.GCP_PROJECT_ID)
        bucket = client.bucket(bucket_name)

        # Generate a unique filename
        filename = f"muse_{uuid.uuid4()}.png"
        blob = bucket.blob(filename)

        blob.upload_from_string(image_data, content_type=content_type)

        # Return the public URL (assuming public access or signed URL is handled elsewhere)
        # For now, we'll return a GCS URI or a standard storage URL
        url = f"https://storage.googleapis.com/{bucket_name}/{filename}"
        logger.info(f"Uploaded image to {url}")
        return url
    except ConnectionError as e:
        from core.enhanced_exceptions import handle_external_service_error

        logger.error(f"GCS connection failed: {str(e)}")
        handle_external_service_error(
            f"Failed to connect to Google Cloud Storage",
            service="gcs_storage",
            original_error=str(e),
        )
        # Fallback for local development or if GCS fails: return placeholder or local path
        return f"local://{filename}"
    except PermissionError as e:
        from core.enhanced_exceptions import handle_authorization_error

        logger.error(f"GCS permission denied: {str(e)}")
        handle_authorization_error(
            f"Insufficient permissions for Google Cloud Storage",
            resource="gcs_bucket",
            original_error=str(e),
        )
        return f"local://{filename}"
    except TimeoutError as e:
        from core.enhanced_exceptions import handle_timeout_error

        logger.error(f"GCS upload timeout: {str(e)}")
        handle_timeout_error(
            f"Upload to Google Cloud Storage timed out",
            timeout_seconds=30.0,
            original_error=str(e),
        )
        return f"local://{filename}"
    except Exception as e:
        from core.enhanced_exceptions import handle_system_error

        logger.error(f"Unexpected GCS error: {str(e)}")
        handle_system_error(
            f"Unexpected error during GCS upload",
            component="storage_upload",
            original_error=str(e),
        )
        # Fallback for local development or if GCS fails: return placeholder or local path
        return f"local://{filename}"


def pil_to_bytes(image) -> bytes:
    """Converts a PIL Image object to bytes."""
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format="PNG")
    return img_byte_arr.getvalue()
