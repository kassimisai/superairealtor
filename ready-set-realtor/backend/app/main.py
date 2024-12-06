from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from .api import auth, leads, communications, documents
from .core.config import settings

load_dotenv()

app = FastAPI(
    title="Ready Set Realtor API",
    description="AI-driven platform for real estate professionals",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(leads.router)
app.include_router(communications.router)
app.include_router(documents.router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Ready Set Realtor API",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    } 