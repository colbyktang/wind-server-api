import os
import jwt
import bcrypt
import secrets
import hashlib
import uuid
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.auth.auth_models import RevokedToken
from app.database import get_db
from dataclasses import dataclass

# Using os.environ["JWT_SECRET"] (not os.getenv) means the app crashes at startup 
# if the variable is missing — which is the right behaviour.

SECRET_KEY = os.environ["JWT_SECRET"]
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@dataclass
class TokenData:
    username: str
    role: str

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain-text password against a hashed password."""
    encoded = plain_password.encode("utf-8")[:72]
    return bcrypt.checkpw(encoded, hashed_password.encode("utf-8"))

def get_password_hash(password: str) -> str:
    """Hashes a plain-text password. Truncates to 72 bytes per bcrypt's limit."""
    encoded = password.encode("utf-8")[:72]
    return bcrypt.hashpw(encoded, bcrypt.gensalt()).decode("utf-8")

def create_access_token(subject: str, role: str = "user") -> str:
    """Creates a signed JWT."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": subject,   # "subject" — who this token belongs to
        "exp": expire,    # "expiry" — PyJWT enforces this automatically on decode
        "jti": str(uuid.uuid4()),   # unique ID for this token
        "role": role,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict:
    """Decodes and validates a JWT. Raises jwt.PyJWTError on failure."""
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    
def create_refresh_token() -> tuple[str, str, datetime]:
    """
    Returns (raw_token, hashed_token, expiry).
    raw_token is sent to the client. hashed_token is stored in the DB.
    """
    raw = secrets.token_urlsafe(64)
    token_hash = hash_token(raw)
    expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    return raw, token_hash, expires_at

def hash_token(raw: str) -> str:
    """Hashes a raw token for DB lookup."""
    return hashlib.sha256(raw.encode()).hexdigest()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> TokenData:
    try:
        payload = decode_access_token(token)
        jti = payload.get("jti")
        if jti and db.query(RevokedToken).filter(RevokedToken.jti == jti).first():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has been revoked.")
        return TokenData(username=payload["sub"], role=payload.get("role", "user"))
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired.")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token.")
    
def require_admin(current_user: TokenData = Depends(get_current_user)) -> TokenData:
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required.")
    return current_user