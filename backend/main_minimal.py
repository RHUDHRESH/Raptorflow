"""
Deprecated entrypoint.
Use `backend.main` as the single canonical backend app.
This module keeps a minimal app instance for tests and backward compatibility.
"""

from backend.app_factory import create_app

# Keep docs enabled for test clients that expect /docs and /redoc
app = create_app(enable_docs=True)
