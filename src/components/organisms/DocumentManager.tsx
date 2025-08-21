import React, { useState, useEffect } from 'react'
import { Trash2, FileText } from 'lucide-react'
import { Button } from '@/components/atoms/Button'
import { useAppContext } from '@/contexts/AppContext'
import { DocumentAPI } from '@/services/api'
import { Document } from '@/types'
import { formatFileSize } from '@/utils'

export const DocumentManager: React.FC = () => {
  const { state, setLoading, setError, setSuccess, dispatch } = useAppContext()
  const [searchQuery, setSearchQuery] = useState('')
  const [filteredDocuments, setFilteredDocuments] = useState<Document[]>([])
  const [sortBy, setSortBy] = useState<'name' | 'date' | 'size'>('date')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')

  useEffect(() => {
    loadDocuments()
  }, [])

  useEffect(() => {
    filterAndSortDocuments()
  }, [state.documents, searchQuery, sortBy, sortOrder])

  const loadDocuments = async () => {
    setLoading(true)
    try {
      const response = await DocumentAPI.getDocuments(0, 100)
      if (response.success) {
        dispatch({ type: 'SET_DOCUMENTS', payload: response.documents })
      }
    } catch (error: any) {
      setError({
        code: 'NETWORK_ERROR',
        message: `Error al cargar documentos: ${error.message}`,
        timestamp: new Date()
      })
    } finally {
      setLoading(false)
    }
  }

  const filterAndSortDocuments = () => {
    let filtered = [...state.documents]

    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(doc =>
        doc.title.toLowerCase().includes(query) ||
        doc.filename.toLowerCase().includes(query)
      )
    }

    filtered.sort((a, b) => {
      let comparison = 0
      switch (sortBy) {
        case 'name':
          comparison = a.title.localeCompare(b.title)
          break
        case 'date':
          comparison = new Date(a.uploadedAt).getTime() - new Date(b.uploadedAt).getTime()
          break
        case 'size':
          comparison = a.size - b.size
          break
      }
      return sortOrder === 'asc' ? comparison : -comparison
    })

    setFilteredDocuments(filtered)
  }

  const handleDeleteDocument = async (document: Document) => {
    if (!confirm(`¿Estás seguro de que quieres eliminar "${document.title}"?`)) return

    setLoading(true)
    try {
      await DocumentAPI.deleteDocument(document.id)
      dispatch({ type: 'REMOVE_DOCUMENT', payload: document.id })
      setSuccess(`Documento "${document.title}" eliminado exitosamente`)
    } catch (error: any) {
      setError({
        code: 'NETWORK_ERROR',
        message: `Error al eliminar documento: ${error.message}`,
        timestamp: new Date()
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h3 className="text-sm font-medium text-gray-900 mb-3">
        Documents ({state.documents.length})
      </h3>

      {state.documents.length === 0 ? (
        <div className="text-center py-8">
          <FileText className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p className="text-sm text-gray-500">No documents uploaded yet</p>
          <p className="text-xs text-gray-400 mt-1">Upload PDF or TXT files to get started</p>
        </div>
      ) : (
        <div className="space-y-2">
          {state.documents.map((doc) => (
            <div
              key={doc.id}
              className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <FileText className="w-4 h-4 text-gray-500 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">{doc.title}</p>
                <p className="text-xs text-gray-500">{formatFileSize(doc.size)}</p>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => handleDeleteDocument(doc)}
                className="h-6 w-6 p-0 text-gray-400 hover:text-red-500"
              >
                <Trash2 className="w-3 h-3" />
              </Button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
