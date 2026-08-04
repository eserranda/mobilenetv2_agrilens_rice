"""
app/core/security.py
=====================
Security utilities for password hashing, verification, and HMAC-based signed token authentication.
Does not require any external dependencies like PyJWT or bcrypt.
"""
import hashlib
import hmac
import secrets
import time
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.config import settings
from app.db.session import get_db
from app.models.user import User

# Use bearer token schema for authorization
security_scheme = HTTPBearer(auto_error=False)

# Fallback secret key for token signing
SECRET_KEY = (settings.openai_api_key or "agrilens_default_super_secret_key_1329").encode()


def hash_password(password: str) -> str:
    """Hash password using PBKDF2 with SHA-256 and a random salt."""
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100_000,
    )
    return f"{salt}${key.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against the stored salt and hash."""
    try:
        salt, key_hex = hashed_password.split("$")
        check_key = hashlib.pbkdf2_hmac(
            "sha256",
            plain_password.encode("utf-8"),
            salt.encode("utf-8"),
            100_000,
        )
        return secrets.compare_digest(check_key.hex(), key_hex)
    except Exception:
        return False


def create_access_token(user_id: int, expires_in_seconds: int = 86400 * 7) -> str:
    """Create a signed token containing user_id and expiration timestamp."""
    expiry = int(time.time()) + expires_in_seconds
    payload = f"{user_id}.{expiry}"
    signature = hmac.new(
        SECRET_KEY,
        payload.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    return f"{payload}.{signature}"


def verify_token(token: str) -> Optional[int]:
    """Verify a signed token and return the user_id if valid."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        user_id_str, expiry_str, signature = parts
        
        # Verify expiration
        expiry = int(expiry_str)
        if time.time() > expiry:
            return None
            
        # Recreate signature and verify
        payload = f"{user_id_str}.{expiry_str}"
        expected_sig = hmac.new(
            SECRET_KEY,
            payload.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        
        if secrets.compare_digest(signature, expected_sig):
            return int(user_id_str)
    except Exception:
        pass
    return None


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Dependency to retrieve the logged-in user from the bearer token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token autentikasi tidak valid atau telah kedaluwarsa.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not credentials or credentials.scheme.lower() != "bearer":
        raise credentials_exception
        
    token = credentials.credentials
    user_id = verify_token(token)
    
    if user_id is None:
        raise credentials_exception
        
    # Query user from DB
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
        
    return user


async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to enforce admin access role control."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akses ditolak. Anda memerlukan akses administrator.",
        )
    return current_user
