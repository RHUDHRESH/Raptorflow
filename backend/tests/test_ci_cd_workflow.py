import os


def test_workflow_exists():
    """Verify that backend-ci-cd.yml exists in the workflows directory."""
    assert os.path.exists(".github/workflows/backend-ci-cd.yml")
