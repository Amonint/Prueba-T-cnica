"""Document management API routes."""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query, BackgroundTasks
from typing import List, Optional
import tempfile
import os
import logging
from datetime import datetime

from app.models.schemas import (
    DocumentResponse, DocumentListResponse, UploadResponse,
    UploadProgress, Document
)
from app.services.document_service import DocumentService
from app.core.exceptions import DocumentProcessingError, FileValidationError

logger = logging.getLogger(__name__)

router = APIRouter()

def get_document_service() -> DocumentService:
    """Get document service dependency"""
    from main import get_document_service
    return get_document_service()

@router.post("/ingest", response_model=UploadResponse)
@router.post("/ingest/", response_model=UploadResponse)
async def ingest_documents(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    document_service: DocumentService = Depends(get_document_service)
):
    """
    Process and index uploaded documents
    
    - Accepts multiple PDF/TXT files
    - Validates file format and size
    - Extracts text and generates embeddings
    - Stores in vector database for search
    """
    try:
        if not files:
            raise HTTPException(status_code=400, detail="No files provided")
        
        if len(files) > 10:  # Max files limit
            raise HTTPException(status_code=400, detail="Too many files. Maximum 10 files allowed")
        
        successful_docs = []
        errors = []
        
        for file in files:
            try:
                # Create temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as temp_file:
                    # Write uploaded file to temp location
                    content = await file.read()
                    temp_file.write(content)
                    temp_file_path = temp_file.name
                
                # Process document
                document = await document_service.process_document(temp_file_path, file.filename)
                successful_docs.append(document)
                
                # Clean up temp file
                os.unlink(temp_file_path)
                
            except (DocumentProcessingError, FileValidationError) as e:
                errors.append(f"{file.filename}: {str(e)}")
                logger.warning(f"Failed to process {file.filename}: {e}")
                
                # Clean up temp file on error
                if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
            except Exception as e:
                errors.append(f"{file.filename}: Unexpected error - {str(e)}")
                logger.error(f"Unexpected error processing {file.filename}: {e}")
                
                # Clean up temp file on error
                if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
        
        return UploadResponse(
            success=len(successful_docs) > 0,
            documents=successful_docs,
            errors=errors,
            total_uploaded=len(successful_docs),
            total_failed=len(errors)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Document ingestion failed: {str(e)}")

@router.get("/", response_model=DocumentListResponse)
@router.get("", response_model=DocumentListResponse)
async def list_documents(
    skip: int = Query(0, ge=0, description="Number of documents to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of documents to return"),
    document_service: DocumentService = Depends(get_document_service)
):
    """
    List all indexed documents
    
    - Supports pagination with skip/limit
    - Returns document metadata and processing status
    - Sorted by upload date (newest first)
    """
    try:
        documents = await document_service.list_documents(skip=skip, limit=limit)
        total_count = document_service.get_document_count()
        
        return DocumentListResponse(
            success=True,
            documents=documents,
            total=total_count,
            page=skip // limit + 1,
            limit=limit
        )
        
    except Exception as e:
        logger.error(f"Failed to list documents: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")

@router.get("/{document_id}", response_model=DocumentResponse)
@router.get("/{document_id}/", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    document_service: DocumentService = Depends(get_document_service)
):
    """
    Get specific document by ID
    
    - Returns full document metadata
    - Includes processing status and chunk count
    """
    try:
        document = await document_service.get_document(document_id)
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return DocumentResponse(
            success=True,
            data=document,
            message="Document retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get document {document_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get document: {str(e)}")

@router.delete("/{document_id}")
@router.delete("/{document_id}/")
async def delete_document(
    document_id: str,
    document_service: DocumentService = Depends(get_document_service)
):
    """
    Delete document and remove from index
    
    - Removes document and all associated chunks
    - Clears from vector database
    - Cannot be undone
    """
    try:
        # Check if document exists
        document = await document_service.get_document(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Delete document
        success = await document_service.delete_document(document_id)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete document")
        
        return {
            "success": True,
            "message": f"Document '{document.filename}' deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete document {document_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")

"""Removed unused reprocess endpoint to avoid incomplete functionality."""

@router.get("/{document_id}/chunks")
@router.get("/{document_id}/chunks/")
async def get_document_chunks(
    document_id: str,
    document_service: DocumentService = Depends(get_document_service)
):
    """
    Get all chunks for a specific document
    
    - Returns chunked text with metadata
    - Useful for debugging or detailed inspection
    """
    try:
        # Check if document exists
        document = await document_service.get_document(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Get chunks from vector store
        chunks = await document_service.get_document_chunks(document_id)
        
        return {
            "success": True,
            "document_id": document_id,
            "chunks": [
                {
                    "id": chunk.id,
                    "content": chunk.content,
                    "chunk_index": chunk.chunk_index,
                    "page_number": chunk.page_number,
                    "has_embedding": bool(chunk.embedding)
                }
                for chunk in chunks
            ],
            "total_chunks": len(chunks)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get chunks for document {document_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get document chunks: {str(e)}")

@router.get("/stats")
@router.get("/stats/")
async def get_document_stats(
    document_service: DocumentService = Depends(get_document_service)
):
    """
    Get document collection statistics
    
    - Total documents and chunks
    - Storage usage information
    - Processing status summary
    """
    try:
        documents = await document_service.list_documents(skip=0, limit=1000)  # Get all for stats
        # Basic vector stats placeholder (no document_id context here)
        vector_stats = {
            "total_chunks": sum(doc.chunk_count for doc in documents),
            "chunks_with_embeddings": sum(doc.chunk_count for doc in documents),
            "index_health": "healthy" if documents else "empty"
        }
        
        # Calculate statistics
        total_docs = len(documents)
        total_size = sum(doc.size for doc in documents)
        avg_size = total_size / total_docs if total_docs > 0 else 0
        
        # Group by status
        status_counts = {}
        type_counts = {}
        
        for doc in documents:
            status_counts[doc.status] = status_counts.get(doc.status, 0) + 1
            type_counts[doc.type.value] = type_counts.get(doc.type.value, 0) + 1
        
        return {
            "success": True,
            "stats": {
                "documents": {
                    "total": total_docs,
                    "total_size_bytes": total_size,
                    "avg_size_bytes": avg_size,
                    "by_status": status_counts,
                    "by_type": type_counts
                },
                "vector_store": vector_stats,
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get document stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get document stats: {str(e)}")
