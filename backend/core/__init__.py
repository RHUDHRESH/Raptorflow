"""
Backend core utilities.

In reconstruction mode, this package must remain lightweight to avoid importing
legacy/broken modules at startup. Import specific modules directly (e.g.
`core.supabase_mgr`) instead of relying on package-level exports.
"""

__all__: list[str] = []

