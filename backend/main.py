"""
RaptorFlow Backend - Single Entry Point
Canonical FastAPI app wired through the app factory.
"""

from backend.app_factory import create_app
from backend.config import settings

app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.is_development,
    )
