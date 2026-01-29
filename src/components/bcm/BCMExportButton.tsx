'use client';

import React, { useState } from 'react';
import { useBcmStore } from '@/stores/bcmStore';
import { Button } from '@/components/ui/button';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Download, FileText, FileJson, Loader2, AlertTriangle } from 'lucide-react';
import { exportManifest, downloadBlob, getFreshnessStatus } from '@/lib/bcm-client';
import { cn } from '@/lib/utils';

interface BCMExportButtonProps {
  workspaceId: string;
  className?: string;
  variant?: 'default' | 'outline' | 'ghost' | 'secondary';
  size?: 'default' | 'sm' | 'lg' | 'icon';
}

export function BCMExportButton({
  workspaceId,
  className,
  variant = 'outline',
  size = 'sm'
}: BCMExportButtonProps) {
  const { manifest, status, error } = useBcmStore();
  const [isExporting, setIsExporting] = useState(false);
  const [exportFormat, setExportFormat] = useState<'json' | 'markdown'>('json');
  const [showPreview, setShowPreview] = useState(false);

  const handleExport = async (format: 'json' | 'markdown') => {
    if (!manifest) return;

    setIsExporting(true);
    try {
      const blob = await exportManifest(workspaceId, format);
      const timestamp = new Date().toISOString().slice(0, 19).replace(/[:.]/g, '-');
      const filename = `bcm-${workspaceId}-${timestamp}.${format}`;
      downloadBlob(blob, filename);
    } catch (error) {
      console.error('Export failed:', error);
    } finally {
      setIsExporting(false);
    }
  };

  const canExport = status !== 'loading' && manifest && !isExporting;
  const freshness = manifest?.generatedAt
    ? getFreshnessStatus(manifest.generatedAt)
    : { status: 'expired' as const, color: 'red' as const, daysOld: Infinity };

  return (
    <div className={cn('flex items-center gap-2', className)}>
      {/* Export Dropdown */}
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button
            variant={variant}
            size={size}
            disabled={!canExport}
            className="gap-2"
          >
            <Download className="h-4 w-4" />
            Export
          </Button>
        </DropdownMenuTrigger>

        <DropdownMenuContent align="end">
          <DropdownMenuItem onClick={() => handleExport('json')} disabled={!canExport}>
            <FileJson className="h-4 w-4 mr-2" />
            Export as JSON
          </DropdownMenuItem>

          <DropdownMenuItem onClick={() => handleExport('markdown')} disabled={!canExport}>
            <FileText className="h-4 w-4 mr-2" />
            Export as Markdown
          </DropdownMenuItem>

          <DropdownMenuItem onClick={() => setShowPreview(true)} disabled={!canExport}>
            <FileText className="h-4 w-4 mr-2" />
            Preview Export
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>

      {/* Freshness Badge */}
      {manifest && (
        <Badge
          variant={freshness.color === 'green' ? 'default' :
                     freshness.color === 'yellow' ? 'secondary' : 'destructive'}
          className="text-xs"
        >
          {freshness.daysOld === 0 ? 'Today' :
           freshness.daysOld === 1 ? '1d' :
           `${freshness.daysOld}d`}
        </Badge>
      )}

      {/* Export Preview Dialog */}
      <Dialog open={showPreview} onOpenChange={setShowPreview}>
        <DialogContent className="sm:max-w-2xl max-h-[80vh] overflow-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Export Preview
            </DialogTitle>
          </DialogHeader>

          <div className="space-y-4">
            {/* Export Options */}
            <div className="flex gap-2">
              <Button
                variant={exportFormat === 'json' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setExportFormat('json')}
              >
                <FileJson className="h-4 w-4 mr-2" />
                JSON
              </Button>

              <Button
                variant={exportFormat === 'markdown' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setExportFormat('markdown')}
              >
                <FileText className="h-4 w-4 mr-2" />
                Markdown
              </Button>
            </div>

            {/* Preview Content */}
            <div className="border rounded-lg p-4 bg-gray-50 dark:bg-gray-800">
              <div className="mb-2 text-xs text-gray-500 mb-4">
                Preview of {exportFormat} export for BCM v{manifest?.version || '1.0.0'}
              </div>

              <pre className="text-xs overflow-auto max-h-60 whitespace-pre-wrap">
                {exportFormat === 'json' ? (
                  JSON.stringify(manifest, null, 2).slice(0, 1000) +
                  (JSON.stringify(manifest, null, 2).length > 1000 ? '...' : '')
                ) : (
                  `# Business Context Manifest

**Generated:** ${manifest?.generatedAt || 'Unknown'}
**Workspace:** ${workspaceId}
**Completion:** {Object.keys(manifest.rawStepData || {}).length}/23 steps

## Company Information
- **Name:** ${manifest?.company?.name || 'N/A'}
- **Industry:** ${manifest?.company?.industry || 'N/A'}
- **Stage:** ${manifest?.company?.stage || 'N/A'}

## Ideal Customer Profiles
${manifest?.icps ?
  manifest.icps.map((icp, i) => `### ICP ${i + 1}
- **Name:** ${icp.name || 'N/A'}
- **Description:** ${icp.description || 'N/A'}
`).join('\n') : 'No ICPs defined'}

## Value Proposition
${manifest?.value_prop?.primary || 'No value proposition defined'}

---
*Export generated on ${new Date().toLocaleString()}*`
                )}
              </pre>
            </div>

            {/* Export Info */}
            <div className="bg-blue-50 dark:bg-blue-900/20 p-3 rounded-lg">
              <h4 className="font-medium text-sm mb-2">Export Information:</h4>
              <ul className="text-xs text-gray-600 dark:text-gray-400 space-y-1">
                <li>• JSON format includes complete BCM data structure</li>
                <li>• Markdown format is optimized for readability</li>
                <li>• Files are timestamped for version tracking</li>
                <li>• Exported data reflects current BCM state</li>
              </ul>
            </div>

            {/* Error Display */}
            {error && (
              <Alert variant="destructive">
                <AlertTriangle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {/* Actions */}
            <div className="flex gap-2 justify-end">
              <Button
                variant="outline"
                onClick={() => setShowPreview(false)}
                disabled={isExporting}
              >
                Close
              </Button>

              <Button
                onClick={() => handleExport(exportFormat)}
                disabled={!canExport || isExporting}
                className="gap-2"
              >
                {isExporting ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Exporting...
                  </>
                ) : (
                  <>
                    <Download className="h-4 w-4" />
                    Export {exportFormat.toUpperCase()}
                  </>
                )}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
