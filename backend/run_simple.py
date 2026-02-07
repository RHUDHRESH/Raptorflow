"""
Simple Backend Runner (canonical).
"""

import uvicorn

from backend.config import settings


def main() -> None:
    """Run the FastAPI application."""
    uvicorn.run(
        "backend.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.is_development,
        log_level="info" if not settings.DEBUG else "debug",
    )


if __name__ == "__main__":
    main()
