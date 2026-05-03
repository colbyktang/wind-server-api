# OAuth2 Authentication Flow

This document explains how the JWT-based OAuth2 authentication system works in the Wind Server application.

## Overview

The authentication system uses JSON Web Tokens (JWT) with a dual-token approach:
- **Access Token**: Short-lived (30 minutes default), sent with every API request
- **Refresh Token**: Long-lived (7 days default), used to obtain new access tokens

## Architecture Components

### Backend (FastAPI)
- `app/auth/security.py` - Token creation, validation, password hashing
- `app/auth/auth_routes.py` - Authentication endpoints (login, register, refresh, logout)
- `app/auth/auth_models.py` - Database models for users, refresh tokens, revoked tokens

### Frontend (Angular)
- `services/auth.service.ts` - Authentication API calls and token management
- `interceptors/auth.interceptor.ts` - Automatic token injection and refresh

## Authentication Flows

### 1. User Registration

**Request Flow:**
```
Frontend                          Backend
   |                                 |
   |  POST /auth/register            |
   |  { username, password }         |
   |-------------------------------->|
   |                                 | 1. Validate username is unique
   |                                 | 2. Hash password with bcrypt
   |                                 | 3. Create user record in database
   |                                 |
   |  { message: "User created" }    |
   |<--------------------------------|
   |                                 |
```

**Implementation Details:**
- Passwords are hashed using bcrypt with automatic salt generation
- Passwords are truncated to 72 bytes (bcrypt limitation)
- Rate limited to 5 requests per minute per IP address

### 2. User Login

**Request Flow:**
```
Frontend                          Backend
   |                                 |
   |  POST /auth/login               |
   |  { username, password }         |
   |-------------------------------->|
   |                                 | 1. Look up user by username
   |                                 | 2. Verify password with bcrypt
   |                                 | 3. Create access token (JWT)
   |                                 | 4. Create refresh token (random)
   |                                 | 5. Hash refresh token with SHA-256
   |                                 | 6. Store hashed refresh token in DB
   |                                 |
   |  { access_token, refresh_token, |
   |    token_type: "bearer" }       |
   |<--------------------------------|
   | Store tokens in localStorage    |
   |                                 |
```

**Access Token Structure:**
```json
{
  "sub": "username",
  "exp": 1234567890,
  "jti": "unique-token-id",
  "role": "user"
}
```

**Token Details:**
- Access token is a signed JWT (HS256 algorithm)
- Contains user identity, expiry, unique ID (jti), and role
- Refresh token is a 64-byte URL-safe random string
- Only the hashed refresh token is stored in the database

**Security Features:**
- Rate limited to 5 requests per minute per IP address
- Passwords never stored in plain text
- Refresh tokens stored as SHA-256 hashes

### 3. Authenticated API Requests

**Request Flow:**
```
Frontend                          Backend
   |                                 |
   | HTTP Interceptor adds header    |
   | Authorization: Bearer <token>   |
   |                                 |
   |  GET /api/protected             |
   |  Header: Authorization          |
   |-------------------------------->|
   |                                 | 1. Extract token from header
   |                                 | 2. Verify JWT signature
   |                                 | 3. Check expiration
   |                                 | 4. Check if token is revoked (logout)
   |                                 | 5. Extract user data from token
   |                                 |
   |  { protected_data }             |
   |<--------------------------------|
   |                                 |
```

**OAuth2 Scheme:**
- Uses `OAuth2PasswordBearer` with token URL `/auth/login`
- Tokens are extracted from the `Authorization` header
- Format: `Authorization: Bearer <access_token>`

**Token Validation:**
1. JWT signature verification using secret key
2. Expiry check (automatic via PyJWT)
3. Revocation check against database blocklist

### 4. Token Refresh

**Request Flow:**
```
Frontend                          Backend
   |                                 |
   | Access token expired (401)      |
   |<--------------------------------|
   |                                 |
   | HTTP Interceptor catches 401    |
   |                                 |
   |  POST /auth/refresh             |
   |  { refresh_token }              |
   |-------------------------------->|
   |                                 | 1. Hash the refresh token
   |                                 | 2. Look up in database
   |                                 | 3. Verify not revoked
   |                                 | 4. Check expiration
   |                                 | 5. Create new access token
   |                                 |
   |  { access_token,                |
   |    token_type: "bearer" }       |
   |<--------------------------------|
   | Update access_token in storage  |
   |                                 |
   |  Retry original request         |
   |  with new access token          |
   |-------------------------------->|
   |                                 |
```

**Automatic Refresh:**
- The Angular HTTP interceptor catches 401 errors
- Automatically calls `/auth/refresh` with the refresh token
- Retries the original request with the new access token
- If refresh fails, redirects user to login page

**Why This Approach:**
- Short-lived access tokens limit exposure if compromised
- Client doesn't need to check token expiry before each request
- Seamless user experience with automatic token renewal

### 5. User Logout

**Request Flow:**
```
Frontend                          Backend
   |                                 |
   |  POST /auth/logout              |
   |  { refresh_token }              |
   |  Header: Authorization          |
   |-------------------------------->|
   |                                 | 1. Mark refresh token as revoked
   |                                 | 2. Extract jti from access token
   |                                 | 3. Add jti to revoked tokens table
   |                                 | 4. Commit to database
   |                                 |
   |  { message: "Logged out" }      |
   |<--------------------------------|
   | Clear tokens from localStorage  |
   |                                 |
```

**Token Revocation:**
- Refresh token marked as `revoked = true` in database
- Access token's `jti` (unique ID) added to blocklist
- Future requests with revoked tokens return 401

**Performance Note:**
- Checking the revoked token table on every request adds database overhead
- In high-traffic systems, this is typically moved to Redis (in-memory cache)
- Current implementation is suitable for small to medium scale

## Security Considerations

### Token Storage
**Frontend (localStorage):**
- Access token: `localStorage.getItem('access_token')`
- Refresh token: `localStorage.getItem('refresh_token')`

**Security Trade-offs:**
- localStorage is vulnerable to XSS attacks
- Alternative: httpOnly cookies (prevents XSS but vulnerable to CSRF)
- Current approach requires proper XSS protection in the frontend

### Password Security
- Bcrypt hashing with automatic salt generation
- Passwords truncated to 72 bytes (bcrypt specification)
- Password verification uses constant-time comparison

### Token Security
- Access tokens are signed JWTs (cannot be modified without secret key)
- Refresh tokens are cryptographically random (64 bytes)
- Secret key loaded from environment variable (fails at startup if missing)
- Tokens include unique identifiers (jti) for revocation tracking

### Rate Limiting
- Login and register endpoints limited to 5 requests/minute per IP
- Uses SlowAPI middleware
- Prevents brute force attacks

### CORS Configuration
- Allowed origins configured via environment variable
- Default: `http://localhost:4200` (development)
- Production should restrict to actual frontend domain

## Configuration

### Environment Variables

**Required:**
```bash
JWT_SECRET=your-secret-key-here
```

**Optional (with defaults):**
```bash
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ALLOWED_ORIGINS=http://localhost:4200
```

### Database Models

**User Table:**
- `id`: Primary key
- `username`: Unique identifier
- `password_hash`: Bcrypt hashed password
- `role`: User role (user/admin)
- `created_at`: Account creation timestamp

**RefreshToken Table:**
- `id`: Primary key
- `user_id`: Foreign key to User
- `token_hash`: SHA-256 hash of refresh token
- `expires_at`: Expiration timestamp
- `revoked`: Boolean flag
- `created_at`: Token creation timestamp

**RevokedToken Table:**
- `id`: Primary key
- `jti`: Unique token identifier from JWT
- `expires_at`: Original token expiration
- `revoked_at`: When token was revoked

## API Endpoints

### POST /auth/register
**Request:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response (201):**
```json
{
  "message": "User created successfully."
}
```

### POST /auth/login
**Request:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "random-url-safe-string",
  "token_type": "bearer"
}
```

### POST /auth/refresh
**Request:**
```json
{
  "refresh_token": "string"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### POST /auth/logout
**Request:**
```json
{
  "refresh_token": "string"
}
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "message": "Logged out."
}
```

## Common Issues and Debugging

### Token Expired
**Error:** `401 Unauthorized - Token expired`
**Solution:** The HTTP interceptor should automatically refresh the token. Check that refresh token is still valid.

### Invalid Token
**Error:** `401 Unauthorized - Invalid token`
**Causes:**
- Token signature doesn't match (wrong secret key)
- Malformed token
- Token has been revoked

### Refresh Token Issues
**Error:** `401 Unauthorized - Invalid or expired refresh token`
**Causes:**
- Refresh token has expired (>7 days old)
- Refresh token has been revoked (user logged out)
- Refresh token hash doesn't match database

### CORS Errors
**Error:** CORS policy blocks request
**Solution:** Ensure frontend origin is in `ALLOWED_ORIGINS` environment variable

## Future Improvements

1. **Redis Token Blocklist**: Move revoked tokens to Redis for faster lookups
2. **Refresh Token Rotation**: Issue new refresh token with each refresh
3. **Device Tracking**: Associate refresh tokens with devices
4. **Token Introspection**: Endpoint to validate token without making a protected request
5. **OAuth2 Scopes**: Implement fine-grained permissions
6. **Multi-Factor Authentication**: Add 2FA support
7. **Password Reset Flow**: Email-based password recovery
8. **Session Management**: Allow users to view and revoke active sessions
