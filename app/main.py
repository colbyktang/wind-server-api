from fastapi import FastAPI, HTTPException, Depends, Response, status
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import List
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import datetime, timezone, UTC
from jwt import PyJWTError

from app.auth.auth_models import RefreshToken as RefreshTokenModel
from app.auth.auth_models import RevokedToken as RevokedTokenModel
from app.auth.auth_models import User as UserModel
from app.auth.user import User
from app.auth.refresh_request import RefreshRequest
from app.auth.login import login
from app.auth.register import register
from app.auth.security import require_admin, create_access_token, decode_access_token, get_current_user, hash_token, oauth2_scheme
from app.database import get_db

limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app
app = FastAPI(
    title="Wind Server API",
    description="REST API for managing game servers",
    version="1.0.0"
)


@app.get("/", tags=["root"])
def read_root():
    """Root endpoint with API information"""
    return {
        "name": "Wind Server API",
        "description": "REST API for managing game servers",
        "version": "1.0.0",
        "endpoints": {
            "GET /health": "Checks the health of the API and its dependencies",
            "POST /auth/register": "Register an account",
            "POST /auth/login": "Login endpoint",
        }
    }

@app.get("/health", tags=["root"])
def health_route(response: Response, db: Session = Depends(get_db)):
    """Checks the health of the API and its dependencies"""
    db_status = "ok"
    try:
        db.execute(text("SELECT 1"))
    except (SQLAlchemyError, ConnectionRefusedError):
        db_status = "error"
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    finally:
        if db is not None and db.is_active:
            db.close()

    return {
        "status": "ok" if db_status == "ok" else "error",
        "timestamp": datetime.now(UTC).isoformat() + "Z",
        "dependencies": {
            "database": db_status
        }
    }
        

@app.post("/auth/login", tags=["auth"])
@limiter.limit("5/minute")
def login_route(user: User, db: Session = Depends(get_db)):
    """Login endpoint"""
    login_response = login(user, db)
    return login_response

@app.post("/auth/register", tags=["auth"])
@limiter.limit("5/minute")
def register_route(user: User, db: Session = Depends(get_db)):
    """Register an account"""
    register_response = register(user, db)
    return register_response

@app.post("/auth/refresh", tags=["auth"])
def refresh_route(body: RefreshRequest, db: Session = Depends(get_db)):
    """Exchange a valid refresh token for a new access token."""
    token_hash = hash_token(body.refresh_token)
    db_token = db.query(RefreshTokenModel).filter(
        RefreshTokenModel.token_hash == token_hash,
        RefreshTokenModel.revoked.is_(False),
    ).first()

    if db_token is None or db_token.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token.")
    
    user = db.query(UserModel).filter(UserModel.id == db_token.user_id).first()
    
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")
    
    return {
        "access_token": create_access_token(subject=str(user.username)),
        "token_type": "bearer"
    }

# Performance note: The blocklist DB lookup on every request adds latency. 
# In high-traffic production systems this is usually moved to Redis (in-memory, sub-millisecond).
# Update this in the future
@app.post("/auth/logout", tags=["auth"])
def logout_route(body: RefreshRequest, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """Revoke a refresh token (logout)."""
    token_hash = hash_token(body.refresh_token)
    db_token = db.query(RefreshTokenModel).filter(
        RefreshTokenModel.token_hash == token_hash
    ).first()
    if db_token:
        db_token.revoked = True

    # Blocklist the access token
    try:
        payload = decode_access_token(token)
        jti = payload.get("jti")
        exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        if jti:
            db.add(RevokedTokenModel(jti=jti, expires_at=exp))
    except PyJWTError:
        pass # if it's already invalid, no need to blocklist
    return {"message": "Logged out."}

@app.get("/servers", tags=["servers"])
def list_servers(current_user: str = Depends(get_current_user)):
    # current_user is the username from the token's "sub" claim
    return {"message": f"Hello {current_user}, here are your servers."}