import React, { useState, useRef, useEffect } from 'react'
import { Bot, User, Copy, ThumbsUp, ThumbsDown } from 'lucide-react'
import { Button } from '@/components/atoms/Button'
import { ChatInput } from '@/components/organisms/ChatInput'
import { Badge } from '@/components/atoms/Badge'
import { useAppContext } from '@/contexts/AppContext'
import { QAAPI, SearchAPI } from '@/services/api'
import { CitationSource, ChatMessage } from '@/types'
import {  copyToClipboard, generateSessionId } from '@/utils'

export const QAInterface: React.FC = () => {
  const { state, setError, setSuccess, addMessage } = useAppContext()
  const [question, setQuestion] = useState('')
  const [isAsking, setIsAsking] = useState(false)
  const [sessionId] = useState(() => generateSessionId())
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [state.messages])


  const CitationList: React.FC<{ sources: CitationSource[] }> = ({ sources }) => {
    const [openIndex, setOpenIndex] = useState<number | null>(null)
    const containerRef = useRef<HTMLDivElement>(null)

    useEffect(() => {
      const handleClickOutside = (e: MouseEvent) => {
        if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
          setOpenIndex(null)
        }
      }
      document.addEventListener('mousedown', handleClickOutside)
      return () => document.removeEventListener('mousedown', handleClickOutside)
    }, [])

    return (
      <div ref={containerRef} className="flex flex-wrap gap-2">
        {sources.map((source, index) => (
          <div key={source.chunkId} className="relative">
            <button
              type="button"
              onClick={() => setOpenIndex(openIndex === index ? null : index)}
              className="text-xs inline-flex items-center px-2 py-1 rounded border border-border/50 hover:bg-muted/60 transition"
              aria-label={`Ver cita ${index + 1}`}
            >
              <Badge variant="outline" size="sm" className="mr-2">
                {index + 1}
              </Badge>
              <span className="opacity-75">
                {source.documentTitle}
                {source.pageNumber && ` (Página ${source.pageNumber})`}
              </span>
            </button>
            {openIndex === index && (
              <div className="absolute z-20 mt-2 w-80 p-3 rounded-md border border-border bg-background shadow-lg">
                <div className="mb-1 flex items-center justify-between">
                  <span className="text-xs font-semibold">{source.documentTitle}</span>
                  <span className="text-[10px] opacity-60">
                    {source.pageNumber ? `Pág. ${source.pageNumber}` : 'Sin página'}
                  </span>
                </div>
                {typeof source.lineNumber === 'number' && (
                  <div className="text-[10px] opacity-60 mb-2">Línea {source.lineNumber}</div>
                )}
                <div className="text-xs leading-snug max-h-40 overflow-auto whitespace-pre-wrap">
                  {source.content}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    )
  }


  const handleCopyMessage = async (content: string) => {
    const success = await copyToClipboard(content)
    if (success) {
      setSuccess('Mensaje copiado al portapapeles')
    } else {
      setError({
        code: 'UNKNOWN_ERROR',
        message: 'Error al copiar mensaje',
        timestamp: new Date()
      })
    }
  }

  const renderMessage = (message: ChatMessage) => {
    const isUser = message.type === 'user'
    
    return (
      <div
        key={message.id}
        className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}
      >
        <div className={`flex items-start space-x-3 max-w-[80%] ${isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
            isUser ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground'
          }`}>
            {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
          </div>

          <div className={`rounded-lg px-4 py-3 ${
            isUser 
              ? 'bg-black text-white ml-auto' 
              : 'bg-white border border-gray-200 text-gray-900 shadow-sm mr-auto'
          }`}>
            <div className="prose prose-sm max-w-none">
              <p className={`whitespace-pre-wrap ${isUser ? '' : 'text-gray-900'}`}>{message.content}</p>
            </div>

            {message.sources && message.sources.length > 0 && (
              <div className="mt-3 pt-3 border-t border-border/20">
                <p className="text-xs opacity-75 mb-2">Fuentes:</p>
                <CitationList sources={message.sources} />
              </div>
            )}

            <div className={`flex items-center justify-between mt-3 pt-2 ${isUser ? 'border-white/20' : 'border-gray-200'} border-t`}>
              <span className={`text-xs ${isUser ? 'opacity-80' : 'text-gray-500'}`}>
                {message.timestamp.toLocaleTimeString()}
              </span>
              <div className="flex items-center space-x-1">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleCopyMessage(message.content)}
                  className="h-6 w-6 p-0"
                >
                  <Copy className="w-3 h-3" />
                </Button>
                {!isUser && (
                  <>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-6 w-6 p-0"
                    >
                      <ThumbsUp className="w-3 h-3" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-6 w-6 p-0"
                    >
                      <ThumbsDown className="w-3 h-3" />
                    </Button>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  const handleChatSubmit = (value: string, mode: 'search' | 'reason' = 'reason') => {
    if (!value.trim() || isAsking) return

    const userMessage: ChatMessage = {
      id: `msg-${Date.now()}-user`,
      type: 'user',
      content: value.trim(),
      timestamp: new Date()
    }

    addMessage(userMessage)
    setQuestion('')
    setIsAsking(true)
    setError(null)

    if (mode === 'search') {
      SearchAPI.searchDocuments(value.trim(), {
        limit: 5,
        threshold: 0.3
      }).then(response => {
        const hasResults = response.results?.length > 0
        let searchResultsText = ''
        
        if (hasResults) {
          const resultCount = response.results.length
          const pluralFragments = resultCount !== 1 ? 'fragmentos' : 'fragmento'
          searchResultsText = `Encontré ${resultCount} ${pluralFragments} relevante${resultCount !== 1 ? 's' : ''} en los documentos:\n\n`
          
          response.results.forEach((result, index) => {
            const documentTitle = result.document.title
            const pageInfo = result.chunk.metadata?.pageNumber ? `Página ${result.chunk.metadata.pageNumber}` : 'Sin página'
            const relevancePercentage = (result.similarity * 100).toFixed(1)
            const contentPreview = result.chunk.content.length > 200 
              ? `${result.chunk.content.substring(0, 200)}...`
              : result.chunk.content
            
            searchResultsText += `${index + 1}. ${documentTitle}\n`
            searchResultsText += `   📄 ${pageInfo} | Relevancia: ${relevancePercentage}%\n`
            searchResultsText += `   ${contentPreview}\n\n`
          })
        } else {
          searchResultsText = 'No encontré fragmentos relevantes para tu búsqueda.\n\nSugerencias:\n• Intenta con términos más específicos\n• Usa palabras clave diferentes\n• Verifica que los documentos contengan información relacionada'
        }
    
        const assistantMessage: ChatMessage = {
          id: `msg-${Date.now()}-assistant`,
          type: 'assistant',
          content: searchResultsText,
          timestamp: new Date(),
          sources: hasResults 
            ? response.results.map(result => ({
                documentId: result.document.id,
                documentTitle: result.document.title,
                chunkId: result.chunk.id,
                content: result.chunk.content,
                pageNumber: result.chunk.metadata?.pageNumber,
                lineNumber: result.chunk.metadata?.pageNumber,
                relevanceScore: result.similarity
              }))
            : []
        }
    
        addMessage(assistantMessage)
      }).catch((error: any) => {
        console.error('Search error:', error)
        
        const errorMessage: ChatMessage = {
          id: `msg-${Date.now()}-error`,
          type: 'assistant',
          content: `Lo siento, ocurrió un error durante la búsqueda:\n\n**Error:** ${error.message}\n\nPor favor, intenta nuevamente o contacta al soporte si el problema persiste.`,
          timestamp: new Date()
        }
        
        addMessage(errorMessage)
        setError({
          code: 'SEARCH_ERROR',
          message: `Error en búsqueda: ${error.message}`,
          timestamp: new Date()
        })
      }).finally(() => {
        setIsAsking(false)
      })
    } else {
      QAAPI.askQuestion({
        question: value.trim(),
        sessionId: sessionId
      }).then(response => {
        const assistantMessage: ChatMessage = {
          id: `msg-${Date.now()}-assistant`,
          type: 'assistant',
          content: response.answer,
          timestamp: new Date(),
          sources: response.sources
        }

        addMessage(assistantMessage)
      }).catch((error: any) => {
        console.error('Q&A error:', error)
        const errorMessage: ChatMessage = {
          id: `msg-${Date.now()}-error`,
          type: 'assistant',
          content: `Lo siento, ocurrió un error al procesar tu pregunta: ${error.message}`,
          timestamp: new Date()
        }
        addMessage(errorMessage)
        setError({
          code: 'LLM_ERROR',
          message: `Error en Q&A: ${error.message}`,
          timestamp: new Date()
        })
      }).finally(() => {
        setIsAsking(false)
      })
    }
  }

  return (
    <div>
      {state.messages.length === 0 ? (
        <div className="text-center mb-8">
          <h1 className="text-2xl font-semibold text-gray-900 mb-8">¿Con qué puedo ayudarte?</h1>
          <ChatInput
            value={question}
            onChange={setQuestion}
            onSubmit={handleChatSubmit}
            disabled={isAsking}
            placeholder="Ask anything"
            isLoading={isAsking}
          />
        </div>
      ) : (
        <>
          <div className="space-y-6 mb-8">
            {state.messages.map((message) => (
              <div key={message.id} className={`flex ${message.type === 'user' ? "justify-end" : "justify-start"}`}>
                <div
                  className={`max-w-2xl px-4 py-3 rounded-lg ${
                    message.type === 'user'
                      ? "bg-black text-white"
                      : "bg-white border border-gray-200 text-gray-900 shadow-sm"
                  }`}
                >
                  <p className="text-sm leading-relaxed">{message.content}</p>
                  
                  {message.sources && message.sources.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-gray-200">
                      <p className="text-xs opacity-75 mb-2">Fuentes:</p>
                      <CitationList sources={message.sources} />
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
          <div className="sticky bottom-0">
            <ChatInput
              value={question}
              onChange={setQuestion}
              onSubmit={handleChatSubmit}
              disabled={isAsking}
              placeholder="Ask anything"
              isLoading={isAsking}
            />
          </div>
        </>
      )}
    </div>
  )
}
