from typing import Dict
from datetime import datetime
from app.models import GameServer
import uuid


class GameServerStore:
    """In-memory storage for game servers"""
    
    def __init__(self):
        self.servers: Dict[str, GameServer] = {}
    
    def create_server(self, server: GameServer) -> GameServer:
        """Create a new game server"""
        server.id = str(uuid.uuid4())
        server.created_at = datetime.utcnow()
        server.updated_at = datetime.utcnow()
        self.servers[server.id] = server
        return server
    
    def get_server(self, server_id: str) -> GameServer:
        """Get a server by ID"""
        return self.servers.get(server_id)
    
    def get_all_servers(self) -> list[GameServer]:
        """Get all servers"""
        return list(self.servers.values())
    
    def update_server(self, server_id: str, updates: dict) -> GameServer:
        """Update a server"""
        server = self.servers.get(server_id)
        if not server:
            return None
        
        # Update fields
        for key, value in updates.items():
            if value is not None and hasattr(server, key):
                setattr(server, key, value)
        
        server.updated_at = datetime.utcnow()
        return server
    
    def delete_server(self, server_id: str) -> bool:
        """Delete a server"""
        if server_id in self.servers:
            del self.servers[server_id]
            return True
        return False


# Global store instance
game_server_store = GameServerStore()
