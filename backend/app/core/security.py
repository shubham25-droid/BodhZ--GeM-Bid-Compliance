import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, List
from jose import jwt, JWTError
from fastapi import HTTPException, Security, status, Depends, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db

security_scheme = HTTPBearer(auto_error=False)


# --------------------------------------------------
# CRYPTOGRAPHICALLY SECURE PASSWORD HASHING (PBKDF2-SHA256)
# --------------------------------------------------
def hash_password(password: str) -> str:
    """Generates a secure salted PBKDF2-HMAC-SHA256 hash."""
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return f"{salt}${key.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain text password against a stored salted PBKDF2 hash in constant time."""
    try:
        if "$" not in hashed_password:
            return plain_password == hashed_password
        salt, stored_key = hashed_password.split("$", 1)
        calc_key = hashlib.pbkdf2_hmac('sha256', plain_password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return secrets.compare_digest(calc_key.hex(), stored_key)
    except Exception:
        return False


# --------------------------------------------------
# JWT TOKEN GENERATION & VALIDATION
# --------------------------------------------------
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Creates a cryptographically signed JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Decodes and validates a JWT token, raising HTTP 401 if invalid."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials or token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )


# --------------------------------------------------
# SECURE COOKIE HELPERS
# --------------------------------------------------
def set_auth_cookie(response: Response, token: str):
    """Sets a secure HttpOnly session cookie on the response."""
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=False  # True in production HTTPS
    )


def clear_auth_cookie(response: Response):
    """Clears the session cookie on logout."""
    response.delete_cookie(key="access_token", samesite="lax")


# --------------------------------------------------
# AUTHENTICATED USER EXTRACTION DEPENDENCY
# --------------------------------------------------
def get_current_user(
    request: Request,
    auth_header: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: Session = Depends(get_db)
):
    """
    Extracts the current authenticated user from:
    1. Authorization: Bearer <token> header
    2. HttpOnly access_token cookie
    Validates token signature and loads UserModel from DB.
    """
    from app.models.models import UserModel

    token = None
    if auth_header and auth_header.credentials:
        token = auth_header.credentials
    elif "access_token" in request.cookies:
        token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please log in.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token subject",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        # Fallback by username if sub was username
        user = db.query(UserModel).filter(UserModel.username == payload.get("username")).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found or deleted",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account has been deactivated."
        )

    return user


def get_optional_current_user(
    request: Request,
    auth_header: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: Session = Depends(get_db)
):
    """Returns authenticated user if present, or None if unauthenticated."""
    try:
        return get_current_user(request, auth_header, db)
    except HTTPException:
        return None


def require_role(allowed_roles: List[str]):
    """Role-Based Access Control (RBAC) dependency factory."""
    def role_checker(current_user = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {allowed_roles}, your role: {current_user.role}"
            )
        return current_user
    return role_checker


# --------------------------------------------------
# SECURITY HEADERS MIDDLEWARE
# --------------------------------------------------
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware injecting government-grade HTTP security headers while allowing
    trusted UI CDNs for styling.
    """
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self' 'unsafe-inline' 'unsafe-eval' https: http:; "
            "style-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://fonts.googleapis.com https://cdnjs.cloudflare.com; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.tailwindcss.com https://cdn.jsdelivr.net; "
            "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com;"
        )
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response
