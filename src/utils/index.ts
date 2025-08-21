import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export const cn = (...inputs: ClassValue[]) => {
  return twMerge(clsx(inputs))
}

export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes'
  
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`
}

export const formatDate = (date: Date | string): string => {
  const d = typeof date === 'string' ? new Date(date) : date
  
  return new Intl.DateTimeFormat('es-ES', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(d)
}

export const formatRelativeTime = (date: Date | string): string => {
  const d = typeof date === 'string' ? new Date(date) : date
  const now = new Date()
  const diffInSeconds = Math.floor((now.getTime() - d.getTime()) / 1000)
  
  if (diffInSeconds < 60) {
    return 'hace menos de un minuto'
  }
  
  const diffInMinutes = Math.floor(diffInSeconds / 60)
  if (diffInMinutes < 60) {
    return `hace ${diffInMinutes} minuto${diffInMinutes !== 1 ? 's' : ''}`
  }
  
  const diffInHours = Math.floor(diffInMinutes / 60)
  if (diffInHours < 24) {
    return `hace ${diffInHours} hora${diffInHours !== 1 ? 's' : ''}`
  }
  
  const diffInDays = Math.floor(diffInHours / 24)
  if (diffInDays < 7) {
    return `hace ${diffInDays} día${diffInDays !== 1 ? 's' : ''}`
  }
  
  return formatDate(d)
}

export const validateFile = (file: File, options?: {
  allowedTypes?: string[]
  maxSize?: number
}): { isValid: boolean; errors: string[] } => {
  const errors: string[] = []
  const allowedTypes = options?.allowedTypes || ['pdf', 'txt']
  const maxSize = options?.maxSize || 10 * 1024 * 1024
  
  const extension = file.name.split('.').pop()?.toLowerCase()
  if (!extension || !allowedTypes.includes(extension)) {
    errors.push(`Tipo de archivo no permitido. Permitidos: ${allowedTypes.join(', ')}`)
  }
  
  if (file.size > maxSize) {
    errors.push(`Archivo demasiado grande. Máximo: ${formatFileSize(maxSize)}`)
  }
  
  if (file.size === 0) {
    errors.push('El archivo está vacío')
  }
  
  return {
    isValid: errors.length === 0,
    errors
  }
}

export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: NodeJS.Timeout
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeout)
    timeout = setTimeout(() => func(...args), wait)
  }
}

export const generateId = (): string => {
  return Math.random().toString(36).substr(2, 9)
}

export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text
  return text.substr(0, maxLength) + '...'
}

export const getFileExtension = (filename: string): string => {
  return filename.split('.').pop()?.toLowerCase() || ''
}

export const isPDF = (filename: string): boolean => {
  return getFileExtension(filename) === 'pdf'
}

export const isText = (filename: string): boolean => {
  return getFileExtension(filename) === 'txt'
}

export const formatConfidence = (confidence: number): string => {
  return `${Math.round(confidence * 100)}%`
}

export const formatProcessingTime = (seconds: number): string => {
  if (seconds < 1) {
    return `${Math.round(seconds * 1000)}ms`
  }
  return `${seconds.toFixed(2)}s`
}

export const highlightSearchTerms = (text: string, searchTerm: string): string => {
  if (!searchTerm.trim()) return text
  
  const regex = new RegExp(`(${searchTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi')
  return text.replace(regex, '<mark>$1</mark>')
}

export const getFileIcon = (filename: string): string => {
  const extension = getFileExtension(filename)
  
  switch (extension) {
    case 'pdf':
      return '📄'
    case 'txt':
      return '📝'
    default:
      return '📄'
  }
}

export const calculateReadingTime = (text: string): string => {
  const wordsPerMinute = 200
  const words = text.trim().split(/\s+/).length
  const minutes = Math.ceil(words / wordsPerMinute)
  
  if (minutes < 1) return 'menos de 1 min'
  return `${minutes} min`
}

export const copyToClipboard = async (text: string): Promise<boolean> => {
  try {
    await navigator.clipboard.writeText(text)
    return true
  } catch (error) {
    console.error('Failed to copy to clipboard:', error)
    return false
  }
}

export const downloadTextAsFile = (text: string, filename: string): void => {
  const blob = new Blob([text], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

export const scrollToElement = (elementId: string): void => {
  const element = document.getElementById(elementId)
  if (element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

export const formatSimilarity = (similarity: number): string => {
  return `${Math.round(similarity * 100)}%`
}

export const generateSessionId = (): string => {
  return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}
