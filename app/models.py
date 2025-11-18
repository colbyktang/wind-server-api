from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class GameServer(BaseModel):
    """Model representing a game server"""
    id: Optional[str] = None
    name: str = Field(..., description="Name of the game server")
    game: str = Field(..., description="Type of game (e.g., Minecraft, Counter-Strike)")
    ip_address: str = Field(..., description="IP address of the server")
    port: int = Field(..., description="Port number", ge=1, le=65535)
    max_players: int = Field(..., description="Maximum number of players", ge=1)
    current_players: int = Field(default=0, description="Current number of players", ge=0)
    status: str = Field(default="offline", description="Server status (online/offline/maintenance)")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Epic Minecraft Server",
                "game": "Minecraft",
                "ip_address": "192.168.1.100",
                "port": 25565,
                "max_players": 20,
                "current_players": 5,
                "status": "online"
            }
        }


class GameServerUpdate(BaseModel):
    """Model for updating a game server (all fields optional)"""
    name: Optional[str] = None
    game: Optional[str] = None
    ip_address: Optional[str] = None
    port: Optional[int] = Field(None, ge=1, le=65535)
    max_players: Optional[int] = Field(None, ge=1)
    current_players: Optional[int] = Field(None, ge=0)
    status: Optional[str] = None
