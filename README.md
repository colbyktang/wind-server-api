# Wind Server API

A Python REST API for managing game servers. Built with FastAPI, SQLAlchemy, and SQLite.

## Features

- User registration and login with bcrypt password hashing
- JWT-ready authentication structure
- Health check endpoint with database connectivity status
- Interactive API documentation via Swagger UI
- Data validation with Pydantic
- SQLite database with SQLAlchemy ORM

## Requirements

- Python 3.11+
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
- `GET /health` - Health check with database connectivity status

### Auth
- `POST /auth/register` - Register a new user account
- `POST /auth/login` - Login with username and password

## Example Usage

### Register a User

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "myuser",
    "password": "mypassword"
  }'
```

### Login

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "myuser",
    "password": "mypassword"
  }'
```

### Health Check

```bash
curl -X GET "http://localhost:8000/health"
```

## User Model

Each user has the following properties:

- `id` (integer, auto-generated) - Unique identifier
- `username` (string, unique, required) - Username, max 50 characters
- `hashed_password` (string) - bcrypt-hashed password
- `is_admin` (boolean, default: false) - Admin flag
- `vault_policy` (string, optional) - Vault policy assignment
- `created_at` (datetime, auto-generated) - Account creation timestamp
- `last_login` (datetime, nullable) - Last login timestamp

## License

Personal project for managing game servers.