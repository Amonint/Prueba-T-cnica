"""
Pydantic schemas for API requests and responses
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

# Document Schemas
class DocumentType(str, Enum):
    PDF = "pdf"
    TXT = "txt"

class DocumentMetadata(BaseModel):
    filename: str
    size: int
    type: DocumentType
    upload_timestamp: datetime = Field(default_factory=datetime.now)

class DocumentChunk(BaseModel):
    """Document chunk with embedding and metadata"""
    id: str
    content: str
    page_number: Optional[int] = None
    chunk_index: Optional[int] = None
    embedding: Optional[List[float]] = None
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Rich metadata including filename, pageNumber, chunkIndex, chunkType, wordCount, charCount, documentId, documentTitle, documentType, uploadDate, embeddingModel, embeddingDimension"
    )

class Document(BaseModel):
    id: str
    filename: str
    title: str
    content: str
    type: DocumentType
    size: int
    uploaded_at: datetime
    processed_at: Optional[datetime] = None
    chunk_count: int = 0
    status: str = "pending"  # pending, processing, completed, error

class DocumentResponse(BaseModel):
    success: bool
    data: Optional[Document] = None
    message: str = ""
    error: Optional[str] = None

class DocumentListResponse(BaseModel):
    success: bool
    documents: List[Document] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    limit: int = 10

# Search Schemas
class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    limit: int = Field(default=5, ge=1, le=20)
    threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    document_ids: Optional[List[str]] = None

class SearchResult(BaseModel):
    chunk: DocumentChunk
    document: Document
    similarity: float
    relevance_score: float

class SearchResponse(BaseModel):
    success: bool
    results: List[SearchResult] = Field(default_factory=list)
    query: str
    total_results: int = 0
    processing_time: float = 0.0
    error: Optional[str] = None

# Q&A Schemas
class QARequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    context: Optional[List[str]] = None
    session_id: Optional[str] = None
    document_ids: Optional[List[str]] = None
    max_sources: int = Field(default=5, ge=1, le=10)

class CitationSource(BaseModel):
    document_id: str
    document_title: str
    chunk_id: str
    content: str
    page_number: Optional[int] = None
    line_number: Optional[int] = None
    relevance_score: float

class QAResponse(BaseModel):
    success: bool = True
    answer: str
    sources: List[CitationSource] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    processing_time: float = 0.0
    session_id: str
    error: Optional[str] = None

# Upload Schemas
class UploadProgress(BaseModel):
    filename: str
    progress: float = Field(ge=0.0, le=100.0)
    status: str  # pending, uploading, processing, completed, error
    message: str = ""
    error: Optional[str] = None

class FileValidationResult(BaseModel):
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    file_info: Optional[Dict[str, Any]] = None

class UploadResponse(BaseModel):
    success: bool
    documents: List[Document] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    total_uploaded: int = 0
    total_failed: int = 0

# Chat Schemas
class ChatMessage(BaseModel):
    id: str
    type: str  # user, assistant
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    sources: Optional[List[CitationSource]] = None
    session_id: str

class ChatSession(BaseModel):
    id: str
    messages: List[ChatMessage] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    document_ids: List[str] = Field(default_factory=list)

# Health Check Schema
class HealthResponse(BaseModel):
    status: str
    timestamp: datetime = Field(default_factory=datetime.now)
    services: Dict[str, str] = Field(default_factory=dict)
    version: str = "1.0.0"

# Error Schema
class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    code: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)

# Statistics Schema
class DocumentStats(BaseModel):
    total_documents: int = 0
    total_chunks: int = 0
    total_size_bytes: int = 0
    avg_document_size: float = 0.0
    document_types: Dict[str, int] = Field(default_factory=dict)

class SystemStats(BaseModel):
    documents: DocumentStats
    queries_total: int = 0
    searches_total: int = 0
    uptime_seconds: float = 0.0
    memory_usage_mb: float = 0.0
