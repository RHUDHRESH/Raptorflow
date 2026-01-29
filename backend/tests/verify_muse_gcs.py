import asyncio
import json
import os
import sys
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append(os.getcwd())

# [CRITICAL CHEAT] Mock heavy modules to prevent import hangs
sys.modules["backend.agents.graphs.content"] = MagicMock()
sys.modules["backend.agents.specialists.content_creator"] = MagicMock()
sys.modules["backend.core.auth"] = MagicMock()
sys.modules["backend.core.database"] = MagicMock()


async def run_test():
    print(">>> Verifying Muse GCS Integration...")

    # Mock dependencies BEFORE importing the module to avoid side effects
    with patch("backend.services.storage.storage_service") as mock_storage:
        # Mock upload_file to return a fake URI
        mock_storage.upload_file.return_value = (
            "gs://test-bucket/muse/workspace-123/content-456.md"
        )

        # Import the function to test
        from api.v1.muse import save_content_to_database

        # Mock DB
        mock_db = MagicMock()
        mock_db.execute = MagicMock()

        async def async_execute(*args, **kwargs):
            return True

        mock_db.execute.side_effect = async_execute

        # Test Data
        content_id = "content-456"
        request = MagicMock()
        request.workspace_id = "workspace-123"
        request.user_id = "user-789"
        request.content_type = "blog_post"
        request.topic = "Test Topic"
        request.tone = "Professional"
        request.target_audience = "Developers"
        request.brand_voice_notes = "None"

        result = {
            "final_content": "# Hello World\nThis is a test post.",
            "draft_content": "Draft...",
            "content_status": "approved",
            "quality_score": 95,
            "revision_count": 0,
            "content_versions": [{"version": 1, "content": "Draft..."}],
            "approval_required": False,
            "pending_approval": False,
            "tokens_used": 100,
            "cost_usd": 0.01,
        }

        # Execute
        print("   Invoking save_content_to_database...")
        await save_content_to_database(content_id, request, result, mock_db)

        # Verify GCS Upload
        print("   Checking GCS upload...")
        mock_storage.upload_file.assert_called_once()
        args, _ = mock_storage.upload_file.call_args
        # args[0] is file obj, args[1] is filename
        if args[1] == f"muse/workspace-123/{content_id}.md":
            print("   [PASS] Filename correct")
        else:
            print(f"   [FAIL] Filename mismatch: {args[1]}")

        # Verify DB Update
        print("   Checking DB insert...")
        mock_db.execute.assert_called_once()
        call_args = mock_db.execute.call_args

        # The params are passed as positional args after the query
        # access args from index 0 which is the query string, then parameters
        params = call_args[0]
        # In asyncpg/databases, params might be separate args
        # Our mock receives (query, param1, param2...)

        # Verify content_versions is in there with gcs_uri
        # It's the 14th argument (index 13) based on the SQL
        # $14 is content_versions

        # Let's just scan args for the list
        found_versions = False
        for arg in params:
            if isinstance(arg, list) and len(arg) > 0 and "gcs_uri" in arg[0]:
                if (
                    arg[0]["gcs_uri"]
                    == "gs://test-bucket/muse/workspace-123/content-456.md"
                ):
                    print("   [PASS] content_versions contains correct GCS URI")
                    found_versions = True
                    break

        if not found_versions:
            print("   [FAIL] content_versions did NOT contain GCS URI")
            print(f"   Args sent to DB: {params}")


if __name__ == "__main__":
    asyncio.run(run_test())
