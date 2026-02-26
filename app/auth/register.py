from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.auth.auth_models import User as UserModel
from app.auth.user import User as UserSchema
from app.database import get_db
from app.auth.security import get_password_hash

def register(user: UserSchema, db: Session = Depends(get_db)):
    """
    Handles user registration, including password hashing and database storage.
    """
    # Check if user already exists
    existing_user = db.query(UserModel).filter(UserModel.username == user.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    # Hash the password
    hashed_password = get_password_hash(user.password)

    db_user = UserModel(
        username = user.username,
        hashed_password=hashed_password
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return {"message": f"User {user.username} registered successfully."}