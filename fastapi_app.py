"""
FastAPI application for request management APIs
"""
import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))

from api.requests import router as requests_router

# Create FastAPI app
fastapi_app = FastAPI(
    title="Invoice AI - Request Management API",
    description="REST API for managing invoice requests alongside AI processing",
    version="1.0.0"
)

# Add CORS middleware
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
fastapi_app.include_router(requests_router)

@fastapi_app.get("/")
async def root():
    """Root endpoint for API documentation"""
    return {
        "message": "Invoice AI Request Management API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@fastapi_app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "request-api"}