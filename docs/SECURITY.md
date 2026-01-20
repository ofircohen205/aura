# Security Guide

This document covers security considerations, features, and best practices for the Aura platform.

## Table of Contents

1. [Security Features](#security-features)
2. [Security Concerns](#security-concerns)
3. [Best Practices](#best-practices)
4. [References](#references)

## Security Features

### Input Validation

- **Frontend**: Zod schema validation for all forms (login, register, profile)
- **Backend**: Pydantic models with field validators
- **Password Requirements**: Enforced on both frontend and backend (min 8 chars, uppercase, lowercase, digit, special char)

### CSRF Protection

- **Backend**: CSRF middleware using double-submit cookie pattern
- **Frontend**: API client automatically includes CSRF token in request headers for state-changing operations
- **Implementation**: Token stored in cookie, sent in `X-CSRF-Token` header

### Security Headers

- **Backend**: SecurityHeadersMiddleware adds comprehensive security headers
- **Frontend**: Next.js headers configuration adds security headers
- **Headers Included**:
  - `X-Content-Type-Options: nosniff` - Prevents MIME type sniffing
  - `X-Frame-Options: DENY` - Prevents clickjacking
  - `X-XSS-Protection: 1; mode=block` - XSS protection
  - `Referrer-Policy: strict-origin-when-cross-origin` - Controls referrer information
  - `Permissions-Policy` - Restricts browser features
  - `Strict-Transport-Security` - HSTS (production only)

### Authentication & Authorization

- JWT tokens with expiration
- Refresh token rotation
- Protected routes on frontend
- Backend dependency injection for auth checks
- Password hashing: Bcrypt with 12 rounds
- Refresh tokens stored in Redis with TTL
- Rate limiting: Token bucket algorithm with Redis

## Security Concerns

### Token Storage (XSS Vulnerability)

**Current Implementation**: Access and refresh tokens are stored in `localStorage`.

**Security Risk**: Tokens stored in `localStorage` are vulnerable to XSS (Cross-Site Scripting) attacks. If an attacker can inject malicious JavaScript into the application, they can access tokens from `localStorage`.

**Mitigation in Place**:

- Input validation on all forms
- Security headers (CSP, X-XSS-Protection)
- No use of `dangerouslySetInnerHTML` or `eval()`
- React's built-in XSS protection for rendering

**Recommended Solution**: Use httpOnly cookies for token storage. This requires:

1. **Backend Changes**:
   - Modify authentication endpoints to set httpOnly cookies instead of returning tokens in response body
   - Ensure cookies are marked as `Secure` (HTTPS only) and `SameSite=Strict` or `SameSite=Lax`
   - Update CORS configuration to allow credentials

2. **Frontend Changes**:
   - Remove `localStorage` token storage
   - Update API client to rely on cookies being sent automatically
   - Update token refresh logic to work with cookies

**Migration Path**:

1. Implement cookie-based authentication on backend
2. Add feature flag to switch between localStorage and cookie-based auth
3. Test thoroughly
4. Deploy backend changes
5. Deploy frontend changes
6. Monitor for issues
7. Remove localStorage code after verification

**Priority**: Medium - Should be addressed before production deployment

## Security Best Practices Followed

1. ✅ **Input Validation**: All user inputs validated on both client and server
2. ✅ **Output Encoding**: React automatically escapes content (no XSS from rendering)
3. ✅ **CSRF Protection**: Double-submit cookie pattern implemented
4. ✅ **Security Headers**: Comprehensive headers set on all responses
5. ✅ **HTTPS**: Required in production (HSTS header set)
6. ✅ **Rate Limiting**: Implemented on backend
7. ✅ **Error Handling**: Generic error messages (no information disclosure)
8. ✅ **Dependencies**: Regular security audits recommended

## References

- [OWASP: XSS Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [OWASP: Session Management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)
- [OWASP: CSRF Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
- [OWASP: Security Headers](https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Headers_Cheat_Sheet.html)

## Related Documentation

- [Deployment Guide](DEPLOYMENT.md) - Secrets management and environment configuration
- [Deployment Guide](DEPLOYMENT.md) - Production deployment security considerations
