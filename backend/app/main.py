"""
FastAPI application entry point for Contract Risk Analysis Agent.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.api.routes import health, contracts
from app.utils.logger import setup_logger

# Setup logging
logger = setup_logger(__name__, settings.log_level)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info(f"Starting ContractsConnected API in {settings.environment} mode")
    logger.info(f"OpenAI Model: {settings.openai_model}")
    yield
    # Shutdown
    logger.info("Shutting down ContractsConnected API")


# Create FastAPI app
app = FastAPI(
    title="Contract Risk Analysis Agent API",
    description="AI-powered system for analyzing contract documents and identifying risks",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(health.router)
app.include_router(contracts.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Contract Risk Analysis Agent API",
        "docs": "/docs",
        "health": "/api/v1/health"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc) if settings.environment == "development" else "An error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.environment == "development"
    )
