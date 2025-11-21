import { useState, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Plus, Tag } from 'lucide-react'
import { cn } from '../../utils/cn'

// 50+ predefined tags across categories
export const COHORTS_TAG_CATEGORIES = {
  Demographics: [
    'Enterprise (500+)', 'Mid-Market (100-500)', 'SMB (10-100)', 'Startup (1-10)',
    'Solo Founder', 'C-Suite', 'VP Level', 'Director Level', 'Manager Level',
    'North America', 'Europe', 'APAC', 'Remote-First', 'Hybrid', 'On-Site'
  ],
  Psychographics: [
    'Safety Seeker', 'Innovator', 'Early Adopter', 'Pragmatist', 'Skeptic',
    'Status-Driven', 'Value-Driven', 'Community-Oriented', 'Lone Wolf',
    'Risk-Averse', 'Risk-Tolerant', 'Data-Driven', 'Intuition-Driven'
  ],
  Behavioral: [
    'High Intent', 'Low Intent', 'Price Sensitive', 'Price Insensitive',
    'Quick Decision', 'Long Sales Cycle', 'Self-Service', 'High Touch',
    'High Volume', 'Low Volume', 'Churn Risk', 'Loyal', 'Switcher'
  ],
  Industry: [
    'SaaS', 'E-commerce', 'Healthcare', 'Finance', 'Education', 'Real Estate',
    'Manufacturing', 'Retail', 'Consulting', 'Agency', 'Non-Profit', 'Government'
  ],
  PainPoints: [
    'Scalability', 'Security', 'Integration', 'Cost Reduction', 'Efficiency',
    'Compliance', 'Data Management', 'Customer Retention', 'Acquisition',
    'Team Collaboration', 'Reporting', 'Automation', 'Migration'
  ],
  TechStack: [
    'No-Code', 'Low-Code', 'Full Stack', 'Cloud-Native', 'On-Premise',
    'API-First', 'Mobile-First', 'Legacy Systems', 'Modern Stack'
  ],
  Budget: [
    '$0-$10k', '$10k-$50k', '$50k-$200k', '$200k-$500k', '$500k+',
    'Bootstrapped', 'VC-Backed', 'Enterprise Budget', 'Department Budget'
  ],
  Engagement: [
    'High Engagement', 'Low Engagement', 'Power User', 'Casual User',
    'Champion', 'Influencer', 'Gatekeeper', 'End User', 'Decision Maker'
  ]
}

export const ALL_TAGS = Object.values(COHORTS_TAG_CATEGORIES).flat()

export default function CohortsTagSystem({ selectedTags = [], onChange, maxTags = 20 }) {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [showTagPicker, setShowTagPicker] = useState(false)

  const filteredTags = useMemo(() => {
    let tags = ALL_TAGS

    // Filter by category
    if (selectedCategory !== 'all') {
      tags = COHORTS_TAG_CATEGORIES[selectedCategory] || []
    }

    // Filter by search
    if (searchQuery) {
      tags = tags.filter(tag => 
        tag.toLowerCase().includes(searchQuery.toLowerCase())
      )
    }

    // Exclude already selected tags
    return tags.filter(tag => !selectedTags.includes(tag))
  }, [searchQuery, selectedCategory, selectedTags])

  const handleAddTag = (tag) => {
    if (selectedTags.length < maxTags && !selectedTags.includes(tag)) {
      onChange([...selectedTags, tag])
    }
  }

  const handleRemoveTag = (tag) => {
    onChange(selectedTags.filter(t => t !== tag))
  }

  const getTagCategory = (tag) => {
    for (const [category, tags] of Object.entries(COHORTS_TAG_CATEGORIES)) {
      if (tags.includes(tag)) return category
    }
    return 'Other'
  }

  const getTagColor = (tag) => {
    const category = getTagCategory(tag)
    const colors = {
      Demographics: 'bg-blue-100 text-blue-900 border-blue-200',
      Psychographics: 'bg-purple-100 text-purple-900 border-purple-200',
      Behavioral: 'bg-green-100 text-green-900 border-green-200',
      Industry: 'bg-orange-100 text-orange-900 border-orange-200',
      PainPoints: 'bg-red-100 text-red-900 border-red-200',
      TechStack: 'bg-yellow-100 text-yellow-900 border-yellow-200',
      Budget: 'bg-indigo-100 text-indigo-900 border-indigo-200',
      Engagement: 'bg-pink-100 text-pink-900 border-pink-200'
    }
    return colors[category] || 'bg-neutral-100 text-neutral-900 border-neutral-200'
  }

  return (
    <div className="space-y-4">
      {/* Selected Tags */}
      <div className="flex flex-wrap gap-2">
        <AnimatePresence>
          {selectedTags.map((tag) => (
            <motion.div
              key={tag}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              transition={{ duration: 0.18 }}
              className={cn(
                "inline-flex items-center gap-2 px-3 py-1.5 rounded-lg border text-sm font-medium",
                getTagColor(tag)
              )}
            >
              <Tag className="w-3 h-3" />
              <span>{tag}</span>
              <button
                onClick={() => handleRemoveTag(tag)}
                className="hover:bg-black/10 rounded-full p-0.5 transition-colors duration-180"
              >
                <X className="w-3 h-3" />
              </button>
            </motion.div>
          ))}
        </AnimatePresence>

        {selectedTags.length < maxTags && (
          <button
            onClick={() => setShowTagPicker(!showTagPicker)}
            className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg border-2 border-dashed border-neutral-300 text-sm font-medium text-neutral-600 hover:border-neutral-900 hover:text-neutral-900 transition-all duration-180"
          >
            <Plus className="w-4 h-4" />
            Add Tag ({selectedTags.length}/{maxTags})
          </button>
        )}
      </div>

      {/* Tag Picker */}
      <AnimatePresence>
        {showTagPicker && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.18 }}
            className="runway-card p-4 space-y-4"
          >
            {/* Category Filter */}
            <div className="flex flex-wrap gap-2">
              {['all', ...Object.keys(COHORTS_TAG_CATEGORIES)].map((category) => (
                <button
                  key={category}
                  onClick={() => setSelectedCategory(category)}
                  className={cn(
                    "px-3 py-1.5 text-xs font-medium rounded-lg border transition-all duration-180",
                    selectedCategory === category
                      ? "border-neutral-900 bg-neutral-900 text-white"
                      : "border-neutral-200 bg-white text-neutral-700 hover:border-neutral-900"
                  )}
                >
                  {category}
                </button>
              ))}
            </div>

            {/* Search */}
            <input
              type="text"
              placeholder="Search tags..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-4 py-2 rounded-lg border border-neutral-200 focus:outline-none focus:ring-2 focus:ring-neutral-900"
            />

            {/* Tag List */}
            <div className="max-h-60 overflow-y-auto space-y-2">
              {filteredTags.length === 0 ? (
                <p className="text-sm text-neutral-500 text-center py-4">No tags found</p>
              ) : (
                filteredTags.map((tag) => (
                  <button
                    key={tag}
                    onClick={() => {
                      handleAddTag(tag)
                      if (selectedTags.length + 1 >= maxTags) {
                        setShowTagPicker(false)
                      }
                    }}
                    className={cn(
                      "w-full text-left px-3 py-2 rounded-lg border text-sm font-medium transition-all duration-180 hover:shadow-md",
                      getTagColor(tag)
                    )}
                  >
                    {tag}
                  </button>
                ))
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

