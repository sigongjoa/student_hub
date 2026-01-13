"""
FastAPI Server for Chat API

대화형 채팅 API 서버 (SSE Streaming 지원)
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import chat

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Node 0 Student Hub - Chat API",
    description="대화형 AI 어시스턴트 API (Ollama + MCP Tools)",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(chat.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Node 0 Student Hub - Chat API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "ollama_url": "http://localhost:11434"
    }


if __name__ == "__main__":
    import uvicorn

    logger.info(f"🚀 Starting FastAPI server on port {settings.API_PORT}...")
    uvicorn.run(
        "app.api_server:app",
        host="0.0.0.0",
        port=settings.API_PORT,
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    )
