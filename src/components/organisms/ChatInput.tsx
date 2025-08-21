"use client"

import { useState } from "react"
import { Button } from "@/components/atoms/Button"
import { ArrowUp, Mic, X, Check, BrainCircuit, FileSearch2 } from "lucide-react"

interface ChatInputProps {
  value: string
  onChange: (value: string) => void
  onSubmit: (value: string, mode: 'search' | 'reason') => void
  disabled?: boolean
  placeholder?: string
  isLoading?: boolean
}

export const ChatInput: React.FC<ChatInputProps> = ({
  value,
  onChange,
  onSubmit,
  disabled = false,
  placeholder = "Ask anything",
  isLoading = false
}) => {
  const [isRecording, setIsRecording] = useState(false)
  const [selectedMode, setSelectedMode] = useState<'search' | 'reason'>('reason')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (value.trim() && !disabled && !isLoading) {
      onSubmit(value.trim(), selectedMode)
    }
  }

  const handleMicClick = () => {
    setIsRecording(true)
    setTimeout(() => {
      setIsRecording(false)
      onChange("When speech to text feature ?")
    }, 5000)
  }

  const handleCancelRecording = () => {
    setIsRecording(false)
  }

  const handleConfirmRecording = () => {
    setIsRecording(false)
    onChange("When speech to text feature ?")
  }

  return (
    <div className="relative">
      <form onSubmit={handleSubmit} className="relative">
        <div className="border border-gray-200 rounded-2xl p-4 bg-white shadow-sm hover:shadow-md transition-shadow duration-200">
          {isRecording ? (
            <div className="flex items-center justify-between h-12 animate-in fade-in-0 slide-in-from-top-2 duration-500 w-full">
              <div className="flex-1 text-center text-gray-500 text-sm italic">
                Listening...
              </div>
              <div className="flex items-center gap-2 ml-4">
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={handleCancelRecording}
                  className="h-8 w-8 p-0 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-all duration-200"
                >
                  <X className="h-4 w-4" />
                </Button>
                <Button
                  type="button"
                  size="sm"
                  onClick={handleConfirmRecording}
                  className="h-8 w-8 p-0 bg-black hover:bg-gray-800 text-white rounded-lg transition-all duration-200"
                >
                  <Check className="h-4 w-4" />
                </Button>
              </div>
            </div>
          ) : (
            <div className="animate-in fade-in-0 slide-in-from-bottom-2 duration-500">
              <textarea
                value={value}
                onChange={(e) => onChange(e.target.value)}
                placeholder={selectedMode === 'search' ? 'Buscar contenido en documentos...' : placeholder}
                disabled={disabled || isLoading}
                className="w-full bg-transparent text-gray-900 placeholder-gray-500 resize-none border-none outline-none text-base leading-relaxed min-h-[24px] max-h-32 transition-all duration-200"
                rows={1}
                onInput={(e) => {
                  const target = e.target as HTMLTextAreaElement
                  target.style.height = "auto"
                  target.style.height = target.scrollHeight + "px"
                }}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault()
                    handleSubmit(e)
                  }
                }}
              />

              <div className="flex items-center justify-between mt-4">
                <div className="flex items-center gap-2">
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => setSelectedMode('search')}
                    className={`h-8 px-3 rounded-lg transition-all duration-200 text-sm ${
                      selectedMode === 'search'
                        ? 'bg-blue-100 text-blue-700 hover:bg-blue-200'
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                    }`}
                  >
                    <FileSearch2 className="h-4 w-4 mr-1" />
                    Textual Search
                  </Button>

                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => setSelectedMode('reason')}
                    className={`h-8 px-3 rounded-lg transition-all duration-200 text-sm ${
                      selectedMode === 'reason'
                        ? 'bg-blue-100 text-blue-700 hover:bg-blue-200'
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                    }`}
                  >
                    <BrainCircuit className="h-4 w-4 mr-1" />
                    AI Reasoning Search
                  </Button>

                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={handleMicClick}
                    className="h-8 w-8 p-0 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-all duration-200"
                  >
                    <Mic className="h-4 w-4" />
                  </Button>
                </div>

                <Button
                  type="submit"
                  size="sm"
                  disabled={!value.trim() || disabled || isLoading}
                  className="h-8 w-8 p-0 bg-black hover:bg-gray-800 disabled:bg-gray-200 disabled:text-gray-400 text-white rounded-lg transition-all duration-200"
                >
                  <ArrowUp className="h-4 w-4" />
                </Button>
              </div>
            </div>
          )}
        </div>
      </form>
    </div>
  )
}
