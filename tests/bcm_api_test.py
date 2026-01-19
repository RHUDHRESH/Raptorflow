import requests
import json

# Test rebuild endpoint
def test_rebuild():
    url = "http://localhost:8000/api/v1/context/rebuild"
    payload = {"workspace_id": "test_workspace", "force": True}
    response = requests.post(url, json=payload)
    print(f"Rebuild Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

# Test manifest retrieval
def test_retrieve():
    url = "http://localhost:8000/api/v1/context/manifest"
    params = {"workspace_id": "test_workspace"}
    response = requests.get(url, params=params)
    print(f"Retrieve Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    test_rebuild()
    test_retrieve()
