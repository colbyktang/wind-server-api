# Wind Server API

A Python REST API for managing game servers. Built with FastAPI, this API provides endpoints to create, read, update, and delete game server configurations.

## Features

- Manage multiple game servers
- Fast and modern REST API built with FastAPI
- Automatic interactive API documentation (Swagger UI)
- Data validation with Pydantic
- In-memory storage for server data

## Requirements

- Python 3.8+
- [uv](https://github.com/astral-sh/uv)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/colbyktang/wind-server-api.git
cd wind-server-api
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
uv pip install -r requirements.txt
```

## Usage

### Starting the API Server

Run the API server using the included script:

```bash
python run.py
```

Or use uvicorn directly:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### Interactive API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Root
- `GET /` - API information and available endpoints
- `GET /health` - Health check endpoint

### Game Servers
- `GET /servers` - List all game servers
- `GET /servers/{server_id}` - Get a specific game server
- `POST /servers` - Create a new game server
- `PUT /servers/{server_id}` - Update a game server
- `DELETE /servers/{server_id}` - Delete a game server

## Example Usage

### Create a Game Server

```bash
curl -X POST "http://localhost:8000/servers" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Epic Minecraft Server",
    "game": "Minecraft",
    "ip_address": "192.168.1.100",
    "port": 25565,
    "max_players": 20,
    "current_players": 5,
    "status": "online"
  }'
```

### List All Servers

```bash
curl -X GET "http://localhost:8000/servers"
```

### Get a Specific Server

```bash
curl -X GET "http://localhost:8000/servers/{server_id}"
```

### Update a Server

```bash
curl -X PUT "http://localhost:8000/servers/{server_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "current_players": 10,
    "status": "online"
  }'
```

### Delete a Server

```bash
curl -X DELETE "http://localhost:8000/servers/{server_id}"
```

## Game Server Model

Each game server has the following properties:

- `id` (string, auto-generated): Unique identifier
- `name` (string, required): Name of the game server
- `game` (string, required): Type of game (e.g., Minecraft, Counter-Strike)
- `ip_address` (string, required): IP address of the server
- `port` (integer, required): Port number (1-65535)
- `max_players` (integer, required): Maximum number of players
- `current_players` (integer, default: 0): Current number of players
- `status` (string, default: "offline"): Server status (online/offline/maintenance)
- `created_at` (datetime, auto-generated): Creation timestamp
- `updated_at` (datetime, auto-generated): Last update timestamp

## Development

The project structure:

```
wind-server-api/
├── app/
│   ├── __init__.py
│   ├── main.py       # FastAPI application and routes
│   ├── models.py     # Pydantic models
│   └── storage.py    # In-memory data storage
├── requirements.txt  # Python dependencies
├── run.py           # Application entry point
└── README.md        # This file
```

## License

Personal project for managing game servers.
