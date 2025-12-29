import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';
import { HelpCircle, Check, ChevronDown, ChevronUp, X } from 'lucide-react';

interface Option {
  value: string;
  label: string;
  description?: string;
  icon?: React.ReactNode;
}

interface WizardQuestionProps {
  title: React.ReactNode;
  subtitle?: string;
  options?: Option[];
  selectedValues: string[];
  onSelect: (value: string) => void;
  multiSelect?: boolean;
  maxSelections?: number;
  cols?: 1 | 2 | 3 | 4;
  autoAdvance?: boolean;
  onAutoAdvance?: () => void;
  whyWeAsk?: string;
  definitions?: Record<string, string>;
  example?: string;
  isUnsure?: boolean;
  onToggleUnsure?: (val: boolean) => void;
  children?: React.ReactNode;
}

// Helper to highlight defined terms
const TextWithDefinitions = ({
  text,
  definitions,
  onShowDef,
}: {
  text: string;
  definitions?: Record<string, string>;
  onShowDef: (term: string, def: string) => void;
}) => {
  if (!definitions || Object.keys(definitions).length === 0) return <>{text}</>;

  const parts = text.split(
    new RegExp(`(${Object.keys(definitions).join('|')})`, 'gi')
  );
  return (
    <>
      {parts.map((part, i) => {
        const def = Object.entries(definitions).find(
          ([k]) => k.toLowerCase() === part.toLowerCase()
        );
        if (def) {
          return (
            <span
              key={i}
              onClick={(e) => {
                e.stopPropagation();
                onShowDef(def[0], def[1]);
              }}
              className="group/term relative inline-block cursor-help border-b border-dotted border-[#9D9F9F] mx-1"
            >
              {part}
              {/* Desktop Tooltip */}
              <span className="hidden md:block absolute left-1/2 -translate-x-1/2 bottom-full mb-2 w-48 p-3 bg-[#2D3538] text-[#F3F4EE] text-xs rounded-lg opacity-0 group-hover/term:opacity-100 transition-opacity pointer-events-none z-50 shadow-xl leading-relaxed text-center normal-case font-sans">
                {def[1]}
                <span className="absolute top-full left-1/2 -translate-x-1/2 border-8 border-transparent border-t-[#2D3538]" />
              </span>
            </span>
          );
        }
        return part;
      })}
    </>
  );
};

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.05,
    },
  },
};

const item = {
  hidden: { opacity: 0, y: 10 },
  show: { opacity: 1, y: 0 },
};

export default function WizardQuestion({
  title,
  subtitle,
  options,
  selectedValues,
  onSelect,
  multiSelect = false,
  maxSelections,
  cols = 2,
  autoAdvance,
  onAutoAdvance,
  whyWeAsk,
  definitions,
  example,
  isUnsure,
  onToggleUnsure,
  children,
}: WizardQuestionProps) {
  const [showExample, setShowExample] = useState(false);
  const [mobileHelp, setMobileHelp] = useState<{
    title: string;
    body: string;
  } | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Auto-focus container logic
  useEffect(() => {
    const timer = setTimeout(() => {
      const firstBtn = containerRef.current?.querySelector('button');
      if (firstBtn) {
        firstBtn.focus({ preventScroll: true });
      }
    }, 100);
    return () => clearTimeout(timer);
  }, [title]);

  const handleSelect = (value: string) => {
    if (isUnsure && onToggleUnsure) onToggleUnsure(false);

    if (!multiSelect) {
      onSelect(value);
      if (autoAdvance && onAutoAdvance) {
        setTimeout(() => {
          onAutoAdvance();
        }, 400);
      }
      return;
    }

    const isSelected = selectedValues.includes(value);
    if (isSelected) {
      onSelect(value);
    } else {
      if (maxSelections && selectedValues.length >= maxSelections) return;
      onSelect(value);
    }
  };

  // Numeric Hotkeys
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const num = parseInt(e.key);
      if (!isNaN(num) && num > 0 && num <= (options?.length || 0)) {
        handleSelect(options![num - 1].value);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [options, handleSelect]);

  const gridCols = {
    1: 'grid-cols-1',
    2: 'grid-cols-1 md:grid-cols-2',
    3: 'grid-cols-1 md:grid-cols-3',
    4: 'grid-cols-2 md:grid-cols-4',
  };

  return (
    <div className="space-y-12 relative">
      <div className="text-center space-y-4 animate-in fade-in zoom-in-95 duration-500 flex flex-col items-center">
        <div className="relative inline-block">
          <h1 className="font-serif text-4xl text-[#2D3538] leading-tight flex items-center gap-3">
            {typeof title === 'string' ? (
              <TextWithDefinitions
                text={title}
                definitions={definitions}
                onShowDef={(t, d) => setMobileHelp({ title: t, body: d })}
              />
            ) : (
              title
            )}

            {whyWeAsk && (
              <div className="group relative">
                <HelpCircle
                  className="w-5 h-5 text-[#C0C1BE] hover:text-[#2D3538] cursor-help transition-colors"
                  onClick={() =>
                    setMobileHelp({ title: 'Why we ask', body: whyWeAsk })
                  }
                />
                {/* Desktop Tooltip */}
                <div className="hidden md:block absolute left-1/2 -translate-x-1/2 bottom-full mb-2 w-64 p-3 bg-[#2D3538] text-[#F3F4EE] text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50 shadow-xl leading-relaxed text-center">
                  {whyWeAsk}
                  <div className="absolute top-full left-1/2 -translate-x-1/2 border-8 border-transparent border-t-[#2D3538]" />
                </div>
              </div>
            )}
          </h1>
        </div>

        {subtitle && (
          <p className="text-[#5B5F61] text-lg max-w-md mx-auto">{subtitle}</p>
        )}

        {/* Example Toggle View */}
        {example && showExample && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="bg-[#F3F4EE] border border-[#C0C1BE] border-dashed rounded-xl p-4 max-w-lg mx-auto text-sm text-[#5B5F61] italic font-serif text-left relative mt-4"
          >
            <span className="absolute -top-3 left-4 bg-[#F3F4EE] px-2 text-[10px] uppercase font-bold tracking-widest text-[#9D9F9F]">
              Example
            </span>
            "{example}"
          </motion.div>
        )}

        <div className="flex items-center gap-4">
          {/* Selection Counter */}
          {multiSelect && (
            <div className="inline-flex items-center gap-2 px-3 py-1 bg-[#E5E7E1] rounded-full text-xs font-medium text-[#5B5F61] uppercase tracking-wide">
              {selectedValues.length}{' '}
              {maxSelections ? `/ ${maxSelections}` : ''} Selected
            </div>
          )}

          {/* Example Toggle Button */}
          {example && (
            <button
              onClick={() => setShowExample(!showExample)}
              className="text-xs font-semibold text-[#2D3538] underline decoration-dotted hover:text-blue-600 transition-colors"
            >
              {showExample ? 'Hide Example' : 'See Example'}
            </button>
          )}

          {/* Unsure Toggle */}
          {onToggleUnsure && (
            <button
              onClick={() => onToggleUnsure(!isUnsure)}
              className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium uppercase tracking-wide transition-colors border
                                ${
                                  isUnsure
                                    ? 'bg-yellow-100 text-yellow-800 border-yellow-200'
                                    : 'bg-transparent text-[#9D9F9F] border-transparent hover:bg-[#E5E7E1]'
                                }
                            `}
            >
              {isUnsure ? 'Marked as Unsure' : 'Unsure?'}
            </button>
          )}

          {/* Clear Button */}
          {selectedValues.length > 0 && (
            <button
              onClick={() => {
                // Need to reverse selectedValues for safety, or iterate
                selectedValues.forEach((v) => onSelect(v));
              }}
              className="text-xs font-medium text-[#9D9F9F] hover:text-red-500 transition-colors uppercase tracking-wide underline decoration-dotted"
            >
              Clear
            </button>
          )}
        </div>
      </div>

      {children ? (
        children
      ) : (
        <motion.div
          ref={containerRef}
          variants={container}
          initial="hidden"
          animate="show"
          className={`grid ${gridCols[cols]} gap-4 group/list`}
        >
          {options?.map((option, index) => {
            const isSelected = selectedValues.includes(option.value);
            const isDisabled =
              multiSelect && maxSelections
                ? !isSelected && selectedValues.length >= maxSelections
                : false;

            return (
              <motion.button
                variants={item}
                key={option.value}
                onClick={() => handleSelect(option.value)}
                disabled={isDisabled}
                role={multiSelect ? 'checkbox' : 'radio'}
                aria-checked={isSelected}
                aria-disabled={isDisabled}
                whileHover={{
                  scale: isDisabled ? 1 : 1.02,
                  y: isDisabled ? 0 : -2,
                }}
                whileTap={{ scale: isDisabled ? 1 : 0.98 }}
                className={cn(
                  'flex flex-col items-start p-6 rounded-2xl border transition-all duration-300 text-left relative overflow-hidden',
                  'outline-none focus-visible:ring-2 focus-visible:ring-[#2D3538] focus-visible:ring-offset-2',
                  'hover:shadow-lg group-hover/list:opacity-50 hover:!opacity-100',
                  isSelected
                    ? 'border-[#2D3538] bg-white shadow-md !opacity-100'
                    : isDisabled
                      ? 'opacity-30 cursor-not-allowed border-[#C0C1BE]/30 bg-[#F3F4EE] grayscale'
                      : 'border-[#C0C1BE]/50 bg-transparent hover:border-[#2D3538]/50 hover:bg-white/90'
                )}
              >
                {/* Ripple / Pulse Effect on Selection */}
                {isSelected && (
                  <motion.div
                    layoutId="highlight"
                    className="absolute inset-0 bg-[#2D3538]/5 pointer-events-none"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                  />
                )}

                <div className="absolute top-4 right-4 text-[10px] font-mono text-[#C0C1BE] opacity-0 group-hover:opacity-100 transition-opacity">
                  {index + 1}
                </div>

                <div className="font-medium text-lg text-[#2D3538] mb-1 flex items-center gap-2 relative z-10">
                  {option.icon}
                  {option.label}
                </div>
                {option.description && (
                  <div
                    className={`text-sm ${isSelected ? 'text-[#5B5F61]' : 'text-[#9D9F9F]'}`}
                  >
                    {option.description}
                  </div>
                )}

                {isSelected && (
                  <motion.div
                    layoutId="check"
                    className="absolute top-4 right-4 w-2 h-2 rounded-full bg-[#2D3538]"
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ type: 'spring', stiffness: 300, damping: 20 }}
                  />
                )}
              </motion.button>
            );
          })}
        </motion.div>
      )}
      {/* Mobile Bottom Sheet Drawer */}
      <AnimatePresence>
        {mobileHelp && (
          <>
            <motion.div
              className="fixed inset-0 bg-black/40 z-[60] backdrop-blur-sm md:hidden"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setMobileHelp(null)}
            />
            <motion.div
              className="fixed bottom-0 left-0 right-0 bg-white rounded-t-2xl z-[70] p-6 pb-12 shadow-2xl md:hidden"
              initial={{ y: '100%' }}
              animate={{ y: 0 }}
              exit={{ y: '100%' }}
              drag="y"
              dragConstraints={{ top: 0 }}
              onDragEnd={(e, { offset, velocity }) => {
                if (offset.y > 100 || velocity.y > 20) {
                  setMobileHelp(null);
                }
              }}
            >
              <div className="w-12 h-1 bg-[#E5E7E1] rounded-full mx-auto mb-6" />
              <div className="flex justify-between items-start mb-4">
                <h3 className="font-serif text-xl text-[#2D3538] font-bold">
                  {mobileHelp.title}
                </h3>
                <button onClick={() => setMobileHelp(null)}>
                  <X className="w-6 h-6 text-[#9D9F9F]" />
                </button>
              </div>
              <p className="text-[#5B5F61] leading-relaxed">
                {mobileHelp.body}
              </p>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
}
