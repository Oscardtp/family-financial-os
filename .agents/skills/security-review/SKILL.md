---
name: security-review
description: Use this skill when adding authentication, handling user input, working with secrets, creating API endpoints, or implementing payment/sensitive features. Provides comprehensive security checklist and patterns.
---

# Security Review Skill

## Security Checklist

### 1. Secrets Management
- No hardcoded API keys, tokens, or passwords
- All secrets in environment variables
- `.env` in .gitignore
- No secrets in git history

### 2. Input Validation
- All user inputs validated with schemas (Pydantic, Zod)
- File uploads restricted (size, type, extension)
- Whitelist validation (not blacklist)
- Error messages don't leak sensitive info

### 3. SQL Injection Prevention
- All database queries use parameterized queries
- No string concatenation in SQL
- ORM/query builder used correctly

### 4. Authentication & Authorization
- Tokens stored securely (httpOnly cookies or secure storage)
- Authorization checks before sensitive operations
- Role-based access control implemented
- Session management secure

### 5. XSS Prevention
- User-provided HTML sanitized
- Content Security Policy configured
- No unvalidated dynamic content rendering

### 6. CSRF Protection
- CSRF tokens on state-changing operations
- SameSite=Strict on all cookies

### 7. Rate Limiting
- Rate limiting on all API endpoints
- Stricter limits on expensive operations

### 8. Sensitive Data Exposure
- No passwords, tokens, or secrets in logs
- Error messages generic for users
- Detailed errors only in server logs
- No stack traces exposed to users

### 9. Dependency Security
- Dependencies up to date
- No known vulnerabilities
- Lock files committed

## Pre-Deployment Security Checklist

- [ ] **Secrets**: No hardcoded secrets, all in env vars
- [ ] **Input Validation**: All user inputs validated
- [ ] **SQL Injection**: All queries parameterized
- [ ] **XSS**: User content sanitized
- [ ] **CSRF**: Protection enabled
- [ ] **Authentication**: Proper token handling
- [ ] **Authorization**: Role checks in place
- [ ] **Rate Limiting**: Enabled on all endpoints
- [ ] **HTTPS**: Enforced in production
- [ ] **Security Headers**: CSP, X-Frame-Options configured
- [ ] **Error Handling**: No sensitive data in errors
- [ ] **Logging**: No sensitive data logged
- [ ] **Dependencies**: Up to date, no vulnerabilities
- [ ] **CORS**: Properly configured
