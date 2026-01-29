from datetime import datetime, timedelta

from db import get_db

from .core.supabase_mgr import get_supabase_client


async def delete_expired_originals():
    """
    Daily job to delete expired onboarding files
    """
    db = get_db()
    supabase = get_supabase_client()

    # Get files past retention date
    expired_files = await db.execute(
        """
        SELECT id, original_path
        FROM onboarding_files
        WHERE retention_date < NOW()
        AND status = 'processed'
        """
    )

    # Delete from storage and update DB
    for file in expired_files:
        try:
            await supabase.storage.remove(file["original_path"])
            await db.execute(
                "UPDATE onboarding_files SET status = 'deleted' WHERE id = %s",
                (file["id"],),
            )
        except Exception as e:
            print(f"Failed to delete {file['original_path']}: {str(e)}")
