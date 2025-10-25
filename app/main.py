from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
import redis.asyncio as redis
import aiofiles

from app.core.config import settings
from app.api.v1 import auth, leads
import os

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Lead Management System API"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    # Initialize rate limiter
    redis_client = redis.from_url(settings.redis.url, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis_client)
    
    # Create uploads directory if it doesn't exist
    os.makedirs(settings.storage.upload_dir, exist_ok=True)

# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(leads.router, prefix="/api/v1/leads")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}