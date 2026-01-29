'use client';

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { cn } from '@/lib/utils';

interface AutoSaveProps {
  data: any;
  onSave: (data: any) => Promise<void>;
  debounceMs?: number;
  enabled?: boolean;
  showStatus?: boolean;
  showManualSave?: boolean;
  className?: string;
}

type SaveStatus = 'idle' | 'saving' | 'saved' | 'error';

export function AutoSave({
  data,
  onSave,
  debounceMs = 2000,
  enabled = true,
  showStatus = true,
  showManualSave = true,
  className
}: AutoSaveProps) {
  const [saveStatus, setSaveStatus] = useState<SaveStatus>('idle');
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isDirty, setIsDirty] = useState(false);

  const debounceRef = useRef<NodeJS.Timeout | null>(null);
  const saveInProgressRef = useRef(false);
  const lastDataRef = useRef<any>(null);

  // Check if data has changed
  const hasDataChanged = useCallback((newData: any, oldData: any) => {
    if (!oldData) return true;
    return JSON.stringify(newData) !== JSON.stringify(oldData);
  }, []);

  // Save function
  const performSave = useCallback(async (dataToSave: any) => {
    if (saveInProgressRef.current) return;

    saveInProgressRef.current = true;
    setSaveStatus('saving');
    setError(null);

    try {
      await onSave(dataToSave);
      setSaveStatus('saved');
      setLastSaved(new Date());
      setIsDirty(false);
      lastDataRef.current = { ...dataToSave };

      // Reset to idle after 2 seconds
      setTimeout(() => {
        if (saveStatus === 'saved') {
          setSaveStatus('idle');
        }
      }, 2000);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Save failed';
      setError(errorMessage);
      setSaveStatus('error');

      // Auto-retry after 3 seconds
      setTimeout(() => {
        if (saveStatus === 'error' && isDirty) {
          performSave(dataToSave);
        }
      }, 3000);
    } finally {
      saveInProgressRef.current = false;
    }
  }, [onSave, saveStatus, isDirty]);

  // Debounced save
  const debouncedSave = useCallback((dataToSave: any) => {
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    debounceRef.current = setTimeout(() => {
      if (enabled && isDirty) {
        performSave(dataToSave);
      }
    }, debounceMs);
  }, [enabled, isDirty, performSave, debounceMs]);

  // Manual save
  const handleManualSave = useCallback(async () => {
    if (saveStatus === 'saving') return;

    setIsDirty(true);
    await performSave(data);
  }, [saveStatus, performSave, data]);

  // Watch for data changes
  useEffect(() => {
    if (!enabled) return;

    if (hasDataChanged(data, lastDataRef.current)) {
      setIsDirty(true);
      debouncedSave(data);
    }
  }, [data, enabled, hasDataChanged, debouncedSave]);

  // Cleanup debounce on unmount
  useEffect(() => {
    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    };
  }, []);

  // Status indicator component
  const StatusIndicator = () => {
    if (!showStatus) return null;

    const statusConfig = {
      idle: { icon: '○', color: 'text-[var(--muted)]', label: 'Ready' },
      saving: { icon: '⟳', color: 'text-blue-500 animate-spin', label: 'Saving...' },
      saved: { icon: '✓', color: 'text-green-500', label: 'Saved' },
      error: { icon: '✕', color: 'text-red-500', label: 'Error' }
    };

    const config = statusConfig[saveStatus];

    return (
      <div className="flex items-center gap-2 text-xs font-technical">
        <span className={cn('transition-colors', config.color)}>
          {config.icon}
        </span>
        <span className="text-[var(--muted)]">{config.label}</span>

        {lastSaved && (
          <span className="text-[var(--muted)]">
            {lastSaved.toLocaleTimeString()}
          </span>
        )}

        {isDirty && saveStatus !== 'saving' && (
          <span className="text-orange-500">• Unsaved</span>
        )}
      </div>
    );
  };

  // Manual save button
  const ManualSaveButton = () => {
    if (!showManualSave) return null;

    const isDisabled = saveStatus === 'saving' || !isDirty;

    return (
      <button
        onClick={handleManualSave}
        disabled={isDisabled}
        className={cn(
          "px-3 py-1 text-xs font-technical rounded border transition-all duration-200",
          isDisabled
            ? "bg-[var(--paper)] text-[var(--muted)] border-[var(--border)] cursor-not-allowed"
            : isDirty
            ? "bg-blue-50 text-blue-600 border-blue-200 hover:bg-blue-100"
            : "bg-[var(--paper)] text-[var(--muted)] border-[var(--border)]"
        )}
      >
        {saveStatus === 'saving' ? 'Saving...' : 'Save Now'}
      </button>
    );
  };

  // Error display
  const ErrorDisplay = () => {
    if (!error) return null;

    return (
      <div className="flex items-center gap-2 p-2 bg-red-50 border border-red-200 rounded text-xs">
        <span className="text-red-500">✕</span>
        <span className="text-red-700">{error}</span>
        <button
          onClick={() => {
            setError(null);
            setSaveStatus('idle');
          }}
          className="ml-auto text-red-500 hover:text-red-700"
        >
          Dismiss
        </button>
      </div>
    );
  };

  return (
    <div className={cn("space-y-2", className)}>
      {/* Status and manual save */}
      <div className="flex items-center justify-between">
        <StatusIndicator />
        <ManualSaveButton />
      </div>

      {/* Error display */}
      <ErrorDisplay />

      {/* Auto-save info (debug mode) */}
      {process.env.NODE_ENV === 'development' && (
        <div className="text-xs text-[var(--muted)] font-technical space-y-1">
          <div>Status: {saveStatus}</div>
          <div>Dirty: {isDirty ? 'Yes' : 'No'}</div>
          <div>Debounce: {debounceMs}ms</div>
          <div>Enabled: {enabled ? 'Yes' : 'No'}</div>
          {lastSaved && (
            <div>Last saved: {lastSaved.toISOString()}</div>
          )}
        </div>
      )}
    </div>
  );
}

// Hook for auto-save functionality
export function useAutoSave(
  data: any,
  saveFunction: (data: any) => Promise<void>,
  options: {
    debounceMs?: number;
    enabled?: boolean;
  } = {}
) {
  const [saveStatus, setSaveStatus] = useState<SaveStatus>('idle');
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [error, setError] = useState<string | null>(null);

  const { debounceMs = 2000, enabled = true } = options;
  const debounceRef = useRef<NodeJS.Timeout | null>(null);
  const saveInProgressRef = useRef(false);
  const lastDataRef = useRef<any>(null);

  const save = useCallback(async (dataToSave: any) => {
    if (saveInProgressRef.current) return;

    saveInProgressRef.current = true;
    setSaveStatus('saving');
    setError(null);

    try {
      await saveFunction(dataToSave);
      setSaveStatus('saved');
      setLastSaved(new Date());
      lastDataRef.current = { ...dataToSave };

      setTimeout(() => {
        setSaveStatus('idle');
      }, 2000);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Save failed';
      setError(errorMessage);
      setSaveStatus('error');
    } finally {
      saveInProgressRef.current = false;
    }
  }, [saveFunction]);

  const triggerSave = useCallback((dataToSave: any) => {
    if (!enabled) return;

    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    debounceRef.current = setTimeout(() => {
      save(dataToSave);
    }, debounceMs);
  }, [enabled, save, debounceMs]);

  useEffect(() => {
    if (!enabled) return;

    if (JSON.stringify(data) !== JSON.stringify(lastDataRef.current)) {
      triggerSave(data);
    }
  }, [data, enabled, triggerSave]);

  return {
    saveStatus,
    lastSaved,
    error,
    manualSave: () => save(data)
  };
}
