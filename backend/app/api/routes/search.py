

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
import logging
import time

from app.models.schemas import SearchRequest, SearchResponse, SearchResult
from app.services.vertex_rag_service import VertexRAGService
from app.core.exceptions import SearchError

logger = logging.getLogger(__name__)

router = APIRouter()



def get_vertex_rag_service() -> VertexRAGService:
    """Get Vertex AI RAG service dependency"""
    from main import get_vertex_rag_service
    return get_vertex_rag_service()

@router.get("/", response_model=SearchResponse)
@router.get("", response_model=SearchResponse)
async def search_documents(
    q: str = Query(..., min_length=1, max_length=1000, description="Search query"),
    limit: int = Query(5, ge=1, le=20, description="Maximum number of results"),
    threshold: float = Query(0.7, ge=0.0, le=1.0, description="Minimum similarity threshold"),
    document_ids: Optional[str] = Query(None, description="Comma-separated document IDs to filter by"),
    vertex_rag_service: VertexRAGService = Depends(get_vertex_rag_service)
):
   
    try:
        start_time = time.time()
        
        # Parse document_ids if provided
        doc_ids_list = None
        if document_ids:
            doc_ids_list = [doc_id.strip() for doc_id in document_ids.split(",") if doc_id.strip()]
        
        # Search using Vertex AI RAG
        try:
            search_results = await vertex_rag_service.search_documents(
                query=q,
                limit=limit,
                threshold=threshold,
                document_ids=doc_ids_list
            )
        except Exception as e:
            logger.error(f"Vertex AI RAG search failed: {e}")
            raise HTTPException(status_code=500, detail="Search operation failed")
        
        processing_time = time.time() - start_time
        
        # Log search query
        logger.info(f"Vertex AI RAG search query: '{q}' - {len(search_results)} results in {processing_time:.3f}s")
        
        return SearchResponse(
            success=True,
            results=search_results,
            query=q,
            total_results=len(search_results),
            processing_time=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.post("/", response_model=SearchResponse)
@router.post("", response_model=SearchResponse)
async def search_documents_post(
    request: SearchRequest,
    vertex_rag_service: VertexRAGService = Depends(get_vertex_rag_service)
):

    try:
        start_time = time.time()
        
        # Search using Vertex AI RAG
        try:
            search_results = await vertex_rag_service.search_documents(
                query=request.query,
                limit=request.limit,
                threshold=request.threshold,
                document_ids=request.document_ids
            )
        except Exception as e:
            logger.error(f"Vertex AI RAG search failed: {e}")
            raise HTTPException(status_code=500, detail="Search operation failed")
        
        processing_time = time.time() - start_time
        
        # Log search query
        logger.info(f"Vertex AI RAG search query: '{request.query}' - {len(search_results)} results in {processing_time:.3f}s")
        
        return SearchResponse(
            success=True,
            results=search_results,
            query=request.query,
            total_results=len(search_results),
            processing_time=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


