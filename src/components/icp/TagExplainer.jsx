/**
 * Tag Explainer Component
 * Shows which fields produced which tags with full transparency
 */

import { useState } from 'react';
import { Tag, X, Plus, Sparkles, AlertCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const TAG_CATEGORIES = {
  descriptive: { label: 'Descriptive', color: 'blue' },
  pain: { label: 'Pain Points', color: 'red' },
  desire: { label: 'Desires/Goals', color: 'green' },
  context: { label: 'Context', color: 'purple' },
  behavior: { label: 'Behavioral', color: 'orange' }
};

export default function TagExplainer({ 
  tags = [], 
  sources = {}, 
  onRemove, 
  onAdd, 
  readOnly = false 
}) {
  const [newTag, setNewTag] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('descriptive');
  const [showSources, setShowSources] = useState(true);

  const handleAddTag = () => {
    if (newTag.trim() && onAdd) {
      onAdd(newTag.trim(), selectedCategory);
      setNewTag('');
    }
  };

  const getCategoryColor = (category) => {
    const colors = {
      blue: 'bg-blue-100 text-blue-800 border-blue-200',
      red: 'bg-red-100 text-red-800 border-red-200',
      green: 'bg-green-100 text-green-800 border-green-200',
      purple: 'bg-purple-100 text-purple-800 border-purple-200',
      orange: 'bg-orange-100 text-orange-800 border-orange-200'
    };
    return colors[TAG_CATEGORIES[category]?.color] || colors.blue;
  };

  const getTagCategory = (tag) => {
    // Try to infer category from tag name or source data
    const tagLower = tag.toLowerCase();
    if (tagLower.includes('pain') || tagLower.includes('struggle') || tagLower.includes('problem')) {
      return 'pain';
    }
    if (tagLower.includes('want') || tagLower.includes('goal') || tagLower.includes('desire')) {
      return 'desire';
    }
    if (tagLower.includes('budget') || tagLower.includes('size') || tagLower.includes('stage')) {
      return 'context';
    }
    if (tagLower.includes('behavior') || tagLower.includes('action') || tagLower.includes('decision')) {
      return 'behavior';
    }
    return 'descriptive';
  };

  const groupedTags = tags.reduce((acc, tag) => {
    const category = getTagCategory(tag);
    if (!acc[category]) acc[category] = [];
    acc[category].push(tag);
    return acc;
  }, {});

  return (
    <div className="runway-card p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="font-serif text-2xl mb-1">Tag System</h3>
          <p className="text-sm text-neutral-600">
            {tags.length} tags • {Object.keys(groupedTags).length} categories
          </p>
        </div>
        <button
          onClick={() => setShowSources(!showSources)}
          className="text-sm text-neutral-600 underline hover:text-neutral-900"
        >
          {showSources ? 'Hide' : 'Show'} sources
        </button>
      </div>

      {/* Add new tag (if not read-only) */}
      {!readOnly && (
        <div className="mb-6 p-4 bg-neutral-50 rounded-lg">
          <h4 className="font-semibold text-sm mb-3">Add Custom Tag</h4>
          <div className="flex gap-2">
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-3 py-2 border-2 border-neutral-200 rounded-lg focus:outline-none focus:border-neutral-900"
            >
              {Object.entries(TAG_CATEGORIES).map(([key, { label }]) => (
                <option key={key} value={key}>{label}</option>
              ))}
            </select>
            <input
              type="text"
              value={newTag}
              onChange={(e) => setNewTag(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleAddTag()}
              placeholder="e.g., growth_focused"
              className="flex-1 px-3 py-2 border-2 border-neutral-200 rounded-lg focus:outline-none focus:border-neutral-900"
            />
            <button
              onClick={handleAddTag}
              disabled={!newTag.trim()}
              className="runway-button-secondary px-4 py-2 disabled:opacity-50"
            >
              <Plus className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Tags by category */}
      <div className="space-y-6">
        {Object.entries(groupedTags).map(([category, categoryTags]) => (
          <div key={category}>
            <div className="flex items-center gap-2 mb-3">
              <Tag className="w-4 h-4 text-neutral-500" />
              <h4 className="font-semibold text-sm uppercase tracking-wider text-neutral-600">
                {TAG_CATEGORIES[category]?.label || category}
              </h4>
              <span className="text-xs text-neutral-400">
                ({categoryTags.length})
              </span>
            </div>

            <div className="flex flex-wrap gap-2">
              {categoryTags.map((tag, index) => {
                const source = sources[tag];
                const hasSource = source && showSources;

                return (
                  <motion.div
                    key={`${tag}-${index}`}
                    initial={{ scale: 0.9, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    exit={{ scale: 0.9, opacity: 0 }}
                    className="group relative"
                  >
                    <span
                      className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm border ${getCategoryColor(category)}`}
                    >
                      {tag}
                      {!readOnly && onRemove && (
                        <button
                          onClick={() => onRemove(tag)}
                          className="w-4 h-4 rounded-full hover:bg-black/10 flex items-center justify-center transition-colors"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      )}
                    </span>

                    {/* Source tooltip */}
                    {hasSource && (
                      <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 hidden group-hover:block z-10">
                        <div className="bg-neutral-900 text-white text-xs rounded-lg p-3 shadow-lg max-w-xs whitespace-normal">
                          <p className="font-semibold mb-1">Source:</p>
                          <p className="text-neutral-300">
                            Field: <span className="text-white">{source.field}</span>
                          </p>
                          {source.value && (
                            <p className="text-neutral-300 mt-1">
                              Value: "{source.value}"
                            </p>
                          )}
                          <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 translate-y-1/2 w-2 h-2 bg-neutral-900 rotate-45" />
                        </div>
                      </div>
                    )}
                  </motion.div>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {/* Tag guidelines */}
      <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <div className="flex items-start gap-2">
          <Sparkles className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
          <div className="text-sm text-blue-900">
            <p className="font-semibold mb-1">Tag Best Practices</p>
            <ul className="text-xs text-blue-800 space-y-1">
              <li>• Use snake_case for consistency (e.g., growth_focused)</li>
              <li>• Be specific: "ai_ml_interested" beats "tech_savvy"</li>
              <li>• Include pain tags to enable Quick Wins matching</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Tag quality check */}
      {tags.length < 5 && (
        <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
          <div className="flex items-start gap-2">
            <AlertCircle className="w-4 h-4 text-yellow-600 mt-0.5 flex-shrink-0" />
            <p className="text-sm text-yellow-900">
              Consider adding more tags. Aim for 8-12 tags for effective targeting and Quick Wins matching.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

