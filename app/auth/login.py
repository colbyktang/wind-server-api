from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.auth.auth_models import User as UserModel, RefreshToken
from app.auth.user import User as UserSchema
from app.database import get_db
from app.auth.security import verify_password, create_access_token, create_refresh_token

def login(user: UserSchema, db: Session = Depends(get_db)):
    """
    Handles user login with a username and password
    """
    db_user = db.query(UserModel).filter(UserModel.username == user.username).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or password is incorrect.",
        )
    
    password_match: bool = verify_password(user.password, str(db_user.hashed_password))
    if not password_match:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username or password is incorrect.",
        )
    
    role = "admin" if db_user.is_admin else "user"
    
    raw_token, token_hash, expires_at = create_refresh_token()

    db_refresh = RefreshToken(
        user_id=db_user.id,
        token_hash=token_hash,
        expires_at=expires_at
    )
    db.add(db_refresh)
    db.commit()

    return {
        "access_token": create_access_token(subject=str(db_user.username), role=role),
        "refresh_token": raw_token,  # send the raw token to the client
        "token_type": "bearer",
    }