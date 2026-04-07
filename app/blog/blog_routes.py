from fastapi import APIRouter, FastAPI, Request, Response
from slowapi import Limiter
from slowapi.util import get_remote_address
import os

router = APIRouter(
    prefix="/blog",
    tags=["blog"]
)

limiter = Limiter(key_func=get_remote_address)
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:4200").split(",")

@router.post("/blog/posts", tags=["blogs"])
@limiter.limit("5/minute")
def create_post(request: Request):
    return {"created": True}