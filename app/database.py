from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.auth.auth_models import Base

# Create SQLite Database file
DATABASE_URL = "sqlite:///./wind_server.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables
Base.metadata.create_all(bind=engine)

# Dependency to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()