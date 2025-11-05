"""
Minimal FastAPI server to test the requests API without AI processing
"""
import sys
import os

# Add current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
    
    # Create FastAPI app
    app = FastAPI(title="Invoice AI - Request Management API")
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Import and include routers
    from api.requests import router as requests_router
    app.include_router(requests_router)
    
    @app.get("/")
    async def root():
        return {
            "message": "Invoice AI Request Management API",
            "status": "running",
            "endpoints": [
                "GET /api/requests/",
                "POST /api/requests/",
                "GET /api/requests/{id}",
                "PATCH /api/requests/{id}/status",
                "GET /api/requests/insights/summary"
            ]
        }
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "service": "request-api"}
    
    if __name__ == "__main__":
        print("Starting Invoice AI Request Management API...")
        print("Available at: http://127.0.0.1:8001")
        uvicorn.run(app, host="127.0.0.1", port=8001, reload=False)
        
except Exception as e:
    print(f"Error starting server: {e}")
    import traceback
    traceback.print_exc()