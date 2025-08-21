import React from 'react'
import { cn } from '@/utils'

interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string
  error?: string
  resizable?: boolean
}

export const Textarea: React.FC<TextareaProps> = ({
  className,
  label,
  error,
  resizable = true,
  id,
  ...props
}) => {
  const generatedId = React.useId()
  const textareaId = id || `textarea-${generatedId}`

  return (
    <div className="space-y-2">
      {label && (
        <label 
          htmlFor={textareaId}
          className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
        >
          {label}
        </label>
      )}
      
      <textarea
        id={textareaId}
        className={cn(
          'textarea',
          !resizable && 'resize-none',
          error && 'border-destructive focus-visible:ring-destructive',
          className
        )}
        {...props}
      />
      
      {error && (
        <p className="text-sm text-destructive">
          {error}
        </p>
      )}
    </div>
  )
}
