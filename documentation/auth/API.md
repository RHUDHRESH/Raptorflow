# Authentication API Endpoints

## Base URL
```
/api/v1/auth
```

## Endpoints

### POST /auth/signup
Create a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (Success):**
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "user-uuid",
    "email": "user@example.com"
  }
}
```

**Response (Email Confirmation Required):**
```json
{
  "message": "Please check your email to confirm your account",
  "user": { ... },
  "requires_email_confirmation": true
}
```

**Response (Error):**
```json
{
  "detail": "Password must be at least 8 characters"
}
```

**Rate Limit:** 3 requests per hour per IP

---

### POST /auth/login
Authenticate a user.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (Success):**
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "user-uuid",
    "email": "user@example.com"
  }
}
```

**Response (Error):**
```json
{
  "detail": "Invalid email or password"
}
```

**Rate Limit:** 5 requests per minute per IP

---

### POST /auth/logout
Sign out the current user.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "message": "Logged out successfully"
}
```

---

### POST /auth/refresh
Refresh access token using refresh token.

**Request:**
```json
{
  "refresh_token": "eyJhbGc..."
}
```

Or send refresh token via cookie (automatic).

**Response:**
```json
{
  "access_token": "new-access-token",
  "refresh_token": "new-refresh-token",
  "token_type": "bearer",
  "expires_in": 3600
}
```

---

### GET /auth/me
Get current authenticated user.

**Headers:**
```
Authorization: Bearer <access_token>
```

Or cookies (automatic with HTTP-only cookies).

**Response:**
```json
{
  "id": "user-uuid",
  "email": "user@example.com",
  "role": "owner",
  "workspace_id": "workspace-uuid"
}
```

---

### POST /auth/verify
Verify if a token is valid.

**Request:**
```json
{
  "access_token": "eyJhbGc..."
}
```

Or use Authorization header or cookie.

**Response:**
```json
{
  "valid": true,
  "user_id": "user-uuid",
  "email": "user@example.com",
  "user": { ... }
}
```

---

### POST /auth/reset-password
Request password reset email.

**Request:**
```json
{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "message": "If the email exists, a password reset link has been sent"
}
```

*Note: Always returns success for security (doesn't reveal if email exists)*

---

### GET /auth/health
Check authentication service health.

**Response:**
```json
{
  "status": "healthy",
  "provider": "supabase",
  "url": "https://xxx.supabase.co"
}
```

---

## Cookie Configuration

| Cookie | Name | Options |
|---------|------|---------|
| Access Token | `sb-access-token` | HttpOnly, Secure, SameSite=Lax, 1hr |
| Refresh Token | `sb-refresh-token` | HttpOnly, Secure, SameSite=Lax, 7 days |

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request (invalid input) |
| 401 | Unauthorized (invalid credentials) |
| 429 | Too Many Requests (rate limited) |
| 500 | Internal Server Error |
