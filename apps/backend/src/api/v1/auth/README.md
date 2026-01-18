# Authentication API Module

This module provides authentication and authorization endpoints for the Aura platform.

## Endpoints

### Public Endpoints

- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/login` - Authenticate and receive tokens
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - Revoke refresh token

### Protected Endpoints

- `GET /api/v1/auth/me` - Get current user profile
- `PATCH /api/v1/auth/me` - Update current user profile

### Admin Endpoints

- `GET /api/v1/auth/users` - List users (paginated)
- `POST /api/v1/auth/users/bulk` - Bulk create users
- `PATCH /api/v1/auth/users/bulk` - Bulk update users
- `DELETE /api/v1/auth/users/bulk` - Bulk delete users

## Authentication Flow

1. **Registration**: User creates account with email, username, password
2. **Login**: User authenticates and receives access + refresh tokens
3. **API Requests**: Include access token in `Authorization: Bearer <token>` header
4. **Token Refresh**: Use refresh token to get new access token when expired
5. **Logout**: Revoke refresh token to invalidate session

## Security Features

- **Password Hashing**: Bcrypt with 12 rounds
- **JWT Tokens**: HS256 algorithm with configurable expiration
- **Refresh Tokens**: Stored in Redis with TTL
- **CSRF Protection**: Double-submit cookie pattern
- **Security Headers**: HSTS, CSP, X-Frame-Options, etc.
- **Rate Limiting**: Token bucket algorithm with Redis

## Error Handling

All errors follow the standard error response format:

```json
{
  "error": {
    "message": "Error message",
    "type": "ErrorType",
    "status_code": 400,
    "details": {},
    "path": "/api/v1/auth/endpoint"
  }
}
```

## Examples

### Register User

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "johndoe",
    "password": "securepassword123"
  }'
```

### Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

### Get Current User

```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <access_token>"
```

## Future Enhancements

- [ ] Email verification
- [ ] Password reset flow
- [ ] Two-factor authentication (2FA)
- [ ] OAuth2 integration
- [ ] Permission system (beyond roles)
- [ ] Account lockout after failed attempts
- [ ] Session management (multiple devices)
