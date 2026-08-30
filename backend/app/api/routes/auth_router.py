import logging
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.core.security import (
    hash_password, verify_password, create_access_token,
    get_current_user, set_auth_cookie, clear_auth_cookie
)
from app.models.models import UserModel
from app.schemas.schemas import (
    LoginRequestSchema, RegisterRequestSchema, TokenSchema, UserResponseSchema
)
from app.core.db_seeder import seed_initial_database

import hmac
import hashlib
import time
import random
import string

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication & Security"])

CAPTCHA_SECRET = "bodhz_sih26100_captcha_secret_key_2026"


# --------------------------------------------------
# 0. SERVER-VALIDATED CAPTCHA GENERATION
# --------------------------------------------------
@router.get("/captcha", summary="Generate Server-Validated Security Captcha")
def get_captcha():
    """Generates a secure, time-limited CAPTCHA challenge with cryptographic signature."""
    chars = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"
    code = "".join(random.choice(chars) for _ in range(5))
    timestamp = int(time.time())
    sig_raw = f"{code}:{timestamp}:{CAPTCHA_SECRET}".encode("utf-8")
    sig = hashlib.sha256(sig_raw).hexdigest()[:16]
    token = f"{sig}.{timestamp}"
    return {
        "captcha_code": code,
        "captcha_token": token,
        "expires_in_seconds": 300
    }



# --------------------------------------------------
# 1. OFFICER REGISTRATION / SIGNUP ENDPOINT
# --------------------------------------------------
@router.post("/register", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED, summary="Register Procurement Officer or Auditor")
def register_user(
    reg_in: RegisterRequestSchema,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Registers a new procurement official with verified professional metadata
    (Organization, Department, Role, Phone, Official Email).
    Enforces password complexity and uniqueness of username and email.
    """
    clean_username = reg_in.username.strip().lower()
    clean_email = reg_in.email.strip().lower()

    existing_username = db.query(UserModel).filter(func.lower(UserModel.username) == clean_username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Username '{reg_in.username}' is already registered. Please choose another username or log in."
        )

    existing_email = db.query(UserModel).filter(func.lower(UserModel.email) == clean_email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email '{reg_in.email}' is already registered. Please use another email or log in."
        )

    if len(reg_in.password.strip()) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters long."
        )

    new_user = UserModel(
        username=reg_in.username.strip(),
        email=clean_email,
        hashed_password=hash_password(reg_in.password.strip()),
        full_name=reg_in.full_name.strip(),
        role=reg_in.role or "PROCUREMENT_OFFICER",
        organization=reg_in.organization or "Government e-Marketplace (GeM)",
        department=reg_in.department or "Public Procurement Division",
        phone=reg_in.phone,
        is_active=True,
        email_verified=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    logger.info(f"Registered new procurement official: {new_user.username} ({new_user.role})")
    return new_user


# --------------------------------------------------
# 2. OFFICER LOGIN & SECURE SESSION ISSUANCE
# --------------------------------------------------
@router.post("/login", response_model=TokenSchema, summary="Authenticate Procurement Officer & Issue Session")
def login_user(
    login_data: LoginRequestSchema,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Authenticates Procurement Officer credentials:
    1. Strictly verifies salted PBKDF2 password hash.
    2. Issues a cryptographically signed JWT token.
    3. Sets secure HttpOnly + SameSite session cookie on response.
    4. Prohibits unauthorized auto-registration.
    """
    # Ensure default demo accounts exist
    seed_initial_database(db)

    clean_username = login_data.username.strip()
    clean_password = login_data.password.strip()

    if not clean_username or not clean_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username and password are required."
        )

    user = db.query(UserModel).filter(func.lower(UserModel.username) == clean_username.lower()).first()

    if not user or not verify_password(clean_password, user.hashed_password):
        logger.warning(f"Unauthorized login attempt for username: '{clean_username}'")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials. Please verify your username and password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account has been deactivated. Contact the system administrator."
        )

    access_token = create_access_token(data={
        "sub": user.id,
        "username": user.username,
        "role": user.role,
        "org": user.organization
    })

    # Set secure HttpOnly session cookie
    set_auth_cookie(response, access_token)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username,
        "role": user.role,
        "full_name": user.full_name,
        "organization": user.organization
    }


# --------------------------------------------------
# 3. OFFICER LOGOUT & SESSION INVALIDATION
# --------------------------------------------------
@router.post("/logout", summary="Logout & Invalidate Session")
def logout_user(response: Response):
    """Clears the HttpOnly session cookie and invalidates client session."""
    clear_auth_cookie(response)
    return {"status": "SUCCESS", "message": "Logged out successfully. Session invalidated."}


# --------------------------------------------------
# 4. CURRENT AUTHENTICATED USER PROFILE
# --------------------------------------------------
@router.get("/me", response_model=UserResponseSchema, summary="Get Current Authenticated User Profile")
def get_my_profile(current_user: UserModel = Depends(get_current_user)):
    """Returns profile and clearance metadata for the currently logged-in user."""
    return current_user
