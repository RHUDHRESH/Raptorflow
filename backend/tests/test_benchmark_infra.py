import os


def test_benchmark_script_exists():
    """Verify that the Benchmarking script exists."""
    assert os.path.exists("backend/scripts/benchmark_matrix.py")
