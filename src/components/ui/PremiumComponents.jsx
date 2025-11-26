import { motion, AnimatePresence } from 'framer-motion';
import { X } from 'lucide-react';
import { useEffect } from 'react';

export default function Modal({ isOpen, onClose, children, title, size = 'md' }) {
    // Close on escape key
    useEffect(() => {
        const handleEscape = (e) => {
            if (e.key === 'Escape') onClose();
        };

        if (isOpen) {
            document.addEventListener('keydown', handleEscape);
            document.body.style.overflow = 'hidden';
        }

        return () => {
            document.removeEventListener('keydown', handleEscape);
            document.body.style.overflow = 'unset';
        };
    }, [isOpen, onClose]);

    const sizeClasses = {
        sm: 'max-w-md',
        md: 'max-w-2xl',
        lg: 'max-w-4xl',
        xl: 'max-w-6xl',
        full: 'max-w-[95vw]'
    };

    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    {/* Backdrop */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        transition={{ duration: 0.2 }}
                        onClick={onClose}
                        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50"
                    />

                    {/* Modal */}
                    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none">
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95, y: 20 }}
                            animate={{ opacity: 1, scale: 1, y: 0 }}
                            exit={{ opacity: 0, scale: 0.95, y: 20 }}
                            transition={{ duration: 0.2, ease: [0.4, 0, 0.2, 1] }}
                            className={`
                relative w-full ${sizeClasses[size]} max-h-[90vh] 
                bg-white border border-black/10 rounded-lg shadow-2xl
                pointer-events-auto overflow-hidden
              `}
                        >
                            {/* Header */}
                            {title && (
                                <div className="flex items-center justify-between px-8 py-6 border-b border-black/5">
                                    <h2 className="text-heading">{title}</h2>
                                    <button
                                        onClick={onClose}
                                        className="w-8 h-8 flex items-center justify-center text-gray-400 hover:text-black transition-colors duration-200 rounded hover:bg-gray-50"
                                    >
                                        <X className="w-5 h-5" strokeWidth={1.5} />
                                    </button>
                                </div>
                            )}

                            {/* Content */}
                            <div className="overflow-y-auto max-h-[calc(90vh-80px)] px-8 py-6">
                                {children}
                            </div>
                        </motion.div>
                    </div>
                </>
            )}
        </AnimatePresence>
    );
}

// Toast Notification Component
export function Toast({ message, type = 'info', isVisible, onClose }) {
    useEffect(() => {
        if (isVisible) {
            const timer = setTimeout(onClose, 4000);
            return () => clearTimeout(timer);
        }
    }, [isVisible, onClose]);

    const typeStyles = {
        success: 'border-black bg-black text-white',
        error: 'border-oxblood bg-oxblood text-white',
        info: 'border-black/10 bg-white text-black',
        warning: 'border-amber-500 bg-amber-50 text-amber-900'
    };

    return (
        <AnimatePresence>
            {isVisible && (
                <motion.div
                    initial={{ opacity: 0, y: -20, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: -20, scale: 0.95 }}
                    transition={{ duration: 0.2, ease: [0.4, 0, 0.2, 1] }}
                    className="fixed top-6 right-6 z-50"
                >
                    <div className={`
            flex items-center gap-3 px-6 py-4 border rounded-lg shadow-lg
            ${typeStyles[type]}
          `}>
                        <p className="text-sm font-medium">{message}</p>
                        <button
                            onClick={onClose}
                            className="opacity-70 hover:opacity-100 transition-opacity"
                        >
                            <X className="w-4 h-4" strokeWidth={2} />
                        </button>
                    </div>
                </motion.div>
            )}
        </AnimatePresence>
    );
}

// Command Palette Component
export function CommandPalette({ isOpen, onClose, commands }) {
    useEffect(() => {
        const handleKeyDown = (e) => {
            // Cmd+K or Ctrl+K to toggle
            if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
                e.preventDefault();
                onClose();
            }
            if (e.key === 'Escape') {
                onClose();
            }
        };

        if (isOpen) {
            document.addEventListener('keydown', handleKeyDown);
            document.body.style.overflow = 'hidden';
        }

        return () => {
            document.removeEventListener('keydown', handleKeyDown);
            document.body.style.overflow = 'unset';
        };
    }, [isOpen, onClose]);

    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    {/* Backdrop */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50"
                    />

                    {/* Command Palette */}
                    <div className="fixed inset-0 z-50 flex items-start justify-center pt-[20vh] p-4 pointer-events-none">
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95, y: -20 }}
                            animate={{ opacity: 1, scale: 1, y: 0 }}
                            exit={{ opacity: 0, scale: 0.95, y: -20 }}
                            transition={{ duration: 0.2, ease: [0.4, 0, 0.2, 1] }}
                            className="w-full max-w-2xl bg-white border border-black/10 rounded-lg shadow-2xl pointer-events-auto overflow-hidden"
                        >
                            {/* Search Input */}
                            <div className="px-6 py-4 border-b border-black/5">
                                <input
                                    type="text"
                                    placeholder="Type a command or search..."
                                    autoFocus
                                    className="w-full bg-transparent text-lg outline-none placeholder:text-gray-400"
                                />
                            </div>

                            {/* Commands List */}
                            <div className="max-h-[400px] overflow-y-auto p-2">
                                {commands?.map((command, index) => (
                                    <button
                                        key={index}
                                        onClick={() => {
                                            command.action();
                                            onClose();
                                        }}
                                        className="w-full flex items-center gap-4 px-4 py-3 text-left hover:bg-gray-50 rounded transition-colors duration-150"
                                    >
                                        {command.icon && (
                                            <div className="w-8 h-8 flex items-center justify-center border border-black/10 bg-gray-50 rounded">
                                                <command.icon className="w-4 h-4 text-black" strokeWidth={1.5} />
                                            </div>
                                        )}
                                        <div className="flex-1">
                                            <p className="text-sm font-medium text-black">{command.label}</p>
                                            {command.description && (
                                                <p className="text-xs text-gray-500">{command.description}</p>
                                            )}
                                        </div>
                                        {command.shortcut && (
                                            <kbd className="px-2 py-1 text-xs font-mono bg-gray-100 border border-black/10 rounded">
                                                {command.shortcut}
                                            </kbd>
                                        )}
                                    </button>
                                ))}
                            </div>

                            {/* Footer */}
                            <div className="px-6 py-3 border-t border-black/5 bg-gray-50">
                                <p className="text-xs text-gray-500 text-center">
                                    Press <kbd className="px-1.5 py-0.5 bg-white border border-black/10 rounded text-xs font-mono">ESC</kbd> to close
                                </p>
                            </div>
                        </motion.div>
                    </div>
                </>
            )}
        </AnimatePresence>
    );
}

// Dropdown Menu Component
export function Dropdown({ trigger, items, align = 'right' }) {
    const [isOpen, setIsOpen] = useState(false);

    useEffect(() => {
        const handleClickOutside = () => setIsOpen(false);
        if (isOpen) {
            document.addEventListener('click', handleClickOutside);
        }
        return () => document.removeEventListener('click', handleClickOutside);
    }, [isOpen]);

    const alignClasses = {
        left: 'left-0',
        right: 'right-0',
        center: 'left-1/2 -translate-x-1/2'
    };

    return (
        <div className="relative">
            <div onClick={(e) => { e.stopPropagation(); setIsOpen(!isOpen); }}>
                {trigger}
            </div>

            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: -10 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: -10 }}
                        transition={{ duration: 0.15, ease: [0.4, 0, 0.2, 1] }}
                        className={`
              absolute top-full mt-2 ${alignClasses[align]}
              min-w-[200px] bg-white border border-black/10 rounded-lg shadow-xl
              overflow-hidden z-50
            `}
                    >
                        <div className="py-2">
                            {items.map((item, index) => (
                                <button
                                    key={index}
                                    onClick={() => {
                                        item.action();
                                        setIsOpen(false);
                                    }}
                                    className="w-full flex items-center gap-3 px-4 py-2.5 text-left hover:bg-gray-50 transition-colors duration-150"
                                >
                                    {item.icon && (
                                        <item.icon className="w-4 h-4 text-gray-600" strokeWidth={1.5} />
                                    )}
                                    <span className="text-sm text-black">{item.label}</span>
                                </button>
                            ))}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
