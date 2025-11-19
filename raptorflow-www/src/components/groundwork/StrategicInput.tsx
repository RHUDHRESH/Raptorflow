'use client';

import React, { useRef, useCallback, useEffect, useState } from 'react';
import { Paperclip, X } from 'lucide-react';
import { cn } from '@/lib/utils';
import { motion, AnimatePresence } from 'framer-motion';

interface StrategicInputProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  contextHint?: string;
  onAttachFile?: () => void;
  attachments?: string[];
  onRemoveAttachment?: (index: number) => void;
  minHeight?: number;
  maxHeight?: number;
  className?: string;
}

function useAutoResizeTextarea({
  minHeight,
  maxHeight,
}: {
  minHeight: number;
  maxHeight?: number;
}) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const adjustHeight = useCallback(
    (reset?: boolean) => {
      const textarea = textareaRef.current;
      if (!textarea) return;

      if (reset) {
        textarea.style.height = `${minHeight}px`;
        return;
      }

      textarea.style.height = `${minHeight}px`;
      const newHeight = Math.max(
        minHeight,
        Math.min(textarea.scrollHeight, maxHeight ?? Number.POSITIVE_INFINITY)
      );
      textarea.style.height = `${newHeight}px`;
    },
    [minHeight, maxHeight]
  );

  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = `${minHeight}px`;
    }
  }, [minHeight]);

  useEffect(() => {
    const handleResize = () => adjustHeight();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [adjustHeight]);

  return { textareaRef, adjustHeight };
}

export function StrategicInput({
  value,
  onChange,
  placeholder = 'Share your thoughts...',
  contextHint,
  onAttachFile,
  attachments = [],
  onRemoveAttachment,
  minHeight = 80,
  maxHeight = 200,
  className,
}: StrategicInputProps) {
  const [isFocused, setIsFocused] = useState(false);
  const { textareaRef, adjustHeight } = useAutoResizeTextarea({ minHeight, maxHeight });

  useEffect(() => {
    adjustHeight();
  }, [value, adjustHeight]);

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    onChange(e.target.value);
    adjustHeight();
  };

  return (
    <div className={cn('space-y-4', className)}>
      <div className="relative">
        <div
          className={cn(
            'relative rounded-lg border transition-all duration-200',
            'bg-rf-bg',
            isFocused
              ? 'border-rf-primary shadow-rf ring-1 ring-rf-primary/20'
              : 'border-rf-cloud hover:border-rf-subtle'
          )}
        >
          <textarea
            ref={textareaRef}
            value={value}
            onChange={handleChange}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            placeholder={placeholder}
            className={cn(
              'w-full resize-none bg-transparent px-4 py-3',
              'text-rf-ink placeholder:text-rf-muted',
              'focus:outline-none',
              'text-sm leading-relaxed'
            )}
            style={{
              minHeight: `${minHeight}px`,
              maxHeight: `${maxHeight}px`,
            }}
          />

          <div className="absolute bottom-3 right-3 flex items-center gap-2">
            {onAttachFile && (
              <button
                type="button"
                onClick={onAttachFile}
                className={cn(
                  'p-2 rounded-lg transition-colors',
                  'text-rf-subtle hover:text-rf-ink hover:bg-rf-cloud'
                )}
                aria-label="Attach file"
              >
                <Paperclip className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>

        {contextHint && (
          <p className="mt-2 text-xs text-rf-subtle">{contextHint}</p>
        )}
      </div>

      <AnimatePresence>
        {attachments.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="flex flex-wrap gap-2"
          >
            {attachments.map((file, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                className="flex items-center gap-2 px-3 py-1.5 bg-rf-cloud rounded-lg text-xs text-rf-ink"
              >
                <span className="truncate max-w-[200px]">{file}</span>
                {onRemoveAttachment && (
                  <button
                    type="button"
                    onClick={() => onRemoveAttachment(index)}
                    className="text-rf-subtle hover:text-rf-ink transition-colors"
                    aria-label="Remove attachment"
                  >
                    <X className="w-3 h-3" />
                  </button>
                )}
              </motion.div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

