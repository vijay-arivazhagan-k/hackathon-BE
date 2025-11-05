"""
Simple test server to verify the API endpoints work
"""
import sys
import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add current directory to Python path
sys.path.append(os.path.dirname(__file__))

# Create a simple FastAPI app for testing
app = FastAPI(title="Test Invoice AI API")

# Add CORS middleware with very permissive settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include the requests router
try:
    from api.requests import router as requests_router
    app.include_router(requests_router)
    print("✓ Successfully imported requests router")
except Exception as e:
    print(f"✗ Failed to import requests router: {e}")

@app.get("/")
async def root():
    return {"message": "Test API Server", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    print("Starting test API server...")
    print("Available at: http://127.0.0.1:8001")
    
    try:
        uvicorn.run(app, host="127.0.0.1", port=8001, reload=False)
    except Exception as e:
        print(f"Failed to start server: {e}")
        # Try alternative port
        print("Trying port 8000...")
        uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)