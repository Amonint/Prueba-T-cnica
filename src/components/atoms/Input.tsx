import React from 'react'
import { cn } from '@/utils'

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  leftIcon?: React.ReactNode
  rightIcon?: React.ReactNode
}

export const Input: React.FC<InputProps> = ({
  className,
  label,
  error,
  leftIcon,
  rightIcon,
  id,
  ...props
}) => {
  const generatedId = React.useId()
  const inputId = id || `input-${generatedId}`

  return (
    <div className="space-y-2">
      {label && (
        <label 
          htmlFor={inputId}
          className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
        >
          {label}
        </label>
      )}
      
      <div className="relative">
        {leftIcon && (
          <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground">
            {leftIcon}
          </div>
        )}
        
        <input
          id={inputId}
          className={cn(
            'input',
            leftIcon && 'pl-10',
            rightIcon && 'pr-10',
            error && 'border-destructive focus-visible:ring-destructive',
            className
          )}
          {...props}
        />
        
        {rightIcon && (
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground">
            {rightIcon}
          </div>
        )}
      </div>
      
      {error && (
        <p className="text-sm text-destructive">
          {error}
        </p>
      )}
    </div>
  )
}
