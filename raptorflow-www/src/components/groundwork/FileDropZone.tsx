'use client';

import React, { useState, useCallback } from 'react';
import { Upload, File, X, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { motion, AnimatePresence } from 'framer-motion';
import { UploadedFile } from '@/lib/groundwork/types';

interface FileDropZoneProps {
  onFilesSelected: (files: File[]) => void;
  uploadedFiles: UploadedFile[];
  onRemoveFile?: (fileId: string) => void;
  className?: string;
}

export function FileDropZone({
  onFilesSelected,
  uploadedFiles,
  onRemoveFile,
  className,
}: FileDropZoneProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);

      const files = Array.from(e.dataTransfer.files);
      if (files.length > 0) {
        setIsProcessing(true);
        onFilesSelected(files);
        // Simulate processing
        setTimeout(() => setIsProcessing(false), 1000);
      }
    },
    [onFilesSelected]
  );

  const handleFileInput = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const files = Array.from(e.target.files || []);
      if (files.length > 0) {
        setIsProcessing(true);
        onFilesSelected(files);
        setTimeout(() => setIsProcessing(false), 1000);
      }
      // Reset input
      e.target.value = '';
    },
    [onFilesSelected]
  );

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <div className={cn('space-y-4', className)}>
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={cn(
          'relative border-2 border-dashed rounded-lg transition-all duration-200',
          'bg-rf-bg',
          isDragging
            ? 'border-rf-primary bg-rf-cloud/50'
            : 'border-rf-cloud hover:border-rf-subtle',
          isProcessing && 'opacity-50 pointer-events-none'
        )}
      >
        <input
          type="file"
          id="file-upload"
          multiple
          accept=".pdf,.ppt,.pptx,.doc,.docx,.png,.jpg,.jpeg,.webp"
          onChange={handleFileInput}
          className="hidden"
        />

        <label
          htmlFor="file-upload"
          className="flex flex-col items-center justify-center p-12 cursor-pointer"
        >
          {isProcessing ? (
            <Loader2 className="w-8 h-8 text-rf-subtle animate-spin mb-3" />
          ) : (
            <Upload className="w-8 h-8 text-rf-subtle mb-3" />
          )}
          <p className="text-sm font-medium text-rf-ink mb-1">
            {isProcessing
              ? 'Processing...'
              : 'Drop files here or click to upload'}
          </p>
          <p className="text-xs text-rf-subtle text-center max-w-sm">
            PDF, PPT, screenshots, pitch decks, brand assets, etc.
          </p>
        </label>
      </div>

      <AnimatePresence>
        {uploadedFiles.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="space-y-2"
          >
            <p className="text-xs font-medium text-rf-subtle uppercase tracking-wide">
              Uploaded Files
            </p>
            <div className="space-y-2">
              {uploadedFiles.map((file) => (
                <motion.div
                  key={file.id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -10 }}
                  className="flex items-center gap-3 p-3 bg-rf-cloud rounded-lg"
                >
                  <File className="w-4 h-4 text-rf-subtle flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-rf-ink truncate">
                      {file.name}
                    </p>
                    <p className="text-xs text-rf-subtle">
                      {formatFileSize(file.size)}
                      {file.ocrStatus === 'processing' && ' • Processing...'}
                      {file.ocrStatus === 'completed' && ' • Processed'}
                    </p>
                  </div>
                  {onRemoveFile && (
                    <button
                      type="button"
                      onClick={() => onRemoveFile(file.id)}
                      className="p-1 text-rf-subtle hover:text-rf-ink transition-colors"
                      aria-label="Remove file"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  )}
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

