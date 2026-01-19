"use client";

import { useState } from "react";
import { BCMEditor } from "@/components/bcm/BCMEditor";
import { BCMVisualization } from "@/components/bcm/BCMVisualization";
import { BlueprintButton } from "@/components/ui/BlueprintButton";
import { Edit3, BarChart3, ArrowLeft } from "lucide-react";

type BCMView = 'editor' | 'analytics';

export default function BCMPage() {
  const [currentView, setCurrentView] = useState<BCMView>('editor');

  return (
    <div className="min-h-screen bg-[var(--canvas)]">
      {/* Header */}
      <div className="border-b border-[var(--border)] bg-[var(--paper)]">
        <div className="max-w-6xl mx-auto px-6 py-6">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="font-serif text-3xl text-[var(--ink)]">Business Context Model</h1>
              <p className="text-sm text-[var(--muted)] mt-1">
                {currentView === 'editor' 
                  ? 'Edit and manage your business context'
                  : 'Analytics and insights from your business context'
                }
              </p>
            </div>

            {/* View Toggle */}
            <div className="flex items-center gap-2">
              <BlueprintButton
                variant={currentView === 'editor' ? 'default' : 'ghost'}
                size="sm"
                onClick={() => setCurrentView('editor')}
                className="flex items-center gap-2"
              >
                <Edit3 size={14} />
                Edit
              </BlueprintButton>
              
              <BlueprintButton
                variant={currentView === 'analytics' ? 'default' : 'ghost'}
                size="sm"
                onClick={() => setCurrentView('analytics')}
                className="flex items-center gap-2"
              >
                <BarChart3 size={14} />
                Analytics
              </BlueprintButton>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-6xl mx-auto">
        {currentView === 'editor' && <BCMEditor />}
        {currentView === 'analytics' && <BCMVisualization />}
      </div>
    </div>
  );
}
