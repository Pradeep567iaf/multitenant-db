from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Optional
from .config import settings

# Use Argon2 for password hashing (more secure than bcrypt, no 72-byte limit)
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password using Argon2."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password using Argon2."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None, is_superadmin: bool = False) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # Use different secret keys for superadmin and tenant
    secret_key = settings.SECRET_KEY_SUPERADMIN if is_superadmin else settings.SECRET_KEY_TENANT
    
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str, is_superadmin: bool = False) -> Optional[dict]:
    """Decode a JWT access token."""
    try:
        secret_key = settings.SECRET_KEY_SUPERADMIN if is_superadmin else settings.SECRET_KEY_TENANT
        payload = jwt.decode(token, secret_key, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
