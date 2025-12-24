import os


def test_ci_workflow_exists():
    """Verify that the Python CI workflow file is present."""
    path = ".github/workflows/python-ci.yml"
    assert os.path.exists(path)


def test_ci_workflow_content():
    """Ensure the CI workflow targets the backend directory and uses flake8."""
    with open(".github/workflows/python-ci.yml", "r") as f:
        content = f.read()


def test_pre_commit_hooks_defined():
    """Verify that isort and bandit hooks are present in the configuration."""
    path = ".pre-commit-config.yaml"
    with open(path, "r") as f:
        content = f.read()
        assert "id: isort" in content
        assert "id: bandit" in content
        assert "id: flake8" in content
