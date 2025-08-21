'use client'

import React, { createContext, useContext, useReducer, ReactNode } from 'react'
import { Document, ChatMessage, AppError } from '@/types'

interface AppState {
  documents: Document[]
  isLoading: boolean
  error: AppError | null
  success: string | null
  currentSession: string
  messages: ChatMessage[]
}

type AppAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: AppError | null }
  | { type: 'SET_SUCCESS'; payload: string | null }
  | { type: 'SET_DOCUMENTS'; payload: Document[] }
  | { type: 'ADD_DOCUMENT'; payload: Document }
  | { type: 'REMOVE_DOCUMENT'; payload: string }
  | { type: 'ADD_MESSAGE'; payload: ChatMessage }
  | { type: 'SET_MESSAGES'; payload: ChatMessage[] }
  | { type: 'SET_SESSION'; payload: string }
  | { type: 'CLEAR_MESSAGES' }

const initialState: AppState = {
  documents: [],
  isLoading: false,
  error: null,
  success: null,
  currentSession: '',
  messages: []
}

const appReducer = (state: AppState, action: AppAction): AppState => {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload }
    
    case 'SET_ERROR':
      return { ...state, error: action.payload, isLoading: false }
    
    case 'SET_SUCCESS':
      return { ...state, success: action.payload, error: null }
    
    case 'SET_DOCUMENTS':
      return { ...state, documents: action.payload }
    
    case 'ADD_DOCUMENT':
      return { 
        ...state, 
        documents: [...state.documents, action.payload] 
      }
    
    case 'REMOVE_DOCUMENT':
      return {
        ...state,
        documents: state.documents.filter(doc => doc.id !== action.payload)
      }
    
    case 'ADD_MESSAGE':
      return {
        ...state,
        messages: [...state.messages, action.payload]
      }
    
    case 'SET_MESSAGES':
      return { ...state, messages: action.payload }
    
    case 'SET_SESSION':
      return { ...state, currentSession: action.payload }
    
    case 'CLEAR_MESSAGES':
      return { ...state, messages: [] }
    
    default:
      return state
  }
}

interface AppContextType {
  state: AppState
  dispatch: React.Dispatch<AppAction>
  setLoading: (loading: boolean) => void
  setError: (error: AppError | null) => void
  setSuccess: (message: string | null) => void
  addDocument: (document: Document) => void
  removeDocument: (documentId: string) => void
  addMessage: (message: ChatMessage) => void
  clearMessages: () => void
}

const AppContext = createContext<AppContextType | undefined>(undefined)

interface AppProviderProps {
  children: ReactNode
}

export const AppProvider: React.FC<AppProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(appReducer, initialState)

  const setLoading = (loading: boolean) => {
    dispatch({ type: 'SET_LOADING', payload: loading })
  }

  const setError = (error: AppError | null) => {
    dispatch({ type: 'SET_ERROR', payload: error })
  }

  const setSuccess = (message: string | null) => {
    dispatch({ type: 'SET_SUCCESS', payload: message })
  }

  const addDocument = (document: Document) => {
    dispatch({ type: 'ADD_DOCUMENT', payload: document })
  }

  const removeDocument = (documentId: string) => {
    dispatch({ type: 'REMOVE_DOCUMENT', payload: documentId })
  }

  const addMessage = (message: ChatMessage) => {
    dispatch({ type: 'ADD_MESSAGE', payload: message })
  }

  const clearMessages = () => {
    dispatch({ type: 'CLEAR_MESSAGES' })
  }

  const value: AppContextType = {
    state,
    dispatch,
    setLoading,
    setError,
    setSuccess,
    addDocument,
    removeDocument,
    addMessage,
    clearMessages
  }

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  )
}

export const useAppContext = (): AppContextType => {
  const context = useContext(AppContext)
  if (context === undefined) {
    throw new Error('useAppContext must be used within an AppProvider')
  }
  return context
}
