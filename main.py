"""
Main FastAPI application for the Nonprofit CRM.

This application provides REST API endpoints for managing constituents,
contributions, interactions, opportunities, and generating personalized
fundraising messages using Claude AI.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config import settings
from models import init_db
from api.routes import message


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    Handles startup and shutdown events.
    """
    # Startup: Initialize database
    init_db(settings.database_url)
    print(f"✓ Database initialized: {settings.database_url}")
    print(f"✓ Using Claude model: {settings.anthropic_model}")

    yield

    # Shutdown: Cleanup if needed
    print("Shutting down...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="""
    Nonprofit CRM API with AI-powered fundraising message generation.

    ## Features

    * **Constituent Management**: Manage donors, volunteers, and supporters
    * **Fundraising Messages**: Generate personalized outreach using Claude AI
    * **Campaign Tracking**: Monitor contributions and campaign performance
    * **Relationship Management**: Track interactions and opportunities

    ## Message Generation

    The message generation endpoint (`POST /api/constituents/{id}/message`) uses
    Claude AI to create tailored fundraising messages based on:

    - Individual donor history and giving patterns
    - Campaign context and organizational messaging
    - Donor segment characteristics
    - Customizable tone and length preferences

    ## Authentication

    Currently, this API does not require authentication. In production, you should
    implement proper authentication and authorization mechanisms.
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    message.router,
    prefix=settings.api_prefix,
    tags=["Messages"]
)


@app.get("/")
async def root():
    """Root endpoint providing API information."""
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "description": "Nonprofit CRM API with AI-powered message generation",
        "docs": "/docs",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "timestamp": "2025-01-15T00:00:00Z"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )
