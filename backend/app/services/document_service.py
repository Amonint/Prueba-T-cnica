"""
Document processing service
Handles file upload, text extraction, chunking, and embedding generation
"""

import os
import uuid
import magic
import PyPDF2
import aiofiles
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime
import asyncio
import tempfile

from app.core.config import get_settings
from app.core.exceptions import DocumentProcessingError, FileValidationError
from app.models.schemas import (
    Document, DocumentChunk, DocumentType, FileValidationResult,
    UploadProgress, DocumentResponse
)
from app.services.vertex_rag_service import VertexRAGService

logger = logging.getLogger(__name__)

class DocumentService:
    """Document processing service"""
    
    def __init__(self, vertex_rag_service: VertexRAGService):
        """Initialize document service
        
        Args:
            vertex_rag_service: Vertex AI RAG service for document processing and search
        """
        self.vertex_rag_service = vertex_rag_service
        self.settings = get_settings()
        self.documents: Dict[str, Document] = {}
        
        # Ensure documents directory exists
        os.makedirs(self.settings.documents_path, exist_ok=True)
        
        logger.info("Document service initialized with Vertex AI RAG Engine")
    
    async def validate_file(self, file_path: str, filename: str) -> FileValidationResult:
        """Validate uploaded file
        
        Args:
            file_path: Path to uploaded file
            filename: Original filename
            
        Returns:
            Validation result
        """
        errors = []
        warnings = []
        file_info = {}
        
        try:
            # Check file exists
            if not os.path.exists(file_path):
                errors.append("File does not exist")
                return FileValidationResult(is_valid=False, errors=errors)
            
            # Get file info
            file_size = os.path.getsize(file_path)
            file_info["size"] = file_size
            file_info["filename"] = filename
            
            # Check file size
            if file_size > self.settings.max_file_size:
                errors.append(f"File size ({file_size} bytes) exceeds maximum allowed ({self.settings.max_file_size} bytes)")
            
            if file_size == 0:
                errors.append("File is empty")
            
            # Check file extension
            file_ext = filename.lower().split('.')[-1] if '.' in filename else ""
            if file_ext not in self.settings.allowed_extensions:
                errors.append(f"File extension '{file_ext}' not allowed. Allowed: {', '.join(self.settings.allowed_extensions)}")
            
            file_info["extension"] = file_ext
            
            # Check file type using magic
            try:
                file_type = magic.from_file(file_path, mime=True)
                file_info["mime_type"] = file_type
                
                # Validate mime type matches extension
                if file_ext == "pdf" and not file_type.startswith("application/pdf"):
                    warnings.append("File extension suggests PDF but MIME type doesn't match")
                elif file_ext == "txt" and not file_type.startswith("text/"):
                    warnings.append("File extension suggests text but MIME type doesn't match")
                    
            except Exception as e:
                warnings.append(f"Could not determine file type: {e}")
            
            # Additional PDF validation
            if file_ext == "pdf":
                try:
                    with open(file_path, 'rb') as f:
                        pdf_reader = PyPDF2.PdfReader(f)
                        num_pages = len(pdf_reader.pages)
                        file_info["pages"] = num_pages
                        
                        if num_pages == 0:
                            errors.append("PDF has no pages")
                        elif num_pages > 100:
                            warnings.append(f"PDF has {num_pages} pages, processing may take time")
                            
                except Exception as e:
                    errors.append(f"Invalid PDF file: {e}")
            
            is_valid = len(errors) == 0
            
            return FileValidationResult(
                is_valid=is_valid,
                errors=errors,
                warnings=warnings,
                file_info=file_info
            )
            
        except Exception as e:
            logger.error(f"File validation error: {e}")
            return FileValidationResult(
                is_valid=False,
                errors=[f"Validation error: {e}"]
            )
    
    async def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text
        """
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text.strip():
                            text += f"\n\n--- Page {page_num + 1} ---\n{page_text}"
                    except Exception as e:
                        logger.warning(f"Failed to extract text from page {page_num + 1}: {e}")
                        continue
            
            if not text.strip():
                raise DocumentProcessingError("No text could be extracted from PDF")
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"PDF text extraction failed: {e}")
            raise DocumentProcessingError(f"Failed to extract text from PDF: {e}")
    
    async def extract_text_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file
        
        Args:
            file_path: Path to TXT file
            
        Returns:
            File content
        """
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
                content = await file.read()
            
            if not content.strip():
                raise DocumentProcessingError("Text file is empty")
            
            return content.strip()
            
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                async with aiofiles.open(file_path, 'r', encoding='latin-1') as file:
                    content = await file.read()
                return content.strip()
            except Exception as e:
                raise DocumentProcessingError(f"Failed to read text file with encoding: {e}")
                
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            raise DocumentProcessingError(f"Failed to extract text from file: {e}")
    
    async def chunk_document(self, text: str, filename: str) -> List[DocumentChunk]:
        """Create semantically coherent chunks preserving sentence boundaries."""
        chunks = []
        current_chunk = ""
        current_page = 1
        chunk_index = 0
        
        # Split text into sentences (preserve sentence boundaries)
        sentences = []
        lines = text.split('\n')
        
        for line in lines:
            if line.startswith('--- Page'):
                # Extract page number
                try:
                    page_match = line.split()
                    if len(page_match) >= 3:
                        current_page = int(page_match[2])
                except (ValueError, IndexError):
                    current_page += 1
                continue
            
            # Split line into sentences (handle multiple sentence endings)
            line_sentences = []
            current_sentence = ""
            
            for char in line:
                current_sentence += char
                if char in '.!?':
                    if current_sentence.strip():
                        line_sentences.append(current_sentence.strip())
                    current_sentence = ""
            
            # Add remaining text as sentence if not empty
            if current_sentence.strip():
                line_sentences.append(current_sentence.strip())
            
            sentences.extend(line_sentences)
        
        # Create chunks preserving sentence boundaries
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Check if adding this sentence would exceed chunk size
            # Use 1024 tokens as recommended by Pinecone (approximately 4000 characters)
            if len(current_chunk) + len(sentence) > 4000:
                if current_chunk:
                    # Create chunk with rich metadata
                    chunk = DocumentChunk(
                        id=f"{filename}_chunk_{chunk_index}",
                        content=current_chunk.strip(),
                        page_number=current_page,
                        chunk_index=chunk_index,
                        metadata={
                            "filename": filename,
                            "pageNumber": current_page,
                            "chunkIndex": chunk_index,
                            "chunkType": "text",
                            "wordCount": len(current_chunk.split()),
                            "charCount": len(current_chunk)
                        }
                    )
                    chunks.append(chunk)
                    chunk_index += 1
                
                # Start new chunk
                current_chunk = sentence + " "
            else:
                current_chunk += sentence + " "
        
        # Add final chunk if not empty
        if current_chunk.strip():
            chunk = DocumentChunk(
                id=f"{filename}_chunk_{chunk_index}",
                content=current_chunk.strip(),
                page_number=current_page,
                chunk_index=chunk_index,
                metadata={
                    "filename": filename,
                    "pageNumber": current_page,
                    "chunkIndex": chunk_index,
                    "chunkType": "text",
                    "wordCount": len(current_chunk.split()),
                    "charCount": len(current_chunk)
                }
            )
            chunks.append(chunk)
        
        logger.info(f"Created {len(chunks)} semantically coherent chunks for {filename}")
        return chunks
    
    async def process_document(self, file_path: str, filename: str) -> Document:
        """Process uploaded document
        
        Args:
            file_path: Path to uploaded file
            filename: Original filename
            
        Returns:
            Processed document
        """
        try:
            logger.info(f"Processing document: {filename}")
            
            # Validate file
            validation = await self.validate_file(file_path, filename)
            if not validation.is_valid:
                raise FileValidationError(f"File validation failed: {', '.join(validation.errors)}")
            
            # Determine document type
            file_ext = filename.lower().split('.')[-1]
            doc_type = DocumentType.PDF if file_ext == "pdf" else DocumentType.TXT
            
            # Extract text
            if doc_type == DocumentType.PDF:
                text_content = await self.extract_text_from_pdf(file_path)
            else:
                text_content = await self.extract_text_from_txt(file_path)
            
            # Create document
            doc_id = str(uuid.uuid4())
            title = filename.rsplit('.', 1)[0]  # Remove extension
            
            document = Document(
                id=doc_id,
                filename=filename,
                title=title,
                content=text_content,
                type=doc_type,
                size=validation.file_info.get("size", 0),
                uploaded_at=datetime.now(),
                status="processing"
            )
            
            # Chunk document
            chunk_data = await self.chunk_document(text_content, filename)
            chunks = []
            
            # Validate chunks before processing
            for chunk in chunk_data:
                if not chunk.content or len(chunk.content.strip()) < 10:
                    logger.warning(f"Skipping chunk {chunk.id} - content too short or empty")
                    continue
                
                # Ensure chunk has valid metadata
                if not chunk.metadata:
                    chunk.metadata = {}
                
                # Validate page number
                if chunk.page_number is None or chunk.page_number < 1:
                    chunk.page_number = 1
                
                chunks.append(chunk)
            
            if not chunks:
                raise DocumentProcessingError("No valid chunks generated from document")
            
            logger.info(f"Generated {len(chunks)} valid chunks for {filename}")
            
            # Store in Vertex AI RAG corpus
            await self.vertex_rag_service.add_document_to_corpus(document, chunks)
            
            # Update document
            document.chunk_count = len(chunks)
            document.processed_at = datetime.now()
            document.status = "completed"
            
            # Store document
            self.documents[doc_id] = document
            
            # Save document content to file for persistence
            doc_file_path = os.path.join(self.settings.documents_path, f"{doc_id}.json")
            try:
                import json
                async with aiofiles.open(doc_file_path, 'w', encoding='utf-8') as f:
                    doc_dict = document.dict()
                    doc_dict['uploaded_at'] = doc_dict['uploaded_at'].isoformat()
                    if doc_dict['processed_at']:
                        doc_dict['processed_at'] = doc_dict['processed_at'].isoformat()
                    await f.write(json.dumps(doc_dict, ensure_ascii=False, indent=2))
            except Exception as e:
                logger.warning(f"Failed to save document metadata: {e}")
            
            logger.info(f"Document processed successfully: {filename} ({len(chunks)} chunks)")
            return document
            
        except Exception as e:
            logger.error(f"Document processing failed: {e}")
            if isinstance(e, (DocumentProcessingError, FileValidationError)):
                raise
            raise DocumentProcessingError(f"Failed to process document: {e}")
    
    async def get_document(self, document_id: str) -> Optional[Document]:
        """Get document by ID
        
        Args:
            document_id: Document ID
            
        Returns:
            Document if found
        """
        return self.documents.get(document_id)
    
    async def list_documents(self, skip: int = 0, limit: int = 10) -> List[Document]:
        """List all documents
        
        Args:
            skip: Number of documents to skip
            limit: Maximum number of documents to return
            
        Returns:
            List of documents
        """
        docs = list(self.documents.values())
        docs.sort(key=lambda x: x.uploaded_at, reverse=True)
        return docs[skip:skip + limit]
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete document and its chunks
        
        Args:
            document_id: Document ID
            
        Returns:
            True if deleted successfully
        """
        try:
            # Note: With Vertex AI RAG, document deletion from corpus requires additional API calls
            # For now, we remove from local storage and let Vertex AI handle corpus cleanup
            
            # Remove from documents
            if document_id in self.documents:
                del self.documents[document_id]
            
            # Remove document file
            doc_file_path = os.path.join(self.settings.documents_path, f"{document_id}.json")
            if os.path.exists(doc_file_path):
                os.remove(doc_file_path)
            
            logger.info(f"Document deleted from local storage: {document_id}")
            logger.warning("Document may still exist in Vertex AI RAG corpus. Manual cleanup may be required.")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete document {document_id}: {e}")
            return False
    
    def get_document_count(self) -> int:
        """Get total number of documents"""
        return len(self.documents)
