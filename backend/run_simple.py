"""
Simple Backend Runner
Clean startup script for the Raptorflow backend
"""

import uvicorn
from config_clean import get_settings


def main():
    """Run the FastAPI application"""
    settings = get_settings()

    print(f"Starting {settings.app_name}")
    print(f"Environment: {settings.environment}")
    print(f"Debug: {settings.debug}")
    print(f"Host: {settings.host}")
    print(f"Port: {settings.port}")

    uvicorn.run(
        "app:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info" if not settings.debug else "debug",
        app_dir=".",
    )


if __name__ == "__main__":
    main()
