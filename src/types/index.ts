export interface Document {
  id: string;
  filename: string;
  title: string;
  content: string;
  type: 'pdf' | 'txt';
  size: number;
  uploadedAt: Date;
  chunks: DocumentChunk[];
}

export interface DocumentChunk {
  id: string;
  documentId: string;
  content: string;
  embedding: number[];
  metadata: ChunkMetadata;
}

export interface ChunkMetadata {
  pageNumber?: number;
  startIndex: number;
  endIndex: number;
  chunkIndex: number;
}

export interface SearchQuery {
  query: string;
  limit?: number;
  threshold?: number;
}

export interface SearchResult {
  chunk: DocumentChunk;
  document: Document;
  similarity: number;
  relevanceScore: number;
}

export interface SearchResponse {
  results: SearchResult[];
  query: string;
  totalResults: number;
  processingTime: number;
}

export interface QARequest {
  question: string;
  context?: string[];
  sessionId?: string;
}

export interface QAResponse {
  answer: string;
  sources: CitationSource[];
  confidence: number;
  processingTime: number;
  sessionId: string;
}

export interface CitationSource {
  documentId: string;
  documentTitle: string;
  chunkId: string;
  content: string;
  pageNumber?: number;
  lineNumber?: number;
  relevanceScore: number;
}

export interface UploadProgress {
  filename: string;
  progress: number;
  status: 'pending' | 'uploading' | 'processing' | 'completed' | 'error';
  error?: string;
}

export interface FileValidation {
  isValid: boolean;
  errors: string[];
  warnings: string[];
}

export interface UIState {
  isLoading: boolean;
  error: string | null;
  success: string | null;
}

export interface ChatMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sources?: CitationSource[];
  isTyping?: boolean;
}

export interface ChatSession {
  id: string;
  messages: ChatMessage[];
  createdAt: Date;
  updatedAt: Date;
}

export interface EmbeddingService {
  generateEmbedding(text: string): Promise<number[]>;
  generateEmbeddings(texts: string[]): Promise<number[][]>;
}

export interface LLMService {
  generateResponse(prompt: string, context?: string[]): Promise<string>;
  generateEmbedding(text: string): Promise<number[]>;
}

export interface DocumentService {
  processDocument(file: File): Promise<Document>;
  extractText(file: File): Promise<string>;
  chunkDocument(content: string, metadata: any): Promise<DocumentChunk[]>;
}

export interface VectorStoreService {
  addDocuments(documents: DocumentChunk[]): Promise<void>;
  search(query: number[], limit?: number, threshold?: number): Promise<SearchResult[]>;
  deleteDocument(documentId: string): Promise<void>;
  getDocumentChunks(documentId: string): Promise<DocumentChunk[]>;
}

export interface AppConfig {
  googleApiKey: string;
  geminiModel: string;
  embeddingModel: string;
  maxFileSize: number;
  allowedExtensions: string[];
  maxFiles: number;
  vectorStorePath: string;
  documentsPath: string;
}

export interface APIResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> extends APIResponse<T[]> {
  total: number;
  page: number;
  limit: number;
  hasNext: boolean;
  hasPrev: boolean;
}

export interface AppError {
  code: string;
  message: string;
  details?: any;
  timestamp: Date;
}

export type ErrorCode = 
  | 'UPLOAD_ERROR'
  | 'PROCESSING_ERROR'
  | 'SEARCH_ERROR'
  | 'LLM_ERROR'
  | 'VALIDATION_ERROR'
  | 'NETWORK_ERROR'
  | 'UNKNOWN_ERROR';
