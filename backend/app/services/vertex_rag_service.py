
import asyncio
import logging
import time
from typing import List, Optional, Dict
from datetime import datetime

from google import genai
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import get_settings
from app.core.exceptions import SearchError
from app.models.schemas import (
    Document,
    DocumentChunk,
    QARequest,
    QAResponse,
    CitationSource,
    SearchResult,
)

logger = logging.getLogger(__name__)


class VertexRAGService:
    """RAG service using Google GenAI with API Key only (no ADC required)"""

    def __init__(self):
        self.settings = get_settings()

        # Initialize Google GenAI client with API Key
        self.client = genai.Client(api_key=self.settings.google_api_key)

        # Simple in-memory stores
        self.documents: Dict[str, Document] = {}
        self.chunks_by_document: Dict[str, List[DocumentChunk]] = {}

        # Compatibility attribute for health checks
        self.memory_corpus = None

        logger.info(
            f"Initialized API-Key RAG service - Model: {self.settings.gemini_model}"
        )

    async def initialize_memory_corpus(self) -> None:
        """No-op initialization for API Key mode."""
        logger.info("Memory corpus initialized (API Key mode, in-memory store)")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
    async def generate_embedding(self, text: str, title: str = None, task_type: str = "RETRIEVAL_DOCUMENT") -> List[float]:
        """Generate embedding using Google GenAI embeddings API with task-specific optimization"""
        try:
            # Try different method signatures based on the SDK version
            try:
                # Method 1: Using embed_content with taskType for better retrieval
                response = await asyncio.to_thread(
                    self.client.embed_content,
                    model=self.settings.embedding_model,
                    content=text
                )
            except (AttributeError, TypeError) as e1:
                logger.debug(f"Method 1 failed: {e1}, trying method 2")
                try:
                    # Method 2: Using models.embed_content with contents
                    response = await asyncio.to_thread(
                        self.client.models.embed_content,
                        model=self.settings.embedding_model,
                        contents=text,
                    )
                except (AttributeError, TypeError) as e2:
                    logger.debug(f"Method 2 failed: {e2}, trying method 3")
                    # Method 3: Using embed method with different structure
                    response = await asyncio.to_thread(
                        self.client.embed,
                        model=self.settings.embedding_model,
                        contents=[text],
                    )
            
            # Debug logging
            logger.debug(f"Embedding response type: {type(response)}")
            logger.debug(f"Embedding response attributes: {dir(response) if hasattr(response, '__dict__') else 'N/A'}")
            
            # Handle EmbedContentResponse format based on logs
            # Response structure: embeddings=[ContentEmbedding(values=[...]), ...]
            if hasattr(response, 'embeddings') and response.embeddings:
                # Get first embedding from the list
                first_embedding = response.embeddings[0]
                if hasattr(first_embedding, 'values'):
                    return list(first_embedding.values)
            
            # Fallback: Handle other possible formats
            if hasattr(response, 'embedding'):
                embedding_obj = response.embedding
                if hasattr(embedding_obj, 'values'):
                    return list(embedding_obj.values)
                elif isinstance(embedding_obj, list):
                    return embedding_obj
            
            if isinstance(response, dict):
                if 'embeddings' in response and response['embeddings']:
                    first_emb = response['embeddings'][0]
                    if isinstance(first_emb, dict) and 'values' in first_emb:
                        return first_emb['values']
                if 'embedding' in response:
                    emb = response['embedding']
                    if isinstance(emb, dict) and 'values' in emb:
                        return emb['values']
                    elif isinstance(emb, list):
                        return emb
                if 'values' in response:
                    return response['values']
            
            if isinstance(response, list):
                return response
                
            logger.error(f"Unexpected embedding response format: {type(response)} - {response}")
            raise ValueError(f"Unexpected embedding response format: {type(response)}")
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise SearchError(f"Failed to generate embedding: {e}")

    async def add_document_to_corpus(self, document: Document, chunks: List[DocumentChunk]) -> bool:
        """Store document and chunk embeddings in-memory with enriched metadata."""
        try:
            self.documents[document.id] = document

            enriched_chunks: List[DocumentChunk] = []
            for chunk in chunks:
                try:
                    # Generate embedding with document title for better retrieval
                    chunk.embedding = await self.generate_embedding(
                        text=chunk.content,
                        title=document.title,
                        task_type="RETRIEVAL_DOCUMENT"
                    )
                    
                    # Enrich metadata with document information
                    if not chunk.metadata:
                        chunk.metadata = {}
                    
                    chunk.metadata.update({
                        "documentId": document.id,
                        "documentTitle": document.title,
                        "documentType": document.type.value,
                        "uploadDate": document.uploaded_at.isoformat() if document.uploaded_at else None,
                        "embeddingModel": self.settings.embedding_model,
                        "embeddingDimension": len(chunk.embedding) if chunk.embedding else 0
                    })
                    
                except Exception as e:
                    logger.error(f"Failed to generate embedding for chunk {chunk.id}: {e}")
                    # Don't add chunks without embeddings to avoid search issues
                    continue
                enriched_chunks.append(chunk)

            self.chunks_by_document[document.id] = enriched_chunks
            logger.info(
                f"Added document {document.id} with {len(enriched_chunks)} chunks to in-memory corpus"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to add document to corpus: {e}")
            return False

    async def search_documents(
        self,
        query: str,
        limit: int = 5,
        threshold: float = None,  # Use config default if not specified
        document_ids: Optional[List[str]] = None,
    ) -> List[SearchResult]:
        """Semantic search over in-memory chunk embeddings with improved precision."""
        try:
            # Use configured threshold if not specified
            if threshold is None:
                from app.core.config import get_settings
                settings = get_settings()
                threshold = settings.similarity_threshold
            
            query_embedding = await self.generate_embedding(
                text=query,
                title="Search query",
                task_type="RETRIEVAL_DOCUMENT"
            )
            logger.debug(f"Generated query embedding for: '{query}' (length: {len(query_embedding)})")

            results: List[SearchResult] = []
            total_chunks = 0
            similarities = []
            
            for doc_id, chunks in self.chunks_by_document.items():
                if document_ids and doc_id not in document_ids:
                    continue

                document = self.documents.get(doc_id)
                if not document:
                    continue

                for chunk in chunks:
                    total_chunks += 1
                    if not chunk.embedding:
                        logger.warning(f"Chunk {chunk.id} has no embedding")
                        continue
                    
                    similarity = self._cosine_similarity(query_embedding, chunk.embedding)
                    similarities.append(similarity)
                    logger.debug(f"Chunk similarity: {similarity:.4f} for content: '{chunk.content[:100]}...'")
                    
                    if similarity >= threshold:
                        results.append(
                            SearchResult(
                                chunk=chunk,
                                document=document,
                                similarity=similarity,
                                relevance_score=similarity,
                            )
                        )

            logger.info(f"Search stats - Total chunks: {total_chunks}, Results above {threshold}: {len(results)}")
            if similarities:
                logger.info(f"Similarity range: {min(similarities):.4f} - {max(similarities):.4f}")

            # Sort by relevance and return top results
            results.sort(key=lambda r: r.similarity, reverse=True)
            return results[:limit]
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise SearchError(f"Search failed: {e}")

    async def answer_question(
        self, request: QARequest, session_id: Optional[str] = None
    ) -> QAResponse:
        """RAG answer using local semantic search + Gemini generation."""
        start = time.time()
        try:
            search_results = await self.search_documents(
                query=request.question, limit=request.max_sources, threshold=None  # Use configured threshold
            )

            citation_sources: List[CitationSource] = []
            for result in search_results:
                # Prefer explicit line_number from metadata if available
                line_number = None
                try:
                    if isinstance(result.chunk.metadata, dict):
                        line_number = result.chunk.metadata.get("line_number")
                except Exception:
                    line_number = None

                citation_sources.append(
                    CitationSource(
                        document_id=result.document.id,
                        document_title=result.document.title,
                        chunk_id=result.chunk.id,
                        content=result.chunk.content,
                        page_number=result.chunk.page_number,
                        line_number=line_number,
                        relevance_score=result.relevance_score,
                    )
                )

            context_text = "\n\n".join(
                [f"Source {i+1} ({r.document.title}, página {r.chunk.page_number}):\n{r.chunk.content}" 
                 for i, r in enumerate(search_results)]
            )
            
            prompt = f"""Eres un asistente especializado en análisis de documentos y CVs.
Debes responder de manera clara, concisa y profesional.

CONTEXTO DEL DOCUMENTO:
{context_text}

PREGUNTA DEL USUARIO: {request.question}

INSTRUCCIONES ESPECÍFICAS:
1. Responde de manera directa y concisa
2. Destaca información clave con **negritas**
3. Incluye citas de fuentes al final de cada sección relevante
4. Mantén un tono profesional y objetivo
6. NO uses emojis ni elementos decorativos
7. NO ofrezcas servicios irrelevantes

FORMATO DE RESPUESTA:
- Usa encabezados ## para secciones principales
- Usa listas con viñetas para enumerar información
- Destaca datos importantes con **negritas**
- Incluye citas de fuentes al final de cada sección
- Mantén un formato limpio y profesional

RESPUESTA:"""

            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.settings.gemini_model,
                contents=prompt,
            )
            
            # Handle response text extraction
            answer_text = None
            if hasattr(response, "text"):
                answer_text = response.text
            elif hasattr(response, "candidates") and response.candidates:
                # Handle structured response with candidates
                candidate = response.candidates[0]
                if hasattr(candidate, "content") and hasattr(candidate.content, "parts"):
                    parts = candidate.content.parts
                    if parts and hasattr(parts[0], "text"):
                        answer_text = parts[0].text
            elif isinstance(response, dict):
                answer_text = response.get("text")
            
            if not answer_text:
                answer_text = "No se pudo generar una respuesta."

            duration = time.time() - start
            confidence = min(len(citation_sources) / 3, 1.0) * 0.9

            return QAResponse(
                success=True,
                answer=answer_text,
                sources=citation_sources,
                confidence=confidence,
                processing_time=duration,
                session_id=session_id or "default",
            )
        except Exception as e:
            logger.error(f"Q&A failed: {e}")
            return QAResponse(
                success=False,
                answer="Lo siento, ocurrió un error al procesar tu pregunta. Por favor intenta nuevamente.",
                sources=[],
                confidence=0.0,
                processing_time=time.time() - start if "start" in locals() else 0.0,
                session_id=session_id or "default",
                error=str(e),
            )

    async def test_connection(self) -> bool:
        """Ping Gemini model using API Key."""
        try:
            resp = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.settings.gemini_model,
                contents="Test connection",
            )
            
            # Check if we got a valid response
            if hasattr(resp, "text") and resp.text:
                return True
            elif hasattr(resp, "candidates") and resp.candidates:
                return True
            elif isinstance(resp, dict) and resp.get("text"):
                return True
            
            return False
        except Exception as e:
            logger.error(f"GenAI test failed: {e}")
            return False

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        try:
            import numpy as np

            a = np.array(vec1)
            b = np.array(vec2)
            denom = (np.linalg.norm(a) * np.linalg.norm(b))
            if denom == 0:
                return 0.0
            return float(np.dot(a, b) / denom)
        except Exception as e:
            logger.error(f"Cosine similarity failed: {e}")
            return 0.0
