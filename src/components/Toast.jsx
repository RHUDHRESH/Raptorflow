import { Toaster, toast } from 'sonner';

// Re-export toast for use in other components
export { toast };

// Compatibility provider that renders the Toaster and children
export const ToastProvider = ({ children }) => {
  return (
    <>
      <Toaster position="top-right" richColors closeButton />
      {children}
    </>
  );
};

// Deprecated hook - mapped to sonner's toast for backward compatibility if needed
// But ideally components should import { toast } directly
export const useToast = () => {
  return {
    addToast: (message, type) => toast[type || 'info'](message),
    success: (message) => toast.success(message),
    error: (message) => toast.error(message),
    info: (message) => toast.info(message),
    warning: (message) => toast.warning(message),
    removeToast: (id) => toast.dismiss(id)
  };
};

