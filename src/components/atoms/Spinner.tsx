import React from 'react'
import { cn } from '@/utils'

interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

export const Spinner: React.FC<SpinnerProps> = ({
  size = 'md',
  className
}) => {
  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8'
  }

  return (
    <div
      className={cn(
        'animate-spin rounded-full border-2 border-current border-r-transparent',
        sizes[size],
        className
      )}
      role="status"
      aria-label="Cargando"
    >
      <span className="sr-only">Cargando...</span>
    </div>
  )
}
