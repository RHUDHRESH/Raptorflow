import { motion } from 'framer-motion'
import { Loader2 } from 'lucide-react'

export const LoadingSpinner = ({ size = 'md', className = '' }) => {
  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
    xl: 'w-12 h-12',
  }

  return (
    <Loader2 className={`${sizes[size]} animate-spin text-black ${className}`} strokeWidth={1.5} />
  )
}

export const LoadingOverlay = ({ message = 'Loading...' }) => {
  return (
    <div className="fixed inset-0 bg-white/80 backdrop-blur-sm z-50 flex items-center justify-center">
      <div className="flex flex-col items-center gap-4">
        <LoadingSpinner size="xl" />
        <p className="text-body">{message}</p>
      </div>
    </div>
  )
}

export const LoadingCard = ({ message = 'Loading...', className = '' }) => {
  return (
    <div className={`flex flex-col items-center justify-center py-12 ${className}`}>
      <LoadingSpinner size="lg" />
      <p className="text-body mt-4">{message}</p>
    </div>
  )
}

export const LoadingInline = ({ message }) => {
  return (
    <div className="flex items-center gap-2">
      <LoadingSpinner size="sm" />
      {message && <span className="text-caption">{message}</span>}
    </div>
  )
}

export const LoadingButton = ({ children, isLoading, ...props }) => {
  return (
    <button {...props} disabled={isLoading || props.disabled}>
      {isLoading ? (
        <div className="flex items-center gap-2">
          <LoadingSpinner size="sm" />
          {children}
        </div>
      ) : (
        children
      )}
    </button>
  )
}

export const SkeletonLoader = ({ className = '', count = 1 }) => {
  return (
    <>
      {Array.from({ length: count }).map((_, index) => (
        <motion.div
          key={index}
          className={`animate-pulse bg-gray-200 rounded ${className}`}
          initial={{ opacity: 0.5 }}
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
        />
      ))}
    </>
  )
}

export default {
  LoadingSpinner,
  LoadingOverlay,
  LoadingCard,
  LoadingInline,
  LoadingButton,
  SkeletonLoader,
}
