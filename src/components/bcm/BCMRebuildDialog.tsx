'use client';

import React, { useState } from 'react';
import { useBcmStore } from '@/stores/bcmStore';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Loader2, RefreshCw, AlertTriangle, CheckCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

interface BCMRebuildDialogProps {
  workspaceId: string;
  children?: React.ReactNode;
  className?: string;
}

export function BCMRebuildDialog({ workspaceId, children, className }: BCMRebuildDialogProps) {
  const { rebuild, status, manifest, error } = useBcmStore();
  const [isOpen, setIsOpen] = useState(false);
  const [isRebuilding, setIsRebuilding] = useState(false);
  const [forceRebuild, setForceRebuild] = useState(false);

  const handleRebuild = async () => {
    setIsRebuilding(true);
    try {
      await rebuild(workspaceId, forceRebuild);
      setIsOpen(false);
      setForceRebuild(false);
    } catch (error) {
      console.error('Rebuild failed:', error);
    } finally {
      setIsRebuilding(false);
    }
  };

  const canRebuild = status !== 'loading' && !isRebuilding;
  const hasRecentManifest = manifest && manifest.generatedAt;
  const isRecent = hasRecentManifest &&
    new Date(manifest.generatedAt).getTime() > Date.now() - (24 * 60 * 60 * 1000); // 24 hours

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        {children || (
          <Button
            variant="outline"
            size="sm"
            disabled={!canRebuild}
            className={cn('gap-2', className)}
          >
            <RefreshCw className="h-4 w-4" />
            Rebuild BCM
          </Button>
        )}
      </DialogTrigger>

      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <RefreshCw className="h-5 w-5" />
            Rebuild Business Context
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {/* Current Status */}
          <div className="space-y-2">
            <h4 className="font-medium text-sm">Current Status</h4>
            <div className="flex items-center gap-2">
              {status === 'loading' && <Loader2 className="h-4 w-4 animate-spin" />}
              {status === 'error' && <AlertTriangle className="h-4 w-4 text-red-500" />}
              {status === 'idle' && manifest && <CheckCircle className="h-4 w-4 text-green-500" />}

              <span className="text-sm">
                {status === 'loading' ? 'Loading...' :
                 status === 'error' ? 'Error loading BCM' :
                 manifest ? 'BCM loaded' : 'No BCM available'}
              </span>
            </div>

            {manifest && (
              <div className="text-xs text-gray-500 space-y-1">
                <div>Version: {manifest.version || '1.0.0'}</div>
                <div>Generated: {manifest.generatedAt ?
                  new Date(manifest.generatedAt).toLocaleString() : 'Unknown'}</div>
                <div>Completion: {Object.keys(manifest.rawStepData || {}).length}/23 steps</div>
              </div>
            )}
          </div>

          {/* Warning for recent rebuilds */}
          {isRecent && !forceRebuild && (
            <Alert>
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                A BCM was generated less than 24 hours ago.
                Rebuilding may not be necessary unless you have made significant changes.
              </AlertDescription>
            </Alert>
          )}

          {/* Force rebuild option */}
          {hasRecentManifest && (
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="force-rebuild"
                checked={forceRebuild}
                onChange={(e) => setForceRebuild(e.target.checked)}
                className="rounded border-gray-300"
              />
              <label htmlFor="force-rebuild" className="text-sm">
                Force rebuild (ignores recent generation)
              </label>
            </div>
          )}

          {/* Error display */}
          {error && (
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* Rebuild info */}
          <div className="bg-gray-50 dark:bg-gray-800 p-3 rounded-lg">
            <h4 className="font-medium text-sm mb-2">What rebuilding does:</h4>
            <ul className="text-xs text-gray-600 dark:text-gray-400 space-y-1">
              <li>• Regenerates BCM from latest onboarding data</li>
              <li>• Updates all cached versions (tier0/1/2)</li>
              <li>• Creates new version in database</li>
              <li>• May take 30-60 seconds to complete</li>
            </ul>
          </div>

          {/* Actions */}
          <div className="flex gap-2 pt-2">
            <Button
              variant="outline"
              onClick={() => setIsOpen(false)}
              disabled={isRebuilding}
            >
              Cancel
            </Button>

            <Button
              onClick={handleRebuild}
              disabled={!canRebuild}
              className="gap-2"
            >
              {isRebuilding ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Rebuilding...
                </>
              ) : (
                <>
                  <RefreshCw className="h-4 w-4" />
                  Rebuild BCM
                </>
              )}
            </Button>
          </div>

          {/* Status badges */}
          <div className="flex gap-2 justify-center">
            {manifest && (
              <Badge variant="secondary" className="text-xs">
                Current: v{manifest.version || '1.0.0'}
              </Badge>
            )}
            {forceRebuild && (
              <Badge variant="destructive" className="text-xs">
                Force Mode
              </Badge>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
