from fastapi import APIRouter, HTTPException
import sentry_sdk

router = APIRouter()

@router.get("/test-sentry")
async def test_sentry(error: bool = False):
    if (error):
        try:
            with sentry_sdk.configure_scope() as scope:
                scope.set_context("sensitive_data", {
                    "api_key": "sk-backend-test-12345",
                    "user_email": "backend-user@example.com"
                })
            raise ValueError("Sentry Backend Test Error: PII Scrubbing Verification")
        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise HTTPException(status_code=500, detail=str(e))
    
    return {
        "message": "Sentry backend test active. Use ?error=true to trigger an error.",
        "dsn_configured": bool(sentry_sdk.Hub.current.client and sentry_sdk.Hub.current.client.dsn)
    }
