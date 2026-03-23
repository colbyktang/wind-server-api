#!/usr/bin/env python3
"""
Wind Server API - Entry Point
Run this script to start the game server management API
"""

from dotenv import load_dotenv
import uvicorn

load_dotenv()

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
