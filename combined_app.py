"""
Combined Flask + FastAPI application serving both AI processing and request management
"""
import sys
import os
import uvicorn
import socket
from flask import Flask
from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware

# Add current directory to Python path
sys.path.append(os.path.dirname(__file__))

# Import the existing Flask app
from app import app as flask_app

# Import the FastAPI app
from fastapi_app import fastapi_app

def create_combined_app():
    """Create combined Flask + FastAPI application"""
    
    # Create main FastAPI app - disable automatic docs in production combined app
    main_app = FastAPI(
        title="Invoice AI - Complete System",
        description="Combined AI processing and request management system",
        version="1.0.0",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    
    # Add CORS middleware to handle frontend requests
    from fastapi.middleware.cors import CORSMiddleware
    main_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins for development
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Mount Flask app under /flask for AI processing endpoints
    main_app.mount("/ai", WSGIMiddleware(flask_app))
    
    # Include FastAPI routers for request management
    from api.requests import router as requests_router
    main_app.include_router(requests_router)
    
    @main_app.get("/")
    async def root():
        """Minimal root endpoint"""
        return {"service": "Invoice AI Complete System", "version": "1.0.0"}
    
    @main_app.get("/health")
    async def combined_health():
        """Combined health check"""
        return {
            "status": "healthy",
            "services": {
                "ai_processing": "running",
                "request_management": "running",
                "database": "connected"
            }
        }

    # When mounted, the Flask app's __main__ won't run, so the file-watcher
    # (which is started in app.py when run as __main__) won't be started.
    # Start and stop the file watcher explicitly when the combined FastAPI
    # application starts and stops so incoming-folder processing works.
    @main_app.on_event("startup")
    async def _start_file_watcher():
        try:
            # Import here to avoid circular imports at module import time
            from app import start_file_watcher
            print("Starting Flask file watcher from combined app startup...")
            # start_file_watcher starts a background Observer thread
            start_file_watcher()
        except Exception as e:
            print(f"Warning: failed to start file watcher: {e}")

    @main_app.on_event("shutdown")
    async def _stop_file_watcher():
        try:
            from app import stop_file_watcher
            print("Stopping Flask file watcher from combined app shutdown...")
            stop_file_watcher()
        except Exception as e:
            print(f"Warning: failed to stop file watcher: {e}")

    return main_app


if __name__ == "__main__":
    print("="*80)
    print("Invoice AI Complete System")
    print("="*80)
    print("\nStarting Invoice AI Combined System")
    print("Available components:")
    print("  - AI Processing (Flask) mounted at /ai")
    print("  - Request Management API mounted at /api/requests")
    
    # Create and run the combined app
    app = create_combined_app()
    
    # Initialize database on startup
    print("\nInitializing database...")
    from database import db_manager
    print("✓ Database ready")
    
    print("Starting server (attempting to bind to http://0.0.0.0:8000)")
    print("✓ Press Ctrl+C to stop")
    print("-" * 80)

    # Try to start uvicorn. On Windows, binding to 0.0.0.0:8000 can fail with
    # WinError 10013 (access denied) if the port is in use or OS policy blocks
    # binding. Fall back to localhost and then to an alternate port with clear
    # messages so the process doesn't immediately exit with an unhelpful trace.
    def _run_uvicorn(host: str, port: int):
        print(f"Attempting to run server on http://{host}:{port}")
        uvicorn.run(
            "combined_app:create_combined_app",
            host=host,
            port=port,
            reload=False,
            factory=True
        )

    def _port_available(host: str, port: int, timeout: float = 1.0) -> bool:
        """Check if a TCP port is available for binding on the given host.

        Returns True if binding to (host, port) succeeds (port is free), False otherwise.
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.settimeout(timeout)
                s.bind((host, port))
            return True
        except OSError as e:
            return False

    # Determine which host/port to bind to using a pre-check to avoid WinError 10013
    candidates = [
        ("0.0.0.0", 8000),
        ("127.0.0.1", 8000),
        ("127.0.0.1", 8001),
    ]

    selected = None
    for host, port in candidates:
        if _port_available(host, port):
            selected = (host, port)
            break

    if selected is None:
        print("\n✖ No available binding found for the default ports (8000/8001).")
        print("Useful diagnostics:\n  - Is another process already listening on these ports?\n  - Run: netstat -ano | findstr :8000\n  - If this is a permissions issue, run PowerShell as Administrator or choose a different port.")
        raise RuntimeError("No available port to bind the server")

    host, port = selected
    print(f"Starting server on http://{host}:{port}")
    _run_uvicorn(host, port)