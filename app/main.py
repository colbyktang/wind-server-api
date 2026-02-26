from fastapi import FastAPI, HTTPException, Depends, Response, status
from fastapi.responses import JSONResponse
from typing import List
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import datetime

from app.auth.user import User
from app.auth.login import login
from app.auth.register import register
from app.database import get_db

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
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "dependencies": {
            "database": db_status
        }
    }
        

@app.post("/auth/login", tags=["auth"])
def login_route(user: User, db: Session = Depends(get_db)):
    """Login endpoint"""
    login_response = login(user, db)
    return login_response

@app.post("/auth/register", tags=["auth"])
def register_route(user: User, db: Session = Depends(get_db)):
    """Register an account"""
    register_response = register(user, db)
    return register_response