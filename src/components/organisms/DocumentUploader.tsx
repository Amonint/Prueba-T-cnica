import React, { useState } from 'react'
import { Upload } from 'lucide-react'
import { useAppContext } from '@/contexts/AppContext'
import { DocumentAPI } from '@/services/api'


interface UploadedFile {
  file: File
  status: 'pending' | 'uploading' | 'completed' | 'error'
  error?: string
}

export const DocumentUploader: React.FC = () => {
  const { setLoading, setError, setSuccess, addDocument } = useAppContext()
  const [selectedFiles, setSelectedFiles] = useState<UploadedFile[]>([])
  const [isUploading, setIsUploading] = useState(false)

  const handleFilesSelected = async (files: File[]) => {
    const uploadFiles = files.map(file => ({
      file,
      status: 'uploading' as const
    }))
    setSelectedFiles(prev => [...prev, ...uploadFiles])
    await uploadDocuments(uploadFiles)
  }

  const uploadDocuments = async (filesToUpload?: UploadedFile[]) => {
    const files = filesToUpload || selectedFiles
    if (files.length === 0) return

    setIsUploading(true)
    setLoading(true)
    setError(null)

    try {
      const fileObjects = files.map(item => item.file)
      const response = await DocumentAPI.uploadDocuments(fileObjects)

      if (response.success) {
        response.documents.forEach((doc: any) => addDocument(doc))

        if (response.total_uploaded > 0) {
          setSuccess(`${response.total_uploaded} documento(s) procesado(s) exitosamente`)
          setSelectedFiles([])
        }

        if (response.total_failed > 0) {
          setError({
            message: `${response.total_failed} documento(s) fallaron: ${response.errors.join(', ')}`,
            code: 'UPLOAD_PARTIAL_FAILURE',
            timestamp: new Date()
          })
        }
      } else {
        throw new Error('Error en la respuesta del servidor')
      }
    } catch (error: any) {
      console.error('Upload error:', error)
      setError({
        message: `Error al subir documentos: ${error.message}`,
        code: 'UPLOAD_ERROR',
        timestamp: new Date()
      })
      setSelectedFiles([])
    } finally {
      setIsUploading(false)
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <div
        className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
          isUploading ? 'border-blue-400 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
        }`}
        onDrop={(e) => {
          e.preventDefault()
          const files = Array.from(e.dataTransfer.files)
          handleFilesSelected(files)
        }}
        onDragOver={(e) => e.preventDefault()}
        onDragLeave={(e) => e.preventDefault()}
      >
        <Upload className="w-8 h-8 text-gray-400 mx-auto mb-2" />
        <p className="text-sm text-gray-600 mb-2">Drop PDF or TXT files here</p>
        <p className="text-xs text-gray-500">or click to browse</p>
        <input
          type="file"
          multiple
          accept=".pdf,.txt"
          onChange={(e) => {
            if (e.target.files) {
              const files = Array.from(e.target.files)
              handleFilesSelected(files)
            }
          }}
          className="hidden"
          id="file-upload"
        />
        <label htmlFor="file-upload" className="cursor-pointer">
          <div className="w-full h-full absolute inset-0" />
        </label>
      </div>
    </div>
  )
}
