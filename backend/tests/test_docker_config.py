import os

def test_docker_files_exist():
    """Verify that essential Docker configuration files are present."""
    assert os.path.exists("docker-compose.yml")
    assert os.path.exists("backend/Dockerfile")
    assert os.path.exists("raptorflow-app/Dockerfile")

def test_docker_compose_services():
    """Ensure that backend and frontend services are defined in docker-compose."""
    with open("docker-compose.yml", "r") as f:
        content = f.read()
        assert "backend:" in content
        assert "frontend:" in content
        assert "redis:" in content
