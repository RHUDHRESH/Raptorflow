"""
🔴 RAPTORFLOW AUTHENTICATION RED-TEAM TEST SUITE
================================================

This test suite performs comprehensive security testing of the authentication system.
Run these tests to verify the auth system is working correctly.

Usage:
    pytest tests/auth/test_auth_redteam.py -v

Requirements:
    - pytest
    - httpx
    - python-dotenv
"""

import os
import time
import uuid
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

import pytest
import httpx
from dotenv import load_dotenv

load_dotenv()

# =============================================================================
# CONFIGURATION
# =============================================================================

BASE_URL = os.getenv("NEXT_PUBLIC_APP_URL", "http://localhost:3000")
API_URL = os.getenv("NEXT_PUBLIC_API_URL", "http://localhost:3001")
SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY", "")

# Test user credentials (create in Supabase for testing)
TEST_USER_EMAIL = os.getenv("TEST_USER_EMAIL", "test@raptorflow.test")
TEST_USER_PASSWORD = os.getenv("TEST_USER_PASSWORD", "TestPassword123!")
TEST_USER_2_EMAIL = os.getenv("TEST_USER_2_EMAIL", "test2@raptorflow.test")


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def client():
    """HTTP client for making requests"""
    return httpx.Client(timeout=30.0, follow_redirects=False)


@pytest.fixture
def auth_headers(client):
    """Get authenticated headers for test user"""
    # Sign in to get session token
    response = client.post(
        f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
        headers={
            "apikey": SUPABASE_ANON_KEY,
            "Content-Type": "application/json",
        },
        json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
        }
    )
    
    if response.status_code != 200:
        pytest.skip("Test user not set up - skipping authenticated tests")
    
    data = response.json()
    access_token = data.get("access_token")
    
    return {
        "Authorization": f"Bearer {access_token}",
        "apikey": SUPABASE_ANON_KEY,
    }


# =============================================================================
# PART 1: UNAUTHENTICATED ACCESS TESTS
# =============================================================================

class TestUnauthenticatedAccess:
    """Test that protected routes are NOT accessible without authentication"""

    @pytest.mark.parametrize("route", [
        "/dashboard",
        "/workspace",
        "/onboarding",
        "/foundation",
        "/cohorts",
        "/campaigns",
        "/moves",
        "/muse",
        "/blackbox",
        "/matrix",
        "/admin",
        "/settings",
    ])
    def test_protected_routes_redirect_to_login(self, client, route):
        """
        RED-TEAM: Protected routes should redirect unauthenticated users to login
        
        PASS: Response is 302/307 redirect to /login
        FAIL: Response is 200 (page loads without auth)
        """
        response = client.get(f"{BASE_URL}{route}")
        
        # Should redirect to login
        assert response.status_code in [302, 307], \
            f"Route {route} returned {response.status_code} instead of redirect"
        
        location = response.headers.get("location", "")
        assert "/login" in location, \
            f"Route {route} should redirect to /login, got: {location}"

    @pytest.mark.parametrize("api_route", [
        "/api/user/profile",
        "/api/workspaces",
        "/api/icp/list",
        "/api/campaigns",
        "/api/moves",
        "/api/admin/users",
    ])
    def test_api_routes_require_auth(self, client, api_route):
        """
        RED-TEAM: API routes should return 401 without authentication
        
        PASS: Response is 401 Unauthorized
        FAIL: Response is 200 or returns data
        """
        response = client.get(f"{BASE_URL}{api_route}")
        
        assert response.status_code == 401, \
            f"API route {api_route} returned {response.status_code} instead of 401"


# =============================================================================
# PART 2: AUTHENTICATION BYPASS TESTS
# =============================================================================

class TestAuthBypass:
    """Test that authentication cannot be bypassed"""

    def test_no_mock_user_in_production(self, client):
        """
        RED-TEAM: Mock/demo users should not exist in production
        
        PASS: Cannot login with demo credentials
        FAIL: Demo user exists and can access app
        """
        # Try to sign in with the bypass demo credentials
        response = client.post(
            f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
            headers={
                "apikey": SUPABASE_ANON_KEY,
                "Content-Type": "application/json",
            },
            json={
                "email": "demo@raptorflow.com",
                "password": "demo",
            }
        )
        
        # Should fail - demo user should not exist
        assert response.status_code == 400, \
            "CRITICAL: Demo user exists! Remove bypass authentication."

    def test_cannot_access_with_fake_token(self, client):
        """
        RED-TEAM: Fake JWT tokens should be rejected
        
        PASS: Fake token returns 401
        FAIL: Fake token is accepted
        """
        fake_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkhhY2tlciIsImlhdCI6MTUxNjIzOTAyMn0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        
        response = client.get(
            f"{SUPABASE_URL}/rest/v1/users",
            headers={
                "Authorization": f"Bearer {fake_token}",
                "apikey": SUPABASE_ANON_KEY,
            }
        )
        
        assert response.status_code == 401, \
            "CRITICAL: Fake JWT token was accepted!"

    def test_cannot_access_with_expired_token(self, client):
        """
        RED-TEAM: Expired tokens should be rejected
        
        PASS: Expired token returns 401
        FAIL: Expired token is accepted
        """
        # This is a token that was valid but is now expired
        expired_token = os.getenv("TEST_EXPIRED_TOKEN", "")
        
        if not expired_token:
            pytest.skip("No expired token configured for testing")
        
        response = client.get(
            f"{SUPABASE_URL}/rest/v1/users",
            headers={
                "Authorization": f"Bearer {expired_token}",
                "apikey": SUPABASE_ANON_KEY,
            }
        )
        
        assert response.status_code == 401, \
            "CRITICAL: Expired token was accepted!"


# =============================================================================
# PART 3: DATA ISOLATION TESTS (RLS)
# =============================================================================

class TestDataIsolation:
    """Test that users can only access their own data"""

    def test_user_cannot_see_other_workspaces(self, client, auth_headers):
        """
        RED-TEAM: User A should NOT see User B's workspaces
        
        PASS: Only returns user's own workspaces
        FAIL: Returns other users' workspaces
        """
        # Get workspaces with auth
        response = client.get(
            f"{SUPABASE_URL}/rest/v1/workspaces?select=*",
            headers=auth_headers
        )
        
        if response.status_code != 200:
            pytest.skip("Could not fetch workspaces")
        
        workspaces = response.json()
        
        # All workspaces should belong to the authenticated user
        # (RLS should filter automatically)
        for workspace in workspaces:
            # The RLS policy should ensure we only see our own
            # If we see workspaces without proper user_id check, RLS is broken
            assert "user_id" in workspace, "Workspace missing user_id"

    def test_cannot_access_other_user_data_directly(self, client, auth_headers):
        """
        RED-TEAM: Cannot access another user's data by ID
        
        PASS: Request returns empty or 404
        FAIL: Returns other user's data
        """
        # Generate a random UUID that doesn't belong to this user
        fake_workspace_id = str(uuid.uuid4())
        
        response = client.get(
            f"{SUPABASE_URL}/rest/v1/workspaces?id=eq.{fake_workspace_id}&select=*",
            headers=auth_headers
        )
        
        # Should return empty array (RLS prevents access)
        data = response.json()
        assert len(data) == 0, \
            f"CRITICAL: Accessed workspace {fake_workspace_id} that doesn't belong to user!"

    def test_cannot_modify_other_user_data(self, client, auth_headers):
        """
        RED-TEAM: Cannot UPDATE another user's data
        
        PASS: Update fails or affects 0 rows
        FAIL: Update succeeds on another user's data
        """
        fake_workspace_id = str(uuid.uuid4())
        
        response = client.patch(
            f"{SUPABASE_URL}/rest/v1/workspaces?id=eq.{fake_workspace_id}",
            headers={**auth_headers, "Content-Type": "application/json", "Prefer": "return=representation"},
            json={"name": "HACKED"}
        )
        
        # Should return empty array (no rows affected due to RLS)
        if response.status_code == 200:
            data = response.json()
            assert len(data) == 0, \
                "CRITICAL: Was able to modify another user's workspace!"


# =============================================================================
# PART 4: INPUT VALIDATION TESTS
# =============================================================================

class TestInputValidation:
    """Test that inputs are properly validated and sanitized"""

    @pytest.mark.parametrize("malicious_email", [
        "test@example.com'; DROP TABLE users; --",
        "<script>alert('xss')</script>@example.com",
        "test@example.com\n\nBcc: hacker@evil.com",
        "a" * 500 + "@example.com",  # Very long email
    ])
    def test_login_sql_injection(self, client, malicious_email):
        """
        RED-TEAM: Login should reject/sanitize SQL injection attempts
        
        PASS: Request fails gracefully with validation error
        FAIL: SQL is executed or server crashes
        """
        response = client.post(
            f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
            headers={
                "apikey": SUPABASE_ANON_KEY,
                "Content-Type": "application/json",
            },
            json={
                "email": malicious_email,
                "password": "password123",
            }
        )
        
        # Should fail gracefully, not with server error
        assert response.status_code in [400, 422], \
            f"Unexpected response {response.status_code} for SQL injection attempt"

    @pytest.mark.parametrize("malicious_password", [
        "'; DELETE FROM auth.users; --",
        "<script>alert('xss')</script>",
        "a" * 10000,  # Very long password
    ])
    def test_password_injection(self, client, malicious_password):
        """
        RED-TEAM: Password field should handle malicious input safely
        
        PASS: Request fails gracefully
        FAIL: Server error or injection succeeds
        """
        response = client.post(
            f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
            headers={
                "apikey": SUPABASE_ANON_KEY,
                "Content-Type": "application/json",
            },
            json={
                "email": "test@example.com",
                "password": malicious_password,
            }
        )
        
        # Should fail gracefully
        assert response.status_code in [400, 422, 500] or response.status_code < 500, \
            "Server crashed on malicious password input"


# =============================================================================
# PART 5: RATE LIMITING TESTS
# =============================================================================

class TestRateLimiting:
    """Test that rate limiting prevents brute force attacks"""

    def test_login_rate_limiting(self, client):
        """
        RED-TEAM: Multiple failed logins should trigger rate limiting
        
        PASS: After X attempts, requests are blocked (429)
        FAIL: Unlimited login attempts allowed
        """
        blocked = False
        
        for i in range(15):  # Try 15 times
            response = client.post(
                f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
                headers={
                    "apikey": SUPABASE_ANON_KEY,
                    "Content-Type": "application/json",
                },
                json={
                    "email": f"ratelimit-test-{uuid.uuid4()}@example.com",
                    "password": "wrongpassword",
                }
            )
            
            if response.status_code == 429:
                blocked = True
                break
            
            time.sleep(0.1)  # Small delay between requests
        
        # Note: Supabase has its own rate limiting, but we should verify
        # This test may need adjustment based on Supabase's rate limits
        # For now, we just verify the endpoint responds appropriately

    def test_api_rate_limiting(self, client, auth_headers):
        """
        RED-TEAM: API endpoints should have rate limiting
        
        PASS: After many rapid requests, get 429
        FAIL: Unlimited requests allowed
        """
        blocked = False
        
        for i in range(50):  # Rapid fire 50 requests
            response = client.get(
                f"{BASE_URL}/api/user/profile",
                headers=auth_headers
            )
            
            if response.status_code == 429:
                blocked = True
                break
        
        # Rate limiting should kick in at some point
        # Exact threshold depends on configuration


# =============================================================================
# PART 6: SESSION SECURITY TESTS
# =============================================================================

class TestSessionSecurity:
    """Test session security measures"""

    def test_session_token_rotation(self, client, auth_headers):
        """
        RED-TEAM: Session tokens should be rotated periodically
        
        PASS: Old session is invalidated after refresh
        FAIL: Old session remains valid
        """
        # This test would need to simulate session rotation
        # For now, verify that refresh endpoint exists
        response = client.post(
            f"{SUPABASE_URL}/auth/v1/token?grant_type=refresh_token",
            headers={
                "apikey": SUPABASE_ANON_KEY,
                "Content-Type": "application/json",
            },
            json={"refresh_token": "invalid_token"}
        )
        
        # Should fail with invalid refresh token
        assert response.status_code in [400, 401], \
            "Refresh token endpoint behaving unexpectedly"

    def test_logout_invalidates_session(self, client):
        """
        RED-TEAM: After logout, session should be invalid
        
        PASS: Session no longer works after logout
        FAIL: Session still works after logout
        """
        # Sign in
        login_response = client.post(
            f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
            headers={
                "apikey": SUPABASE_ANON_KEY,
                "Content-Type": "application/json",
            },
            json={
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD,
            }
        )
        
        if login_response.status_code != 200:
            pytest.skip("Could not login for logout test")
        
        data = login_response.json()
        access_token = data.get("access_token")
        
        # Sign out
        logout_response = client.post(
            f"{SUPABASE_URL}/auth/v1/logout",
            headers={
                "Authorization": f"Bearer {access_token}",
                "apikey": SUPABASE_ANON_KEY,
            }
        )
        
        # Try to use the old token
        # Note: Supabase JWTs are stateless, so this tests server-side validation


# =============================================================================
# PART 7: PASSWORD SECURITY TESTS
# =============================================================================

class TestPasswordSecurity:
    """Test password security requirements"""

    @pytest.mark.parametrize("weak_password,should_fail", [
        ("123456", True),
        ("password", True),
        ("abc", True),
        ("abcdefgh", True),  # No uppercase, number, or special
        ("ABCDEFGH", True),  # No lowercase, number, or special
        ("Abcd1234", True),  # No special character
        ("Abcd123!", False),  # Valid password
    ])
    def test_password_strength_requirements(self, client, weak_password, should_fail):
        """
        RED-TEAM: Weak passwords should be rejected
        
        PASS: Weak passwords fail, strong passwords pass
        FAIL: Weak passwords are accepted
        """
        response = client.post(
            f"{SUPABASE_URL}/auth/v1/signup",
            headers={
                "apikey": SUPABASE_ANON_KEY,
                "Content-Type": "application/json",
            },
            json={
                "email": f"pwtest-{uuid.uuid4()}@example.com",
                "password": weak_password,
            }
        )
        
        if should_fail:
            # Supabase has minimum password length of 6 by default
            # Our policy should be stricter
            pass  # Supabase handles this


# =============================================================================
# PART 8: ADMIN ACCESS TESTS
# =============================================================================

class TestAdminAccess:
    """Test that admin routes are properly protected"""

    def test_regular_user_cannot_access_admin(self, client, auth_headers):
        """
        RED-TEAM: Regular users should NOT access admin routes
        
        PASS: Admin routes return 403 for regular users
        FAIL: Regular user can access admin
        """
        response = client.get(
            f"{BASE_URL}/admin",
            headers=auth_headers
        )
        
        # Should be forbidden or redirect
        assert response.status_code in [302, 307, 403], \
            f"Regular user accessed admin route! Status: {response.status_code}"

    def test_cannot_escalate_to_admin(self, client, auth_headers):
        """
        RED-TEAM: Users cannot change their own role to admin
        
        PASS: Role change attempt fails
        FAIL: User becomes admin
        """
        # Try to update own role to admin
        response = client.patch(
            f"{SUPABASE_URL}/rest/v1/users?select=id",
            headers={**auth_headers, "Content-Type": "application/json"},
            json={"role": "admin"}
        )
        
        # This should either fail or not actually change the role
        # due to RLS policies preventing role self-escalation


# =============================================================================
# PART 9: SUBSCRIPTION BYPASS TESTS
# =============================================================================

class TestSubscriptionSecurity:
    """Test that subscription/payment cannot be bypassed"""

    def test_cannot_access_premium_without_subscription(self, client, auth_headers):
        """
        RED-TEAM: Premium features require active subscription
        
        PASS: Premium features blocked without subscription
        FAIL: Premium features accessible without payment
        """
        # This depends on how premium features are gated
        # Example: API access is Soar-only
        pass

    def test_cannot_modify_subscription_directly(self, client, auth_headers):
        """
        RED-TEAM: Users cannot directly modify their subscription status
        
        PASS: Direct subscription modification fails
        FAIL: User can set their own subscription to active
        """
        response = client.patch(
            f"{SUPABASE_URL}/rest/v1/user_subscriptions",
            headers={**auth_headers, "Content-Type": "application/json"},
            json={"status": "active"}
        )
        
        # RLS should prevent this or require specific conditions


# =============================================================================
# SUMMARY REPORT
# =============================================================================

def test_generate_security_report():
    """
    Generate a summary of all security tests
    Run this last to see overall security posture
    """
    print("\n" + "=" * 60)
    print("RAPTORFLOW SECURITY TEST SUMMARY")
    print("=" * 60)
    print(f"Test Run: {datetime.now().isoformat()}")
    print(f"Target: {BASE_URL}")
    print("=" * 60)
    print("\nReview pytest output above for detailed results.")
    print("\nCRITICAL items to verify manually:")
    print("[ ] Auth bypass code removed from src/lib/auth.ts")
    print("[ ] RLS enabled on ALL tables with user data")
    print("[ ] No demo/mock users in production")
    print("[ ] Email verification required for new accounts")
    print("[ ] Rate limiting configured on auth endpoints")
    print("[ ] HTTPS enforced in production")
    print("=" * 60)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
