from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.auth.auth_models import User as UserModel
from app.auth.user import User as UserSchema
from app.database import get_db
from app.auth.security import verify_password

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

    return {"message": "Login successful."}