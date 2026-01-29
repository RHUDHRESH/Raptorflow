import os
import sys

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from .core.supabase_mgr import get_supabase_client
from .services.onboarding import process_uploaded_file


async def test_ocr_retention():
    """Test OCR file processing and retention"""
    supabase = get_supabase_client()

    # Simulate file upload
    test_file = {
        "filename": "test_ocr.pdf",
        "content_type": "application/pdf",
        "content": b"%PDF-1.4 sample content",
    }

    # Process file
    result = await process_uploaded_file(test_file)
    print(f"OCR Process Result: {result}")

    # Check retention date
    file_record = (
        await supabase.table("onboarding_files")
        .select("*")
        .eq("id", result["id"])
        .single()
    )
    assert file_record.data["retention_date"] is not None
    print("Retention date set successfully")


if __name__ == "__main__":
    asyncio.run(test_ocr_retention())
