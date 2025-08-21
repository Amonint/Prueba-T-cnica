"""Main FastAPI application for Mini Asistente Q&A."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from typing import Optional
import os
import logging

from app.core.config import get_settings
from app.core.exceptions import setup_exception_handlers
from app.api.routes import documents, search, qa
from app.services.document_service import DocumentService
from app.services.vertex_rag_service import VertexRAGService
from app.core.logging import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Global service instances
document_service: Optional[DocumentService] = None
vertex_rag_service: Optional[VertexRAGService] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    global document_service, vertex_rag_service
    
    settings = get_settings()
    logger.info("Starting Mini Asistente Q&A API with Vertex AI RAG Engine...")
    
    try:
        # Initialize Vertex AI RAG service
        vertex_rag_service = VertexRAGService()
        
        # Initialize memory corpus for persistent context storage
        await vertex_rag_service.initialize_memory_corpus()
        
        # Test connection to Vertex AI
        connection_ok = await vertex_rag_service.test_connection()
        if not connection_ok:
            logger.warning("Vertex AI connection test failed, but continuing...")
        
        # Initialize document service with Vertex AI RAG
        document_service = DocumentService(
            vertex_rag_service=vertex_rag_service
        )
        
        # Create necessary directories
        os.makedirs(settings.documents_path, exist_ok=True)
        os.makedirs(settings.vector_store_path, exist_ok=True)
        
        logger.info("Services initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Mini Asistente Q&A API...")

# Create FastAPI app
app = FastAPI(
    title="Mini Asistente Q&A API",
    description="Modular document Q&A system with local PDF processing and Gemini API integration",
    version="1.0.0",
    lifespan=lifespan,
    redirect_slashes=False
)

# Setup CORS from settings
settings = get_settings()
allowed_origins = {"http://localhost:3000", settings.frontend_url}
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(allowed_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup exception handlers
setup_exception_handlers(app)

# Include routers
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(qa.router, prefix="/api/qa", tags=["qa"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Mini Asistente Q&A API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check if services are initialized
        if not all([document_service, vertex_rag_service]):
            raise HTTPException(status_code=503, detail="Services not initialized")
        
        # Test Vertex AI RAG service connection
        connection_ok = await vertex_rag_service.test_connection()
        
        return {
            "status": "healthy",
            "services": {
                "document_service": "ok",
                "vertex_rag_service": "ok" if connection_ok else "warning",
                "memory_corpus": "ok" if vertex_rag_service.memory_corpus else "not_initialized"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

# Dependency injection helpers
def get_document_service() -> DocumentService:
    """Get document service instance"""
    if document_service is None:
        raise HTTPException(status_code=503, detail="Document service not initialized")
    return document_service

def get_vertex_rag_service() -> VertexRAGService:
    """Get Vertex AI RAG service instance"""
    if vertex_rag_service is None:
        raise HTTPException(status_code=503, detail="Vertex AI RAG service not initialized")
    return vertex_rag_service

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
