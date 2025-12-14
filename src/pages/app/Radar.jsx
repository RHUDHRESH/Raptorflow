import React, { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Radar as RadarIcon,
  Search,
  TrendingUp,
  Zap,
  Clock,
  AlertTriangle,
  CheckCircle2,
  ExternalLink,
  Sparkles,
  Play,
  Copy,
  Filter,
  RefreshCw,
  ChevronRight,
  ChevronDown,
  Target,
  Eye,
  Send,
  Flame,
  Globe,
  Hash,
  Calendar,
  BarChart3,
  MessageSquare,
  Image,
  Video,
  FileText,
  Twitter,
  Instagram,
  Linkedin
} from 'lucide-react'

// Animated radar sweep
const RadarSweep = ({ isScanning }) => (
  <div className="relative w-64 h-64">
    {/* Radar circles */}
    <div className="absolute inset-0 flex items-center justify-center">
      {[1, 2, 3, 4].map((ring) => (
        <div
          key={ring}
          className="absolute rounded-full border border-amber-500/20"
          style={{
            width: `${ring * 25}%`,
            height: `${ring * 25}%`
          }}
        />
      ))}
    </div>

    {/* Sweep line */}
    {isScanning && (
      <motion.div
        className="absolute top-1/2 left-1/2 w-1/2 h-0.5 origin-left"
        style={{
          background: 'linear-gradient(90deg, rgba(245,158,11,0.8) 0%, transparent 100%)'
        }}
        animate={{ rotate: 360 }}
        transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
      />
    )}

    {/* Center dot */}
    <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-3 h-3 bg-amber-500 rounded-full" />

    {/* Blips */}
    {!isScanning && (
      <>
        <motion.div
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          className="absolute top-1/4 right-1/4 w-2 h-2 bg-emerald-400 rounded-full"
        />
        <motion.div
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="absolute bottom-1/3 left-1/3 w-2 h-2 bg-amber-400 rounded-full"
        />
        <motion.div
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="absolute top-1/3 left-1/4 w-2 h-2 bg-red-400 rounded-full"
        />
      </>
    )}
  </div>
)

// Urgency badge
const UrgencyBadge = ({ urgency }) => {
  const styles = {
    post_now: 'bg-red-500/20 text-red-400 border-red-500/30',
    within_hours: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
    within_day: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    this_week: 'bg-zinc-500/20 text-zinc-400 border-zinc-500/30'
  }

  const labels = {
    post_now: '🔥 Post NOW',
    within_hours: '⚡ Within Hours',
    within_day: '📅 Within Day',
    this_week: '📆 This Week'
  }

  return (
    <span className={`px-2 py-1 rounded-full text-xs border ${styles[urgency]}`}>
      {labels[urgency]}
    </span>
  )
}

// Opportunity card
const OpportunityCard = ({ opportunity, onGenerateContent, onExpand, isExpanded }) => {
  const riskColors = {
    safe: 'text-emerald-400',
    moderate: 'text-amber-400',
    sensitive: 'text-orange-400',
    avoid: 'text-red-400'
  }

  const formatIcons = {
    image_post: Image,
    video: Video,
    carousel: FileText,
    story: MessageSquare,
    reel: Play,
    thread: MessageSquare,
    blog: FileText,
    email: Send
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-zinc-900/50 border border-white/10 rounded-xl overflow-hidden hover:border-amber-500/30 transition-all"
    >
      <div className="p-5">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <UrgencyBadge urgency={opportunity.urgency} />
              <span className={`text-xs ${riskColors[opportunity.risk_level]}`}>
                {opportunity.risk_level === 'safe' ? '✓ Safe' : `⚠ ${opportunity.risk_level}`}
              </span>
            </div>
            <h3 className="text-lg font-medium text-white">{opportunity.title}</h3>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-2xl font-light text-amber-400">{opportunity.relevance_score}</span>
            <span className="text-xs text-white/40">match</span>
          </div>
        </div>

        {/* Description */}
        <p className="text-sm text-white/60 mb-4">{opportunity.description}</p>

        {/* Matching tags */}
        <div className="flex flex-wrap gap-1 mb-4">
          {opportunity.matching_tags.slice(0, 5).map((tag, i) => (
            <span key={i} className="px-2 py-0.5 bg-amber-500/10 rounded text-xs text-amber-400">
              <Hash className="w-3 h-3 inline mr-0.5" />
              {tag}
            </span>
          ))}
          {opportunity.matching_tags.length > 5 && (
            <span className="text-xs text-white/40">+{opportunity.matching_tags.length - 5} more</span>
          )}
        </div>

        {/* Content angles preview */}
        <div className="flex items-center gap-4 mb-4 text-xs text-white/40">
          <span className="flex items-center gap-1">
            <Sparkles className="w-3 h-3" />
            {opportunity.content_angles.length} content ideas
          </span>
          <span className="flex items-center gap-1">
            <Clock className="w-3 h-3" />
            Peak: {opportunity.peak_window}
          </span>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => onExpand(opportunity.id)}
            className="flex-1 py-2 bg-white/5 hover:bg-white/10 rounded-lg text-sm text-white/60 transition-colors flex items-center justify-center gap-2"
          >
            <Eye className="w-4 h-4" />
            {isExpanded ? 'Hide Details' : 'View Details'}
          </button>
          <button
            onClick={() => onGenerateContent(opportunity)}
            className="flex-1 py-2 bg-amber-500/20 hover:bg-amber-500/30 rounded-lg text-sm text-amber-400 transition-colors flex items-center justify-center gap-2"
          >
            <Zap className="w-4 h-4" />
            Generate Content
          </button>
        </div>
      </div>

      {/* Expanded content */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="border-t border-white/10"
          >
            <div className="p-5 space-y-4">
              {/* Content angles */}
              <div>
                <h4 className="text-sm font-medium text-white mb-3">Content Angles</h4>
                <div className="space-y-3">
                  {opportunity.content_angles.map((angle, i) => {
                    const FormatIcon = formatIcons[angle.format] || FileText
                    return (
                      <div key={i} className="p-3 bg-white/5 rounded-lg">
                        <div className="flex items-start justify-between mb-2">
                          <span className="text-white font-medium text-sm">{angle.angle}</span>
                          <span className={`text-xs px-2 py-0.5 rounded ${
                            angle.estimated_engagement === 'viral_potential' ? 'bg-amber-500/20 text-amber-400' :
                            angle.estimated_engagement === 'high' ? 'bg-emerald-500/20 text-emerald-400' :
                            'bg-zinc-500/20 text-zinc-400'
                          }`}>
                            {angle.estimated_engagement}
                          </span>
                        </div>
                        <p className="text-xs text-white/50 mb-2 italic">"{angle.hook}"</p>
                        <div className="flex items-center gap-3 text-xs text-white/40">
                          <span className="flex items-center gap-1">
                            <FormatIcon className="w-3 h-3" />
                            {angle.format.replace('_', ' ')}
                          </span>
                          <span>{angle.platforms.join(', ')}</span>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>

              {/* Sources */}
              <div>
                <h4 className="text-sm font-medium text-white mb-3">Sources</h4>
                <div className="space-y-2">
                  {opportunity.sources.map((source, i) => (
                    <a
                      key={i}
                      href={source.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center justify-between p-2 bg-white/5 rounded-lg hover:bg-white/10 transition-colors"
                    >
                      <div className="flex items-center gap-2">
                        <Globe className="w-4 h-4 text-white/40" />
                        <span className="text-sm text-white/60">{source.title}</span>
                        <span className="text-xs text-white/30">({source.source_type})</span>
                      </div>
                      <ExternalLink className="w-4 h-4 text-white/30" />
                    </a>
                  ))}
                </div>
              </div>

              {/* Timing */}
              <div className="flex items-center gap-6 text-sm">
                <div>
                  <span className="text-white/40">Peak Window:</span>
                  <span className="text-white ml-2">{opportunity.peak_window}</span>
                </div>
                <div>
                  <span className="text-white/40">Trend Decay:</span>
                  <span className="text-white ml-2">{opportunity.decay_estimate}</span>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

// Cohort selector
const CohortSelector = ({ cohorts, selectedCohort, onSelect }) => (
  <div className="flex items-center gap-2 overflow-x-auto pb-2">
    {cohorts.map((cohort) => (
      <button
        key={cohort.id}
        onClick={() => onSelect(cohort)}
        className={`
          flex items-center gap-2 px-4 py-2 rounded-lg whitespace-nowrap transition-all
          ${selectedCohort?.id === cohort.id
            ? 'bg-amber-500/20 border border-amber-500/50 text-amber-400'
            : 'bg-white/5 border border-white/10 text-white/60 hover:border-white/20'
          }
        `}
      >
        <Target className="w-4 h-4" />
        <span className="text-sm">{cohort.name}</span>
        <span className="text-xs text-white/40">{cohort.tags_count || 0} tags</span>
      </button>
    ))}
  </div>
)

// Main Radar component
const Radar = () => {
  const [isScanning, setIsScanning] = useState(false)
  const [opportunities, setOpportunities] = useState([])
  const [expandedOpportunity, setExpandedOpportunity] = useState(null)
  const [selectedCohort, setSelectedCohort] = useState(null)
  const [timeframe, setTimeframe] = useState('this_week')

  // Mock cohorts (replace with real data)
  const [cohorts, setCohorts] = useState([])

  const handleScan = async () => {
    if (!selectedCohort) return
    
    setIsScanning(true)
    setOpportunities([])

    // Simulate API call - replace with actual API call
    setTimeout(() => {
      // Mock opportunities
      setOpportunities([
        {
          id: '1',
          title: 'IPL 2024 Season Starting This Week',
          trend_type: 'cultural_event',
          description: 'The IPL cricket season is about to begin with massive viewership expected. Perfect opportunity for sports and entertainment content.',
          relevance_score: 92,
          urgency: 'post_now',
          matching_tags: ['sports', 'cricket', 'entertainment', 'india', 'youth'],
          content_angles: [
            {
              angle: 'IPL Predictions Contest',
              hook: '"Who will win IPL 2024? Drop your predictions 👇"',
              format: 'image_post',
              platforms: ['Instagram', 'Twitter'],
              estimated_engagement: 'viral_potential'
            },
            {
              angle: 'Match Day Watch Party',
              hook: '"How are you watching the first match? Tag your cricket buddy!"',
              format: 'story',
              platforms: ['Instagram'],
              estimated_engagement: 'high'
            }
          ],
          risk_level: 'safe',
          risk_notes: null,
          sources: [
            { title: 'IPL Schedule Released', url: '#', source_type: 'news' },
            { title: '#IPL2024 Trending', url: '#', source_type: 'twitter' }
          ],
          peak_window: 'Today 6-9 PM',
          decay_estimate: '2-3 weeks (throughout season)'
        },
        {
          id: '2',
          title: 'New ChatGPT Features Announced',
          trend_type: 'industry_news',
          description: 'OpenAI announced major updates to ChatGPT with new capabilities. Tech community is buzzing.',
          relevance_score: 78,
          urgency: 'within_hours',
          matching_tags: ['technology', 'AI', 'productivity', 'startups'],
          content_angles: [
            {
              angle: 'Feature Breakdown Thread',
              hook: '"ChatGPT just got a massive upgrade. Here\'s what it means for you 🧵"',
              format: 'thread',
              platforms: ['Twitter', 'LinkedIn'],
              estimated_engagement: 'high'
            }
          ],
          risk_level: 'safe',
          risk_notes: null,
          sources: [
            { title: 'OpenAI Blog Post', url: '#', source_type: 'news' }
          ],
          peak_window: 'Next 12 hours',
          decay_estimate: '2-3 days'
        }
      ])
      setIsScanning(false)
    }, 3000)
  }

  const handleGenerateContent = (opportunity) => {
    // Navigate to content generation or open modal
    console.log('Generate content for:', opportunity)
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h1 className="text-3xl font-light text-white flex items-center gap-3">
            <RadarIcon className="w-8 h-8 text-amber-400" />
            Radar
          </h1>
          <p className="text-white/40 mt-1">
            Detect trending opportunities that match your cohorts
          </p>
        </motion.div>

        <div className="flex items-center gap-3">
          <select
            value={timeframe}
            onChange={(e) => setTimeframe(e.target.value)}
            className="px-4 py-2 bg-zinc-900 border border-white/10 rounded-lg text-white text-sm focus:outline-none focus:border-amber-500/50"
          >
            <option value="today">Today</option>
            <option value="this_week">This Week</option>
            <option value="this_month">This Month</option>
          </select>

          <button
            onClick={handleScan}
            disabled={!selectedCohort || isScanning}
            className={`
              flex items-center gap-2 px-6 py-2.5 rounded-lg font-medium transition-all
              ${selectedCohort && !isScanning
                ? 'bg-amber-500 hover:bg-amber-400 text-black'
                : 'bg-white/10 text-white/30 cursor-not-allowed'
              }
            `}
          >
            {isScanning ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                Scanning...
              </>
            ) : (
              <>
                <RadarIcon className="w-4 h-4" />
                Scan Trends
              </>
            )}
          </button>
        </div>
      </div>

      {/* Cohort selector */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="mb-6"
      >
        <label className="text-sm text-white/40 mb-2 block">Select Cohort to Scan</label>
        {cohorts.length > 0 ? (
          <CohortSelector
            cohorts={cohorts}
            selectedCohort={selectedCohort}
            onSelect={setSelectedCohort}
          />
        ) : (
          <div className="p-6 bg-zinc-900/50 border border-white/10 rounded-xl text-center">
            <Target className="w-12 h-12 text-white/20 mx-auto mb-4" />
            <p className="text-white/40 mb-4">No cohorts created yet</p>
            <button className="px-4 py-2 bg-amber-500/20 text-amber-400 rounded-lg text-sm hover:bg-amber-500/30 transition-colors">
              Create Your First Cohort
            </button>
          </div>
        )}
      </motion.div>

      {/* Main content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Radar visualization */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="lg:col-span-1 bg-zinc-900/50 border border-white/10 rounded-xl p-6 flex flex-col items-center justify-center min-h-[400px]"
        >
          <RadarSweep isScanning={isScanning} />
          
          <div className="text-center mt-6">
            <p className="text-white/60 text-sm">
              {isScanning 
                ? 'Scanning news, social media, and trends...'
                : opportunities.length > 0
                  ? `${opportunities.length} opportunities found`
                  : 'Select a cohort and click Scan'
              }
            </p>
          </div>

          {/* Quick stats */}
          {opportunities.length > 0 && !isScanning && (
            <div className="grid grid-cols-3 gap-4 mt-6 w-full">
              <div className="text-center">
                <div className="text-2xl font-light text-red-400">
                  {opportunities.filter(o => o.urgency === 'post_now').length}
                </div>
                <div className="text-xs text-white/40">Post Now</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-light text-amber-400">
                  {opportunities.filter(o => o.urgency === 'within_hours').length}
                </div>
                <div className="text-xs text-white/40">Within Hours</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-light text-white">
                  {opportunities.filter(o => o.relevance_score >= 80).length}
                </div>
                <div className="text-xs text-white/40">High Match</div>
              </div>
            </div>
          )}
        </motion.div>

        {/* Opportunities list */}
        <div className="lg:col-span-2 space-y-4">
          {isScanning ? (
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="bg-zinc-900/50 border border-white/10 rounded-xl p-5 animate-pulse">
                  <div className="h-4 bg-white/10 rounded w-1/4 mb-4" />
                  <div className="h-6 bg-white/10 rounded w-3/4 mb-4" />
                  <div className="h-4 bg-white/10 rounded w-full mb-4" />
                  <div className="flex gap-2">
                    <div className="h-6 bg-white/10 rounded w-20" />
                    <div className="h-6 bg-white/10 rounded w-20" />
                  </div>
                </div>
              ))}
            </div>
          ) : opportunities.length > 0 ? (
            opportunities.map((opp) => (
              <OpportunityCard
                key={opp.id}
                opportunity={opp}
                onGenerateContent={handleGenerateContent}
                onExpand={setExpandedOpportunity}
                isExpanded={expandedOpportunity === opp.id}
              />
            ))
          ) : (
            <div className="bg-zinc-900/50 border border-white/10 rounded-xl p-12 text-center">
              <Flame className="w-12 h-12 text-white/20 mx-auto mb-4" />
              <p className="text-white/40 mb-2">No opportunities scanned yet</p>
              <p className="text-xs text-white/30">
                Select a cohort and click "Scan Trends" to find marketing opportunities
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Radar

