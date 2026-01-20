"""
Comprehensive API Test for Onboarding, Moves, Muse, and Daily Wins
"""
import requests
import json

# Base URL
BASE_URL = "http://localhost:8000/api/v1"

# Test data
TEST_USER_ID = "test-user-123"

# Helper function
def print_response(response):
    print(f"Status Code: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)

# 1. Test Onboarding
print("\n=== Testing Onboarding ===")

# Create session
session_res = requests.post(
    f"{BASE_URL}/onboarding/session",
    json={"user_id": TEST_USER_ID}
)
print("\nCreate Onboarding Session:")
print_response(session_res)
session_id = session_res.json().get("session_id")

# Update step data
if session_id:
    step_res = requests.post(
        f"{BASE_URL}/onboarding/{session_id}/steps/1",
        json={"data": {"company": "Test Inc"}, "version": 1}
    )
    print("\nUpdate Step 1 Data:")
    print_response(step_res)

# 2. Test Moves
print("\n=== Testing Moves ===")

# Create move
move_res = requests.post(
    f"{BASE_URL}/moves",
    json={"name": "Test Move", "category": "growth"}
)
print("\nCreate Move:")
print_response(move_res)
move_id = move_res.json().get("id")

# List moves
list_res = requests.get(f"{BASE_URL}/moves")
print("\nList Moves:")
print_response(list_res)

# 3. Test Muse
print("\n=== Testing Muse ===")

# Send message to Muse
muse_res = requests.post(
    f"{BASE_URL}/muse/chat",
    json={
        "message": "Test message",
        "conversation_history": [],
        "user_id": TEST_USER_ID
    }
)
print("\nMuse Chat Response:")
print_response(muse_res)

# 4. Test Daily Wins
print("\n=== Testing Daily Wins ===")

# Generate daily win
daily_win_res = requests.post(
    f"{BASE_URL}/daily_wins/generate",
    json={"user_id": TEST_USER_ID}
)
print("\nGenerate Daily Win:")
print_response(daily_win_res)

print("\nTest completed.")
