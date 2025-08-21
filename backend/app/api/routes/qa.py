"""Q&A API routes using LLM-generated responses with citations."""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
import logging
import time
import uuid

from app.models.schemas import QARequest, QAResponse, CitationSource
from app.services.vertex_rag_service import VertexRAGService
from app.core.exceptions import SearchError

logger = logging.getLogger(__name__)

router = APIRouter()



def get_vertex_rag_service() -> VertexRAGService:
    """Get Vertex AI RAG service dependency"""
    from main import get_vertex_rag_service
    return get_vertex_rag_service()

@router.post("/ask", response_model=QAResponse)
@router.post("/ask/", response_model=QAResponse)
async def ask_question(
    request: QARequest,
    vertex_rag_service: VertexRAGService = Depends(get_vertex_rag_service)
):
    """
    Answer natural language questions using Vertex AI RAG Engine
    
    - Uses Vertex AI for semantic search with MemoryCorpus
    - Leverages Gemini Live API for RAG-enhanced responses
    - Returns answers with source citations from grounding chunks
    - Maintains session context in Vertex AI memory store
    """
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        logger.info(f"Processing Vertex AI RAG Q&A request: {request.question[:100]}...")
        
        # Use Vertex AI RAG service for complete Q&A flow
        qa_response = await vertex_rag_service.answer_question(request, session_id)
        
        # Log the Q&A interaction
        logger.info(f"Vertex AI RAG Q&A completed - Question: '{request.question[:50]}...' - "
                   f"Sources: {len(qa_response.sources)} - Time: {qa_response.processing_time:.3f}s")
        
        return qa_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Vertex AI RAG Q&A request failed: {e}")
        import time
        return QAResponse(
            success=False,
            answer="Lo siento, ocurrió un error al procesar tu pregunta. Por favor intenta nuevamente.",
            sources=[],
            confidence=0.0,
            processing_time=0.0,
            session_id=request.session_id or str(uuid.uuid4()),
            error=str(e)
        )

@router.post("/explain")
@router.post("/explain/")
async def explain_answer(
    question: str,
    answer: str,
    sources: List[CitationSource],
    vertex_rag_service: VertexRAGService = Depends(get_vertex_rag_service)
):
    """
    Explain how an answer was derived from sources
    
    - Provides transparency into the Q&A process
    - Shows which parts of sources contributed to the answer
    - Helps users understand the reasoning
    """
    try:
        start_time = time.time()
        
        # Build explanation prompt
        source_texts = [f"Fuente {i+1} ({source.document_title}):\n{source.content}" 
                       for i, source in enumerate(sources)]
        source_context = "\n\n".join(source_texts)
        
        explanation_prompt = f"""Explica cómo se derivó la siguiente respuesta a partir de las fuentes proporcionadas:

PREGUNTA: {question}

RESPUESTA: {answer}

FUENTES UTILIZADAS:
{source_context}

Por favor explica:
1. Qué información específica de cada fuente se utilizó
2. Cómo se combinó la información para formar la respuesta
3. Qué nivel de confianza se puede tener en esta respuesta

EXPLICACIÓN:"""
        
        # Use Vertex AI RAG service for explanation
        explanation_response = await vertex_rag_service.generate_content(
            explanation_prompt,
            max_tokens=1000,
            temperature=0.2
        )
        explanation = explanation_response.text if hasattr(explanation_response, 'text') else str(explanation_response)
        
        processing_time = time.time() - start_time
        
        return {
            "success": True,
            "explanation": explanation,
            "processing_time": processing_time,
            "sources_analyzed": len(sources)
        }
        
    except Exception as e:
        logger.error(f"Failed to generate explanation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate explanation: {str(e)}")

@router.post("/follow-up")
@router.post("/follow-up/")
async def ask_follow_up(
    question: str,
    previous_question: str,
    previous_answer: str,
    previous_sources: List[CitationSource],
    vertex_rag_service: VertexRAGService = Depends(get_vertex_rag_service)
):
    """
    Ask a follow-up question with context from previous Q&A
    
    - Uses previous question and answer as context
    - Can clarify or expand on previous responses
    - Maintains conversation continuity
    """
    try:
        start_time = time.time()
        
        # Build contextual question
        contextual_question = f"""Pregunta anterior: {previous_question}
Respuesta anterior: {previous_answer}

Pregunta de seguimiento: {question}"""
        
        # Create Q&A request with context
        qa_request = QARequest(
            question=contextual_question,
            context=[source.content for source in previous_sources[:3]],  # Use top 3 previous sources
            max_sources=5
        )
        
        # Process the follow-up question using the same endpoint logic
        response = await vertex_rag_service.answer_question(qa_request, session_id=None)
        
        return response
        
    except Exception as e:
        logger.error(f"Failed to process follow-up question: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process follow-up: {str(e)}")


