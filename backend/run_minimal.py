"""
Minimal Backend Runner (deprecated).
Use `backend.run_simple.py`.
"""


def main() -> None:
    """Deprecated runner. Use backend.run_simple.main instead."""
    from backend.run_simple import main as run_main

    print("Deprecated: use backend.run_simple.py")
    run_main()


if __name__ == "__main__":
    main()
