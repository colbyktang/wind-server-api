from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session, selectinload
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.auth.auth_models import User as UserModel
from app.auth.security import TokenData, get_current_user
from app.blog.blog_models import Post
from app.blog.blog_schemas import PostCreate, PostResponse, PostUpdate
from app.database import get_db

router = APIRouter(
    prefix="/blog",
    tags=["blog"]
)

limiter = Limiter(key_func=get_remote_address)

@router.post("/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def create_post(
    request: Request,
    body: PostCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    db_user = db.query(UserModel).filter(UserModel.username == current_user.username).first()
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")

    post = Post(
        user_id=db_user.id,
        title=body.title,
        content=body.content,
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


@router.get("/posts", response_model=list[PostResponse])
def list_posts(db: Session = Depends(get_db)):
    posts = (
        db.query(Post)
        .options(selectinload(Post.comments))
        .order_by(Post.created_at.desc())
        .all()
    )
    return posts


@router.get("/posts/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = (
        db.query(Post)
        .options(selectinload(Post.comments))
        .filter(Post.id == post_id)
        .first()
    )
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")
    return post

@router.patch("/posts/{post_id}", response_model=PostResponse)
def patch_post(
    post_id: int,
    body: PostUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    db_user = db.query(UserModel).filter(UserModel.username == current_user.username).first()
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")

    post = (
        db.query(Post)
        .options(selectinload(Post.comments))
        .filter(Post.id == post_id)
        .first()
    )
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")

    if post.user_id != db_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to edit this post.",
        )

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(post, field, value)

    db.commit()
    db.refresh(post)
    return post

@router.delete("/posts/{post_id}", response_model=PostResponse)
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    db_user = db.query(UserModel).filter(UserModel.username == current_user.username).first()
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")

    post = (
        db.query(Post)
        .options(selectinload(Post.comments))
        .filter(Post.id == post_id)
        .first()
    )
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")

    if post.user_id != db_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to delete this post.",
        )

    deleted_post = post
    db.delete(post)
    db.commit()
    return deleted_post