import json


def test_vercel_json_env_vars():
    """Verify that vercel.json has the Matrix API URL."""
    with open("raptorflow-app/vercel.json", "r") as f:
        data = json.load(f)

    assert "NEXT_PUBLIC_MATRIX_API_URL" in data["env"]
