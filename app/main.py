from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from typing import List
from app.models import GameServer, GameServerUpdate
from app.storage import game_server_store

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
            "GET /servers": "List all game servers",
            "GET /servers/{server_id}": "Get a specific game server",
            "POST /servers": "Create a new game server",
            "PUT /servers/{server_id}": "Update a game server",
            "DELETE /servers/{server_id}": "Delete a game server"
        }
    }


@app.get("/servers", response_model=List[GameServer], tags=["servers"])
def list_servers():
    """Get all game servers"""
    servers = game_server_store.get_all_servers()
    return servers


@app.get("/servers/{server_id}", response_model=GameServer, tags=["servers"])
def get_server(server_id: str):
    """Get a specific game server by ID"""
    server = game_server_store.get_server(server_id)
    if not server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Server with ID {server_id} not found"
        )
    return server


@app.post("/servers", response_model=GameServer, status_code=status.HTTP_201_CREATED, tags=["servers"])
def create_server(server: GameServer):
    """Create a new game server"""
    created_server = game_server_store.create_server(server)
    return created_server


@app.put("/servers/{server_id}", response_model=GameServer, tags=["servers"])
def update_server(server_id: str, updates: GameServerUpdate):
    """Update an existing game server"""
    # Convert to dict and filter out None values
    update_data = updates.model_dump(exclude_unset=True)
    
    updated_server = game_server_store.update_server(server_id, update_data)
    if not updated_server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Server with ID {server_id} not found"
        )
    return updated_server


@app.delete("/servers/{server_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["servers"])
def delete_server(server_id: str):
    """Delete a game server"""
    deleted = game_server_store.delete_server(server_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Server with ID {server_id} not found"
        )
    return None


@app.get("/health", tags=["health"])
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "wind-server-api"}
