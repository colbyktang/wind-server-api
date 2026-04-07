from fastapi import FastAPI, Depends, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import datetime, UTC
from starlette.middleware.base import BaseHTTPMiddleware
import os

from app.auth.security import get_current_user
from app.auth.auth_routes import router as auth_router
from app.blog.blog_routes import router as blog_router
from app.database import get_db

allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:4200").split(",")

# Create FastAPI app
app = FastAPI(
    title="Wind Server API",
    description="REST API for managing game servers",
    version="1.0.0"
)

app.include_router(blog_router)
app.include_router(auth_router)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Strict-Transport-Security"] = "max-age=31536000"
        return response
    
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

@app.get("/servers", tags=["servers"])
def list_servers(current_user: str = Depends(get_current_user)):
    # current_user is the username from the token's "sub" claim
    return {"message": f"Hello {current_user}, here are your servers."}