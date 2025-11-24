import { motion, AnimatePresence } from 'framer-motion'
import { X, Check, AlertCircle, Info } from 'lucide-react'
import { createContext, useContext, useState, useCallback } from 'react'

const ToastContext = createContext(null)

export const useToast = () => {
  const context = useContext(ToastContext)
  if (!context) {
    throw new Error('useToast must be used within ToastProvider')
  }
  return context
}

export const ToastProvider = ({ children }) => {
  const [toasts, setToasts] = useState([])

  const addToast = useCallback((message, type = 'info', duration = 3000) => {
    const id = Date.now() + Math.random()
    setToasts(prev => [...prev, { id, message, type, duration }])
    
    if (duration > 0) {
      setTimeout(() => {
        removeToast(id)
      }, duration)
    }
    
    return id
  }, [])

  const removeToast = useCallback((id) => {
    setToasts(prev => prev.filter(toast => toast.id !== id))
  }, [])

  const success = useCallback((message, duration) => addToast(message, 'success', duration), [addToast])
  const error = useCallback((message, duration) => addToast(message, 'error', duration), [addToast])
  const info = useCallback((message, duration) => addToast(message, 'info', duration), [addToast])
  const warning = useCallback((message, duration) => addToast(message, 'warning', duration), [addToast])

  return (
    <ToastContext.Provider value={{ addToast, removeToast, success, error, info, warning }}>
      {children}
      <ToastContainer toasts={toasts} removeToast={removeToast} />
    </ToastContext.Provider>
  )
}

const ToastContainer = ({ toasts, removeToast }) => {
  return (
    <div className="fixed top-4 right-4 z-[9999] flex flex-col gap-2 pointer-events-none">
      <AnimatePresence>
        {toasts.map((toast) => (
          <Toast key={toast.id} toast={toast} onClose={() => removeToast(toast.id)} />
        ))}
      </AnimatePresence>
    </div>
  )
}

const Toast = ({ toast, onClose }) => {
  const { type, message } = toast

  const config = {
    success: {
      icon: Check,
      className: 'bg-white border-black text-black',
      iconClassName: 'text-black',
    },
    error: {
      icon: AlertCircle,
      className: 'bg-oxblood/5 border-oxblood text-oxblood',
      iconClassName: 'text-oxblood',
    },
    warning: {
      icon: AlertCircle,
      className: 'bg-gray-50 border-gray-400 text-gray-900',
      iconClassName: 'text-gray-600',
    },
    info: {
      icon: Info,
      className: 'bg-white border-black text-black',
      iconClassName: 'text-black',
    },
  }

  const { icon: Icon, className, iconClassName } = config[type] || config.info

  return (
    <motion.div
      initial={{ opacity: 0, y: -20, scale: 0.96 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, x: 100, scale: 0.96 }}
      transition={{ duration: 0.18, ease: [0.4, 0, 0.2, 1] }}
      className={`pointer-events-auto flex items-center gap-3 px-4 py-3 rounded border shadow-lg min-w-[300px] max-w-md ${className}`}
    >
      <Icon className={`w-5 h-5 flex-shrink-0 ${iconClassName}`} strokeWidth={1.5} />
      <p className="flex-1 font-sans text-sm font-medium">{message}</p>
      <button
        onClick={onClose}
        className="flex-shrink-0 opacity-60 hover:opacity-100 transition-opacity duration-180"
        aria-label="Close"
      >
        <X className="w-4 h-4" strokeWidth={1.5} />
      </button>
    </motion.div>
  )
}

// Provide simple toast object for direct usage
let toastInstance = null;

const createToast = () => ({
  success: (message, duration) => toastInstance?.success(message, duration),
  error: (message, duration) => toastInstance?.error(message, duration),
  info: (message, duration) => toastInstance?.info(message, duration),
  warning: (message, duration) => toastInstance?.warning(message, duration)
});

export const toast = createToast();

// Hook to set the toast instance (call from ToastProvider)
export const setToastInstance = (instance) => {
  toastInstance = instance;
  return toast;
};

// Hook to set the toast instance (call from ToastProvider)
