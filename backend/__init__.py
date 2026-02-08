"""
Raptorflow backend package (reconstruction mode).

Importing this package must be lightweight: no SDK initialization, no background jobs,
and no optional subsystems (auth, payments, agents).

Create the FastAPI app via `backend.app_factory.create_app()`.
"""

__version__ = "1.0.0"

__all__ = ["__version__"]

