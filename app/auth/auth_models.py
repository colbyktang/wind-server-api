from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, index=True)
    hashed_password = Column(String(100))  # Still hash passwords
    is_admin = Column(Boolean, default=False)
    vault_policy = Column(String(100))     # Vault policy assignment
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

class GameServer(Base):
    __tablename__ = "game_servers"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    game = Column(String, nullable=False)
    ip_address = Column(String, nullable=False)
    port = Column(Integer, nullable=False)
    # Vault secret paths
    rcon_secret_path = Column(String)      # vault:secret/servers/mc1/rcon
    api_secret_path = Column(String)       # vault:secret/servers/mc1/api
    created_at = Column(DateTime, default=datetime.utcnow)