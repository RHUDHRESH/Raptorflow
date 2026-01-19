"use client";

import { useState } from "react";
import { Settings, BarChart3, Edit3, Download, Upload, Eye } from "lucide-react";
import { useBCMStore } from "@/stores/bcmStore";
import { BlueprintButton } from "@/components/ui/BlueprintButton";
import { BlueprintBadge } from "@/components/ui/BlueprintBadge";

interface BCMNavigationProps {
  onEdit?: () => void;
  onVisualize?: () => void;
}

export function BCMNavigation({ onEdit, onVisualize }: BCMNavigationProps) {
  const { bcm, exportBCM, importBCM } = useBCMStore();
  const [showMenu, setShowMenu] = useState(false);

  const handleExport = () => {
    const jsonString = exportBCM();
    if (jsonString) {
      const blob = new Blob([jsonString], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'business-context.json';
      a.click();
      URL.revokeObjectURL(url);
    }
    setShowMenu(false);
  };

  const handleImport = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const jsonString = e.target?.result as string;
        const result = importBCM(jsonString);
        if (!result.success) {
          alert(result.error);
        }
      };
      reader.readAsText(file);
    }
    setShowMenu(false);
  };

  if (!bcm) {
    return (
      <div className="flex items-center gap-2">
        <BlueprintBadge variant="warning" size="sm">
          No Business Context
        </BlueprintBadge>
        <BlueprintButton size="sm" onClick={onEdit}>
          Create BCM
        </BlueprintButton>
      </div>
    );
  }

  return (
    <div className="relative">
      {/* BCM Status */}
      <div className="flex items-center gap-3">
        <BlueprintBadge variant="success" size="sm">
          BCM v{bcm.meta.version}
        </BlueprintBadge>
        
        <BlueprintButton 
          size="sm" 
          onClick={() => setShowMenu(!showMenu)}
          className="flex items-center gap-2"
        >
          <Settings size={14} />
          BCM
        </BlueprintButton>
      </div>

      {/* Dropdown Menu */}
      {showMenu && (
        <div className="absolute top-full right-0 mt-2 w-48 bg-[var(--paper)] border border-[var(--border)] rounded-lg shadow-lg z-50">
          <div className="p-2 space-y-1">
            <button
              onClick={() => {
                onEdit?.();
                setShowMenu(false);
              }}
              className="w-full flex items-center gap-2 px-3 py-2 text-sm text-[var(--ink)] hover:bg-[var(--surface)] rounded transition-colors"
            >
              <Edit3 size={14} />
              Edit BCM
            </button>
            
            <button
              onClick={() => {
                onVisualize?.();
                setShowMenu(false);
              }}
              className="w-full flex items-center gap-2 px-3 py-2 text-sm text-[var(--ink)] hover:bg-[var(--surface)] rounded transition-colors"
            >
              <Eye size={14} />
              View Analytics
            </button>
            
            <button
              onClick={handleExport}
              className="w-full flex items-center gap-2 px-3 py-2 text-sm text-[var(--ink)] hover:bg-[var(--surface)] rounded transition-colors"
            >
              <Download size={14} />
              Export BCM
            </button>
            
            <label className="w-full flex items-center gap-2 px-3 py-2 text-sm text-[var(--ink)] hover:bg-[var(--surface)] rounded transition-colors cursor-pointer">
              <Upload size={14} />
              Import BCM
              <input type="file" accept=".json" onChange={handleImport} className="hidden" />
            </label>
          </div>
        </div>
      )}

      {/* Click outside to close */}
      {showMenu && (
        <div 
          className="fixed inset-0 z-40" 
          onClick={() => setShowMenu(false)}
        />
      )}
    </div>
  );
}
