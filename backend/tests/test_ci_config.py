import os

def test_ci_workflow_exists():
    """Verify that the Python CI workflow file is present."""
    path = ".github/workflows/python-ci.yml"
    assert os.path.exists(path)

def test_ci_workflow_content():
    """Ensure the CI workflow targets the backend directory and uses flake8."""
    with open(".github/workflows/python-ci.yml", "r") as f:
        content = f.read()
        assert "flake8 backend" in content
        assert "pytest backend/tests" in content
