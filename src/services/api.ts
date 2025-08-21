import axios, { AxiosResponse } from 'axios'
import { 
  Document, 
  SearchResponse, 
  QAResponse, 
  QARequest, 
  APIResponse
} from '@/types'

// Prefer direct backend URL in the browser to avoid rewrite redirect loops.
// Fallbacks:
// - In browser on localhost, call backend at http://localhost:8000 directly (CORS enabled)
// - In server (Node) inside Docker, use service name
const getBaseURL = () => {
  if (typeof window !== 'undefined') {
    const origin = window.location.origin
    // Local dev in browser
    if (origin.includes('http://localhost:3000') || origin.includes('http://127.0.0.1:3000')) {
      return 'http://localhost:8000'
    }
    // Default to relative for other deployments (nginx/proxy setups)
    return ''
  }
  // Server-side: use Docker service in production, localhost in dev
  const isProduction = process.env.NODE_ENV === 'production'
  return isProduction ? 'http://backend:8000' : 'http://localhost:8000'
}

const api = axios.create({
  baseURL: getBaseURL(),
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => {
    console.error('API Request Error:', error)
    return Promise.reject(error)
  }
)

api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message)
    
    const errorMessage = error.response?.data?.error || 
                        error.response?.data?.detail || 
                        error.message || 
                        'An unexpected error occurred'
    
    return Promise.reject(new Error(errorMessage))
  }
)

export class DocumentAPI {
  static async uploadDocuments(files: File[]): Promise<any> {
    const formData = new FormData()
    files.forEach(file => {
      formData.append('files', file)
    })

    const response = await api.post('/api/documents/ingest', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 60000,
    })

    return response.data
  }

  static async getDocuments(skip = 0, limit = 10): Promise<any> {
    const response = await api.get('/api/documents', {
      params: { skip, limit }
    })
    return response.data
  }

  static async getDocument(documentId: string): Promise<Document> {
    const response = await api.get<APIResponse<Document>>(`/api/documents/${documentId}`)
    
    if (!response.data.success || !response.data.data) {
      throw new Error('Document not found')
    }
    
    return response.data.data
  }

  static async deleteDocument(documentId: string): Promise<void> {
    await api.delete(`/api/documents/${documentId}`)
  }

  static async getDocumentStats(): Promise<any> {
    const response = await api.get('/api/documents/stats')
    return response.data
  }

  static async getDocumentChunks(documentId: string): Promise<any> {
    const response = await api.get(`/api/documents/${documentId}/chunks`)
    return response.data
  }
}

export class SearchAPI {
  static async searchDocuments(query: string, options?: {
    limit?: number
    threshold?: number
    documentIds?: string[]
  }): Promise<SearchResponse> {
    const params = new URLSearchParams({
      q: query,
      limit: options?.limit?.toString() || '5',
      threshold: options?.threshold?.toString() || '0.7'
    })

    if (options?.documentIds?.length) {
      params.append('document_ids', options.documentIds.join(','))
    }

    const response = await api.get<SearchResponse>(`/api/search?${params}`)
    return response.data
  }

  static async searchDocumentsPost(request: any): Promise<SearchResponse> {
    const response = await api.post<SearchResponse>('/api/search', request)
    return response.data
  }

  static async findSimilarChunks(chunkId: string, limit = 3, threshold = 0.8): Promise<any> {
    const response = await api.get(`/api/search/similar/${chunkId}`, {
      params: { limit, threshold }
    })
    return response.data
  }

  static async getSearchSuggestions(query: string, limit = 5): Promise<any> {
    const response = await api.get('/api/search/suggest', {
      params: { q: query, limit }
    })
    return response.data
  }

  static async getSearchStats(): Promise<any> {
    const response = await api.get('/api/search/stats')
    return response.data
  }
}

export class QAAPI {
  static async askQuestion(request: QARequest): Promise<QAResponse> {
    const response = await api.post<QAResponse>('/api/qa/ask', request, {
      timeout: 45000,
    })
    return response.data
  }

  static async explainAnswer(
    question: string, 
    answer: string, 
    sources: any[]
  ): Promise<any> {
    const response = await api.post('/api/qa/explain', {
      question,
      answer,
      sources
    })
    return response.data
  }

  static async askFollowUp(
    question: string,
    previousQuestion: string,
    previousAnswer: string,
    previousSources: any[]
  ): Promise<QAResponse> {
    const response = await api.post<QAResponse>('/api/qa/follow-up', {
      question,
      previous_question: previousQuestion,
      previous_answer: previousAnswer,
      previous_sources: previousSources
    })
    return response.data
  }

  static async getQuestionSuggestions(): Promise<any> {
    const response = await api.get('/api/qa/suggestions')
    return response.data
  }

  static async getQAHistory(sessionId: string, limit = 10): Promise<any> {
    const response = await api.get(`/api/qa/history/${sessionId}`, {
      params: { limit }
    })
    return response.data
  }

  static async getQAStats(): Promise<any> {
    const response = await api.get('/api/qa/stats')
    return response.data
  }
}

export class HealthAPI {
  static async checkHealth(): Promise<any> {
    const response = await api.get('/api/health')
    return response.data
  }

  static async getInfo(): Promise<any> {
    const response = await api.get('/')
    return response.data
  }
}

export { api }
