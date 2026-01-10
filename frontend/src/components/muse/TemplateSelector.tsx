"use client";

import { useState } from 'react';
import { Search, X, Clock, TrendingUp, Star } from 'lucide-react';
import { ALL_TEMPLATES, TEMPLATE_CATEGORIES, TEMPLATE_TYPES, Template } from '@/lib/museTemplates';
import { BlueprintCard } from '@/components/ui/BlueprintCard';
import { BlueprintButton } from '@/components/ui/BlueprintButton';
import { BlueprintBadge } from '@/components/ui/BlueprintBadge';
import { cn } from '@/lib/utils';

interface TemplateSelectorProps {
  onSelect: (template: Template) => void;
  onClose: () => void;
}

export function TemplateSelector({ onSelect, onClose }: TemplateSelectorProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedType, setSelectedType] = useState<string>('all');

  const filteredTemplates = ALL_TEMPLATES.filter(template => {
    const matchesSearch = template.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         template.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         template.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));

    const matchesCategory = selectedCategory === 'all' || template.category === selectedCategory;
    const matchesType = selectedType === 'all' || template.type === selectedType;

    return matchesSearch && matchesCategory && matchesType;
  });

  const handleTemplateSelect = (template: Template) => {
    onSelect(template);
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <BlueprintCard className="w-full max-w-4xl max-h-[80vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-[var(--structure-subtle)]">
          <h2 className="text-lg font-semibold text-[var(--ink)]">Choose a Template</h2>
          <button
            onClick={onClose}
            className="p-1 hover:bg-[var(--surface)] rounded text-[var(--ink-muted)]"
          >
            <X size={20} />
          </button>
        </div>

        {/* Search and Filters */}
        <div className="p-4 space-y-3 border-b border-[var(--structure-subtle)]">
          {/* Search */}
          <div className="relative">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--ink-muted)]" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search templates..."
              className="w-full pl-10 pr-3 py-2 text-sm bg-[var(--paper)] border border-[var(--structure-subtle)] rounded-[var(--radius)] focus:outline-none focus:border-[var(--blueprint)] placeholder:text-[var(--ink-ghost)]"
            />
          </div>

          {/* Filters */}
          <div className="flex gap-3">
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="flex-1 text-sm bg-[var(--paper)] border border-[var(--structure-subtle)] rounded-[var(--radius)] px-3 py-2 focus:outline-none focus:border-[var(--blueprint)]"
            >
              <option value="all">All Categories</option>
              {TEMPLATE_CATEGORIES.map(cat => (
                <option key={cat.id} value={cat.id}>
                  {cat.icon} {cat.label}
                </option>
              ))}
            </select>

            <select
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
              className="flex-1 text-sm bg-[var(--paper)] border border-[var(--structure-subtle)] rounded-[var(--radius)] px-3 py-2 focus:outline-none focus:border-[var(--blueprint)]"
            >
              <option value="all">All Types</option>
              {TEMPLATE_TYPES.map(type => (
                <option key={type.id} value={type.id}>
                  {type.icon} {type.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Templates Grid */}
        <div className="flex-1 overflow-y-auto p-4">
          {filteredTemplates.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-[var(--ink-muted)]">No templates found</p>
              <p className="text-sm text-[var(--ink-ghost)] mt-1">Try adjusting your filters</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {filteredTemplates.map((template) => (
                <div
                  key={template.id}
                  onClick={() => handleTemplateSelect(template)}
                  className="p-4 bg-[var(--surface)] border border-[var(--structure-subtle)] rounded-[var(--radius)] cursor-pointer hover:border-[var(--blueprint)] transition-all group"
                >
                  {/* Header */}
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <h3 className="font-medium text-[var(--ink)] group-hover:text-[var(--blueprint)] transition-colors">
                        {template.title}
                      </h3>
                      <p className="text-sm text-[var(--ink-muted)] mt-1">
                        {template.description}
                      </p>
                    </div>
                    <div className="ml-2">
                      <BlueprintBadge variant="default" size="sm">
                        {template.type}
                      </BlueprintBadge>
                    </div>
                  </div>

                  {/* Meta Info */}
                  <div className="flex items-center gap-4 text-xs text-[var(--ink-ghost)] mb-3">
                    {template.estimatedReadTime && (
                      <div className="flex items-center gap-1">
                        <Clock size={12} />
                        <span>{template.estimatedReadTime} min read</span>
                      </div>
                    )}
                    <div className="flex items-center gap-1">
                      <TrendingUp size={12} />
                      <span>High conversion</span>
                    </div>
                  </div>

                  {/* Tags */}
                  <div className="flex flex-wrap gap-1 mb-3">
                    {template.tags.map(tag => (
                      <span
                        key={tag}
                        className="text-[10px] px-2 py-0.5 bg-[var(--blueprint-light)]/20 text-[var(--blueprint)] rounded"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>

                  {/* Sections Preview */}
                  <div className="text-xs text-[var(--ink-ghost)]">
                    <p className="font-medium text-[var(--ink-muted)] mb-1">Sections:</p>
                    <ul className="space-y-0.5">
                      {template.sections.slice(0, 3).map(section => (
                        <li key={section.id} className="flex items-center gap-1">
                          <span className="w-1 h-1 bg-[var(--ink-ghost)] rounded-full"></span>
                          {section.title}
                        </li>
                      ))}
                      {template.sections.length > 3 && (
                        <li className="text-[var(--ink-ghost)]">+{template.sections.length - 3} more</li>
                      )}
                    </ul>
                  </div>

                  {/* Conversion Tips */}
                  {template.conversionTips && template.conversionTips.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-[var(--structure-subtle)]">
                      <div className="flex items-center gap-1 text-xs text-[var(--blueprint)]">
                        <Star size={12} />
                        <span className="font-medium">Pro Tips Available</span>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-[var(--structure-subtle)] flex justify-between items-center">
          <p className="text-sm text-[var(--ink-muted)]">
            {filteredTemplates.length} template{filteredTemplates.length !== 1 ? 's' : ''} found
          </p>
          <BlueprintButton onClick={onClose} variant="secondary">
            Cancel
          </BlueprintButton>
        </div>
      </BlueprintCard>
    </div>
  );
}
