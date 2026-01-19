"use client";

import { useState } from 'react';
import { Send, X, Lightbulb, CheckCircle } from 'lucide-react';
import { Template, TemplateSection } from '@/lib/museTemplates';
import { BlueprintCard } from '@/components/ui/BlueprintCard';
import { BlueprintButton } from '@/components/ui/BlueprintButton';
import { cn } from '@/lib/utils';

interface TemplateEditorProps {
  template: Template;
  onSubmit: (content: string) => void;
  onClose: () => void;
}

export function TemplateEditor({ template, onSubmit, onClose }: TemplateEditorProps) {
  const [values, setValues] = useState<Record<string, string>>({});
  const [showTips, setShowTips] = useState(false);
  const [currentSection, setCurrentSection] = useState(0);

  const handleValueChange = (sectionId: string, value: string) => {
    setValues(prev => ({
      ...prev,
      [sectionId]: value
    }));
  };

  const generateContent = () => {
    let content = '';

    template.sections.forEach((section, index) => {
      const value = values[section.id] || section.placeholder || '';

      // Add section title
      if (index > 0) content += '\n\n';
      content += `## ${section.title}\n\n`;

      // Add section content
      content += value;

      // Add placeholder replacements
      if (template.placeholders) {
        Object.entries(template.placeholders).forEach(([key, placeholder]) => {
          content = content.replace(`[${key}]`, placeholder);
        });
      }
    });

    return content;
  };

  const handleSubmit = () => {
    const content = generateContent();
    onSubmit(content);
  };

  const canSubmit = () => {
    return template.sections
      .filter(section => section.required)
      .every(section => values[section.id]?.trim());
  };

  const progress = (template.sections.filter(section => values[section.id]?.trim()).length / template.sections.length) * 100;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <BlueprintCard className="w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-[var(--structure-subtle)]">
          <div>
            <h2 className="text-lg font-semibold text-[var(--ink)]">{template.title}</h2>
            <p className="text-sm text-[var(--ink-muted)]">{template.description}</p>
          </div>
          <div className="flex items-center gap-2">
            {template.conversionTips && (
              <BlueprintButton
                variant="secondary"
                size="sm"
                onClick={() => setShowTips(!showTips)}
                className="flex items-center gap-1"
              >
                <Lightbulb size={14} />
                Tips
              </BlueprintButton>
            )}
            <button
              onClick={onClose}
              className="p-1 hover:bg-[var(--surface)] rounded text-[var(--ink-muted)]"
            >
              <X size={20} />
            </button>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="px-4 py-2 border-b border-[var(--structure-subtle)]">
          <div className="flex items-center justify-between text-xs text-[var(--ink-muted)] mb-1">
            <span>Progress</span>
            <span>{Math.round(progress)}%</span>
          </div>
          <div className="w-full bg-[var(--structure-subtle)] rounded-full h-2">
            <div
              className="bg-[var(--blueprint)] h-2 rounded-full transition-all"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        <div className="flex flex-1 overflow-hidden">
          {/* Sections */}
          <div className="w-1/3 border-r border-[var(--structure-subtle)] overflow-y-auto">
            <div className="p-4 space-y-2">
              {template.sections.map((section, index) => {
                const isCompleted = values[section.id]?.trim();
                const isCurrent = index === currentSection;

                return (
                  <button
                    key={section.id}
                    onClick={() => setCurrentSection(index)}
                    className={cn(
                      "w-full text-left p-3 rounded-lg border transition-all",
                      isCurrent
                        ? "bg-[var(--blueprint-light)]/20 border-[var(--blueprint)]"
                        : "bg-[var(--surface)] border-[var(--structure-subtle)] hover:border-[var(--structure)]"
                    )}
                  >
                    <div className="flex items-start gap-2">
                      <div className="mt-0.5">
                        {isCompleted ? (
                          <CheckCircle size={16} className="text-[var(--success)]" />
                        ) : (
                          <div className={cn(
                            "w-4 h-4 rounded-full border-2",
                            isCurrent ? "border-[var(--blueprint)]" : "border-[var(--ink-ghost)]"
                          )} />
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <h4 className={cn(
                          "text-sm font-medium",
                          isCurrent ? "text-[var(--blueprint)]" : "text-[var(--ink)]"
                        )}>
                          {section.title}
                        </h4>
                        {section.required && (
                          <p className="text-xs text-[var(--ink-ghost)] mt-0.5">Required</p>
                        )}
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Editor */}
          <div className="flex-1 flex flex-col">
            {/* Current Section */}
            <div className="p-4 border-b border-[var(--structure-subtle)]">
              <h3 className="font-medium text-[var(--ink)]">
                {template.sections[currentSection].title}
              </h3>
              <p className="text-sm text-[var(--ink-muted)] mt-1">
                {template.sections[currentSection].prompt}
              </p>
            </div>

            {/* Text Area */}
            <div className="flex-1 p-4">
              <textarea
                value={values[template.sections[currentSection].id] || ''}
                onChange={(e) => handleValueChange(template.sections[currentSection].id, e.target.value)}
                placeholder={template.sections[currentSection].placeholder}
                className="w-full h-full p-3 text-sm bg-[var(--paper)] border border-[var(--structure-subtle)] rounded-[var(--radius)] focus:outline-none focus:border-[var(--blueprint)] resize-none placeholder:text-[var(--ink-ghost)]"
              />
            </div>

            {/* Navigation */}
            <div className="p-4 border-t border-[var(--structure-subtle)] flex justify-between">
              <BlueprintButton
                variant="secondary"
                disabled={currentSection === 0}
                onClick={() => setCurrentSection(Math.max(0, currentSection - 1))}
              >
                Previous
              </BlueprintButton>

              <BlueprintButton
                disabled={currentSection === template.sections.length - 1}
                onClick={() => setCurrentSection(Math.min(template.sections.length - 1, currentSection + 1))}
              >
                Next
              </BlueprintButton>
            </div>
          </div>

          {/* Tips Panel */}
          {showTips && template.conversionTips && (
            <div className="w-80 border-l border-[var(--structure-subtle)] bg-[var(--surface-subtle)] overflow-y-auto">
              <div className="p-4">
                <h4 className="font-medium text-[var(--ink)] mb-3 flex items-center gap-2">
                  <Lightbulb size={16} />
                  Conversion Tips
                </h4>
                <ul className="space-y-2">
                  {template.conversionTips.map((tip, index) => (
                    <li key={index} className="text-sm text-[var(--ink-muted)] flex items-start gap-2">
                      <span className="w-1.5 h-1.5 bg-[var(--blueprint)] rounded-full mt-1.5 shrink-0"></span>
                      {tip}
                    </li>
                  ))}
                </ul>

                {/* Placeholders Reference */}
                {template.placeholders && Object.keys(template.placeholders).length > 0 && (
                  <div className="mt-6">
                    <h4 className="font-medium text-[var(--ink)] mb-3">Placeholders</h4>
                    <div className="space-y-1">
                      {Object.entries(template.placeholders).map(([key, value]) => (
                        <div key={key} className="text-sm">
                          <span className="text-[var(--blueprint)] font-mono">[{key}]</span>
                          <span className="text-[var(--ink-muted)] ml-2">→ {value}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-[var(--structure-subtle)] flex justify-between items-center">
          <BlueprintButton variant="secondary" onClick={onClose}>
            Cancel
          </BlueprintButton>
          <BlueprintButton
            onClick={handleSubmit}
            disabled={!canSubmit()}
            className="flex items-center gap-2"
          >
            <Send size={16} />
            Generate Content
          </BlueprintButton>
        </div>
      </BlueprintCard>
    </div>
  );
}
