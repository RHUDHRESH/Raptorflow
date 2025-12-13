import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Plus,
  Sparkles,
  FileText,
  Mail,
  Video,
  BarChart,
  MessageSquare,
  CheckCircle2,
  Clock,
  Download,
  Copy,
  Edit,
  Trash2,
  Filter,
  Search,
  Grid3X3,
  List,
  Wand2,
  RefreshCw,
  X,
  ChevronRight
} from 'lucide-react'
import { useAuth } from '../../contexts/AuthContext'
import { museAPI } from '../../lib/api'

// Asset type categories and icons
const ASSET_CATEGORIES = {
  pillar: { label: 'Pillar Content', icon: FileText, color: 'purple' },
  micro: { label: 'Micro Content', icon: MessageSquare, color: 'blue' },
  sales: { label: 'Sales Enablement', icon: BarChart, color: 'amber' },
  lifecycle: { label: 'Lifecycle', icon: Mail, color: 'green' },
  abm: { label: 'ABM', icon: Video, color: 'cyan' },
  tools: { label: 'Tools & Calculators', icon: Sparkles, color: 'pink' },
  images: { label: 'Images & Visuals', icon: Wand2, color: 'rose' }
}

const ASSET_TYPES = [
  { type: 'pillar_webinar_script', label: 'Webinar Script', category: 'pillar', description: 'Full webinar presentation script' },
  { type: 'pillar_whitepaper', label: 'Whitepaper', category: 'pillar', description: 'Long-form educational content' },
  { type: 'linkedin_post', label: 'LinkedIn Post', category: 'micro', description: 'High-engagement social post' },
  { type: 'twitter_thread', label: 'Twitter Thread', category: 'micro', description: 'Multi-tweet thread format' },
  { type: 'email_sequence', label: 'Email Sequence', category: 'lifecycle', description: 'Multi-email nurture flow' },
  { type: 'onboarding_email', label: 'Onboarding Email', category: 'lifecycle', description: 'Activation-focused email' },
  { type: 'battlecard', label: 'Sales Battlecard', category: 'sales', description: 'Competitive positioning for sales' },
  { type: 'comparison_page', label: 'Comparison Page', category: 'sales', description: 'Us vs competitors content' },
  { type: 'case_study', label: 'Case Study', category: 'sales', description: 'Customer success story' },
  { type: 'roi_calculator_spec', label: 'ROI Calculator', category: 'tools', description: 'Value calculator specs' },
  { type: 'social_media_image', label: 'Social Media Image', category: 'images', description: 'Eye-catching visuals for social platforms' },
  { type: 'hero_banner', label: 'Hero Banner', category: 'images', description: 'Large banner images for websites' },
  { type: 'product_image', label: 'Product Image', category: 'images', description: 'Product photography and illustrations' },
  { type: 'brand_logo_concept', label: 'Logo Concept', category: 'images', description: 'Brand identity and logo designs' },
  { type: 'infographic', label: 'Infographic', category: 'images', description: 'Data visualization and information graphics' },
  { type: 'website_hero', label: 'Website Hero', category: 'images', description: 'Hero section images for landing pages' }
]

// Status configuration
const STATUS_CONFIG = {
  draft: { label: 'Draft', color: 'bg-white/10 text-white/60' },
  generating: { label: 'Generating', color: 'bg-purple-500/20 text-purple-400' },
  needs_review: { label: 'Needs Review', color: 'bg-amber-500/20 text-amber-400' },
  approved: { label: 'Approved', color: 'bg-emerald-500/20 text-emerald-400' },
  deployed: { label: 'Deployed', color: 'bg-blue-500/20 text-blue-400' },
  archived: { label: 'Archived', color: 'bg-white/10 text-white/40' }
}

// Asset card component
const AssetCard = ({ asset, onClick, onAction }) => {
  const category = ASSET_CATEGORIES[asset.category] || ASSET_CATEGORIES.pillar
  const statusConfig = STATUS_CONFIG[asset.status] || STATUS_CONFIG.draft
  const CategoryIcon = category.icon
  const isImageAsset = asset.category === 'images' || asset.asset_type?.includes('image')

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95 }}
      whileHover={{ y: -2 }}
      className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl overflow-hidden hover:border-white/20 transition-all group"
    >
      {/* Preview area */}
      <div
        className={`${isImageAsset ? 'h-48' : 'h-32'} bg-gradient-to-br from-white/5 to-white/0 p-4 cursor-pointer`}
        onClick={onClick}
      >
        {isImageAsset && asset.imageUrl ? (
          <div className="h-full flex flex-col">
            <div className="flex items-start justify-between mb-2">
              <div className={`w-8 h-8 rounded-lg bg-${category.color}-500/20 flex items-center justify-center`}>
                <CategoryIcon className={`w-4 h-4 text-${category.color}-400`} />
              </div>
              <span className={`px-2 py-0.5 rounded text-xs ${statusConfig.color}`}>
                {statusConfig.label}
              </span>
            </div>
            <div className="flex-1 rounded-lg overflow-hidden bg-white/10">
              <img
                src={asset.imageUrl}
                alt={asset.name}
                className="w-full h-full object-cover"
                onError={(e) => {
                  e.target.src = `data:image/svg+xml;base64,${btoa(`
                    <svg width="200" height="200" viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <rect width="200" height="200" fill="#1a1a1a"/>
                      <circle cx="100" cy="80" r="20" fill="#${category.color === 'rose' ? 'ec4899' : '8b5cf6'}"/>
                      <path d="M70 140 Q100 120 130 140" stroke="#${category.color === 'rose' ? 'ec4899' : '8b5cf6'}" stroke-width="3" fill="none"/>
                    </svg>
                  `)}`;
                }}
              />
            </div>
            <h3 className="font-medium text-white text-sm mt-2 line-clamp-1">{asset.name}</h3>
          </div>
        ) : (
          <>
            <div className="flex items-start justify-between">
              <div className={`w-10 h-10 rounded-lg bg-${category.color}-500/20 flex items-center justify-center`}>
                <CategoryIcon className={`w-5 h-5 text-${category.color}-400`} />
              </div>
              <span className={`px-2 py-0.5 rounded text-xs ${statusConfig.color}`}>
                {statusConfig.label}
              </span>
            </div>
            <div className="mt-3">
              <h3 className="font-medium text-white line-clamp-1">{asset.name}</h3>
              <p className="text-sm text-white/40 mt-1 line-clamp-2">
                {asset.content?.slice(0, 100) || 'Generated content...'}{asset.content?.length > 100 ? '...' : ''}
              </p>
            </div>
          </>
        )}
      </div>

      {/* Footer */}
      <div className="px-4 py-3 border-t border-white/10 flex items-center justify-between">
        <div className="text-xs text-white/40">
          {new Date(asset.created_at).toLocaleDateString()}
        </div>
        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <button 
            onClick={(e) => { e.stopPropagation(); onAction('copy', asset); }}
            className="p-1.5 hover:bg-white/10 rounded"
          >
            <Copy className="w-3.5 h-3.5 text-white/40" />
          </button>
          <button 
            onClick={(e) => { e.stopPropagation(); onAction('edit', asset); }}
            className="p-1.5 hover:bg-white/10 rounded"
          >
            <Edit className="w-3.5 h-3.5 text-white/40" />
          </button>
          <button 
            onClick={(e) => { e.stopPropagation(); onAction('download', asset); }}
            className="p-1.5 hover:bg-white/10 rounded"
          >
            <Download className="w-3.5 h-3.5 text-white/40" />
          </button>
        </div>
      </div>
    </motion.div>
  )
}

// Generate modal
const GenerateModal = ({ isOpen, onClose, onGenerate }) => {
  const [step, setStep] = useState(1)
  const [selectedType, setSelectedType] = useState(null)
  const [selectedICP, setSelectedICP] = useState(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [icps, setIcps] = useState([])
  const [loadingICPs, setLoadingICPs] = useState(false)
  const [imageStyle, setImageStyle] = useState('realistic')
  const [imageDimensions, setImageDimensions] = useState('square')

  // Fetch ICPs when modal opens
  useEffect(() => {
    if (isOpen && step === 2 && icps.length === 0) {
      fetchICPs()
    }
  }, [isOpen, step])

  const fetchICPs = async () => {
    setLoadingICPs(true)
    try {
      // TODO: Fetch ICPs from backend
      // For now, use mock data
      setIcps([
        { id: '1', label: 'Desperate Scaler', summary: 'Fast-growing startups seeking rapid growth' },
        { id: '2', label: 'Frustrated Optimizer', summary: 'Companies frustrated with current tools' },
        { id: '3', label: 'Risk Mitigator', summary: 'Conservative enterprises focused on stability' },
        { id: '4', label: 'Innovation Seeker', summary: 'Forward-thinking companies embracing change' },
        { id: '5', label: 'Cost Cutter', summary: 'Budget-conscious organizations' }
      ])
    } catch (error) {
      console.error('Error fetching ICPs:', error)
      // Fallback to basic ICPs
      setIcps([
        { id: '1', label: 'General Audience', summary: 'Broad target audience' }
      ])
    } finally {
      setLoadingICPs(false)
    }
  }

  const handleGenerate = async () => {
    setIsGenerating(true)
    // Simulate generation
    await new Promise(resolve => setTimeout(resolve, 2000))
    onGenerate({ asset_type: selectedType?.type, icp_id: selectedICP?.id })
    setIsGenerating(false)
    onClose()
    setStep(1)
    setSelectedType(null)
    setSelectedICP(null)
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="bg-[#0a0a0f] border border-white/10 rounded-2xl w-full max-w-3xl max-h-[80vh] overflow-hidden"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-white/10">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-lg flex items-center justify-center">
              <Wand2 className="w-5 h-5 text-purple-400" />
            </div>
            <div>
              <h2 className="text-xl font-medium text-white">Generate Asset</h2>
              <p className="text-sm text-white/40">Create content with Muse AI</p>
            </div>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-white/10 rounded-lg">
            <X className="w-5 h-5 text-white/60" />
          </button>
        </div>

        {/* Progress */}
        <div className="flex items-center gap-4 px-6 py-4 bg-white/5 border-b border-white/10">
          <div className={`flex items-center gap-2 ${step >= 1 ? 'text-white' : 'text-white/40'}`}>
            <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs ${step >= 1 ? 'bg-white/20' : 'bg-white/10'}`}>1</div>
            <span className="text-sm">Asset Type</span>
          </div>
          <ChevronRight className="w-4 h-4 text-white/20" />
          {ASSET_TYPES.find(t => t.type === selectedType?.type)?.category === 'images' && (
            <>
              <div className={`flex items-center gap-2 ${step >= 2 ? 'text-white' : 'text-white/40'}`}>
                <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs ${step >= 2 ? 'bg-white/20' : 'bg-white/10'}`}>2</div>
                <span className="text-sm">Image Style</span>
              </div>
              <ChevronRight className="w-4 h-4 text-white/20" />
              <div className={`flex items-center gap-2 ${step >= 3 ? 'text-white' : 'text-white/40'}`}>
                <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs ${step >= 3 ? 'bg-white/20' : 'bg-white/10'}`}>3</div>
                <span className="text-sm">Target ICP</span>
              </div>
              <ChevronRight className="w-4 h-4 text-white/20" />
              <div className={`flex items-center gap-2 ${step >= 4 ? 'text-white' : 'text-white/40'}`}>
                <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs ${step >= 4 ? 'bg-white/20' : 'bg-white/10'}`}>4</div>
                <span className="text-sm">Generate</span>
              </div>
            </>
          )}
          {(!selectedType || ASSET_TYPES.find(t => t.type === selectedType?.type)?.category !== 'images') && (
            <>
              <div className={`flex items-center gap-2 ${step >= 2 ? 'text-white' : 'text-white/40'}`}>
                <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs ${step >= 2 ? 'bg-white/20' : 'bg-white/10'}`}>2</div>
                <span className="text-sm">Target ICP</span>
              </div>
              <ChevronRight className="w-4 h-4 text-white/20" />
              <div className={`flex items-center gap-2 ${step >= 3 ? 'text-white' : 'text-white/40'}`}>
                <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs ${step >= 3 ? 'bg-white/20' : 'bg-white/10'}`}>3</div>
                <span className="text-sm">Generate</span>
              </div>
            </>
          )}
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[50vh]">
          {step === 1 && (
            <div className="space-y-4">
              {Object.entries(ASSET_CATEGORIES).map(([key, category]) => {
                const types = ASSET_TYPES.filter(t => t.category === key)
                const CategoryIcon = category.icon
                
                return (
                  <div key={key}>
                    <div className="flex items-center gap-2 mb-3">
                      <CategoryIcon className={`w-4 h-4 text-${category.color}-400`} />
                      <span className="text-sm font-medium text-white/60">{category.label}</span>
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                      {types.map(type => (
                        <button
                          key={type.type}
                          onClick={() => setSelectedType(type)}
                          className={`p-3 rounded-lg border text-left transition-all ${
                            selectedType?.type === type.type
                              ? 'bg-white/10 border-white/30'
                              : 'bg-white/5 border-white/10 hover:border-white/20'
                          }`}
                        >
                          <div className="font-medium text-white text-sm">{type.label}</div>
                          <div className="text-xs text-white/40 mt-1">{type.description}</div>
                        </button>
                      ))}
                    </div>
                  </div>
                )
              })}
            </div>
          )}

          {step === 2 && (
            <div className="space-y-3">
              <p className="text-sm text-white/60 mb-4">
                Select which ICP this content should be tailored for
              </p>
              {loadingICPs ? (
                <div className="text-center py-8">
                  <RefreshCw className="w-6 h-6 text-purple-400 animate-spin mx-auto mb-2" />
                  <p className="text-white/60">Loading audience profiles...</p>
                </div>
              ) : (
                icps.map(icp => (
                  <button
                    key={icp.id}
                    onClick={() => setSelectedICP(icp)}
                    className={`w-full p-4 rounded-lg border text-left transition-all ${
                      selectedICP?.id === icp.id
                        ? 'bg-white/10 border-white/30'
                        : 'bg-white/5 border-white/10 hover:border-white/20'
                    }`}
                  >
                    <div className="font-medium text-white">{icp.label}</div>
                    <div className="text-sm text-white/40 mt-1">{icp.summary}</div>
                  </button>
                ))
              )}
            </div>
          )}

          {step === 2 && ASSET_TYPES.find(t => t.type === selectedType?.type)?.category === 'images' && (
            <div className="space-y-4">
              <p className="text-sm text-white/60 mb-4">
                Customize your image settings
              </p>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-white mb-2">Visual Style</label>
                  <select
                    value={imageStyle}
                    onChange={(e) => setImageStyle(e.target.value)}
                    className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white focus:border-white/30 outline-none"
                  >
                    <option value="realistic">Realistic (Photography)</option>
                    <option value="illustrative">Illustrative (Clean Art)</option>
                    <option value="minimalist">Minimalist (Simple)</option>
                    <option value="bold">Bold (Vibrant)</option>
                    <option value="vibrant">Vibrant (Colorful)</option>
                    <option value="monochrome">Monochrome (B&W)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-white mb-2">Dimensions</label>
                  <select
                    value={imageDimensions}
                    onChange={(e) => setImageDimensions(e.target.value)}
                    className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white focus:border-white/30 outline-none"
                  >
                    <option value="square">Square (1:1) - Social Media</option>
                    <option value="landscape">Landscape (16:9) - Banners</option>
                    <option value="portrait">Portrait (9:16) - Stories</option>
                    <option value="banner">Banner (3:1) - Headers</option>
                  </select>
                </div>
              </div>
            </div>
          )}

          {step === (ASSET_TYPES.find(t => t.type === selectedType?.type)?.category === 'images' ? 3 : 2) && (
            <div className="text-center py-8">
              {isGenerating ? (
                <div>
                  <div className="w-16 h-16 bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-2xl flex items-center justify-center mx-auto mb-4">
                    <RefreshCw className="w-8 h-8 text-purple-400 animate-spin" />
                  </div>
                  <h3 className="text-lg font-medium text-white mb-2">Generating your asset...</h3>
                  <p className="text-white/40">
                    Creating {selectedType?.label} for {selectedICP?.label}
                  </p>
                </div>
              ) : (
                <div>
                  <div className={`w-16 h-16 ${ASSET_TYPES.find(t => t.type === selectedType?.type)?.category === 'images' ? 'bg-gradient-to-br from-rose-500/20 to-pink-500/20' : 'bg-gradient-to-br from-purple-500/20 to-pink-500/20'} rounded-2xl flex items-center justify-center mx-auto mb-4`}>
                    {ASSET_TYPES.find(t => t.type === selectedType?.type)?.category === 'images' ? (
                      <Wand2 className="w-8 h-8 text-rose-400" />
                    ) : (
                      <Sparkles className="w-8 h-8 text-purple-400" />
                    )}
                  </div>
                  <h3 className="text-lg font-medium text-white mb-2">Ready to generate</h3>
                  <p className="text-white/40 mb-6">
                    {selectedType?.label} tailored for {selectedICP?.label}
                    {ASSET_TYPES.find(t => t.type === selectedType?.type)?.category === 'images' && (
                      <span className="block text-sm mt-1">
                        Style: {imageStyle} • Dimensions: {imageDimensions}
                      </span>
                    )}
                  </p>
                  <button
                    onClick={handleGenerate}
                    className="px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-lg font-medium hover:opacity-90 transition-opacity flex items-center gap-2 mx-auto"
                  >
                    <Wand2 className="w-4 h-4" />
                    Generate with Muse
                  </button>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        {step < (ASSET_TYPES.find(t => t.type === selectedType?.type)?.category === 'images' ? 3 : 2) && (
          <div className="flex items-center justify-between p-6 border-t border-white/10 bg-white/5">
            <button
              onClick={() => step === 1 ? onClose() : setStep(s => s - 1)}
              className="px-4 py-2 text-white/60 hover:text-white transition-colors"
            >
              {step === 1 ? 'Cancel' : 'Back'}
            </button>
            <button
              onClick={() => setStep(s => s + 1)}
              disabled={
                (step === 1 && !selectedType) ||
                (step === 2 && ASSET_TYPES.find(t => t.type === selectedType?.type)?.category !== 'images' && !selectedICP)
              }
              className="px-6 py-2 bg-white text-black rounded-lg font-medium hover:bg-white/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Continue
            </button>
          </div>
        )}
      </motion.div>
    </div>
  )
}

// Main Muse page
const Muse = () => {
  const { user, profile } = useAuth()
  const [assets, setAssets] = useState([])
  const [loading, setLoading] = useState(true)
  const [view, setView] = useState('grid')
  const [filter, setFilter] = useState('all')
  const [categoryFilter, setCategoryFilter] = useState('all')
  const [search, setSearch] = useState('')
  const [showGenerateModal, setShowGenerateModal] = useState(false)

  useEffect(() => {
    const fetchAssets = async () => {
      setLoading(true)
      try {
        // TODO: Implement asset storage and retrieval
        // For now, start with empty assets list
        setAssets([])
      } catch (error) {
        console.error('Error fetching assets:', error)
        setAssets([])
      } finally {
        setLoading(false)
      }
    }

    fetchAssets()
  }, [])

  const handleGenerate = async (data) => {
    try {
      // Create generating asset placeholder
      const generatingAsset = {
        id: `temp-${Date.now()}`,
        name: `Generating ${ASSET_TYPES.find(t => t.type === data.asset_type)?.label || 'Asset'}`,
        asset_type: data.asset_type,
        category: ASSET_TYPES.find(t => t.type === data.asset_type)?.category || 'pillar',
        status: 'generating',
        content: 'AI is crafting your content...',
        created_at: new Date().toISOString()
      }
      setAssets([generatingAsset, ...assets])

      // Call orchestrator API
      const response = await museAPI.generateAsset(data.asset_type, data.icp_id, {
        asset_type: data.asset_type,
        icp_id: data.icp_id,
        brandProfileId: profile?.organization_id || profile?.id, // Use organization ID as brand profile ID
        inputOverrides: {
          style: ASSET_TYPES.find(t => t.type === data.asset_type)?.category === 'images' ? imageStyle : undefined,
          dimensions: ASSET_TYPES.find(t => t.type === data.asset_type)?.category === 'images' ? imageDimensions : undefined,
          brandColors: ['#6366f1', '#8b5cf6', '#ec4899'], // TODO: Get from brand profile
          targetAudience: selectedICP?.label,
          mood: 'professional',
          assetType: data.asset_type,
          // Additional generation parameters
        },
        contextSnapshot: {
          userId: user?.id,
          organizationId: profile?.organization_id,
          imageStyle: ASSET_TYPES.find(t => t.type === data.asset_type)?.category === 'images' ? imageStyle : undefined,
          imageDimensions: ASSET_TYPES.find(t => t.type === data.asset_type)?.category === 'images' ? imageDimensions : undefined,
          // Additional context
        }
      })

      const { job_id } = response.data

      // Poll for completion
      const pollForResult = async (jobId) => {
        try {
          const statusResponse = await museAPI.getGenerationStatus(jobId)

          if (statusResponse.data.status === 'completed' && statusResponse.data.asset) {
            // Replace generating asset with completed asset
            setAssets(prevAssets =>
              prevAssets.map(asset =>
                asset.id === generatingAsset.id ? statusResponse.data.asset : asset
              )
            )
          } else if (statusResponse.data.status === 'failed') {
            // Mark as failed
            setAssets(prevAssets =>
              prevAssets.map(asset =>
                asset.id === generatingAsset.id
                  ? { ...asset, status: 'failed', content: 'Generation failed. Please try again.' }
                  : asset
              )
            )
          } else {
            // Still processing, poll again
            setTimeout(() => pollForResult(jobId), 2000)
          }
        } catch (error) {
          console.error('Error polling for result:', error)
          setAssets(prevAssets =>
            prevAssets.map(asset =>
              asset.id === generatingAsset.id
                ? { ...asset, status: 'failed', content: 'Generation failed. Please try again.' }
                : asset
            )
          )
        }
      }

      // Start polling
      pollForResult(job_id)

    } catch (error) {
      console.error('Error generating asset:', error)
      // Remove failed generating asset
      setAssets(prevAssets => prevAssets.filter(asset => asset.id !== `temp-${Date.now()}`))
      // TODO: Show error toast
    }
  }

  const handleAssetAction = async (action, asset) => {
    switch (action) {
      case 'copy':
        try {
          if (asset.category === 'images') {
            // For images, copy the image URL
            await navigator.clipboard.writeText(asset.imageUrl || '')
          } else {
            // For text content, copy the text
            await navigator.clipboard.writeText(asset.content || '')
          }
          // TODO: Show success toast
        } catch (error) {
          console.error('Failed to copy:', error)
          // TODO: Show error toast
        }
        break
      case 'edit':
        console.log('Edit:', asset)
        // TODO: Open edit modal or navigate to editor
        break
      case 'download':
        try {
          if (asset.category === 'images') {
            // Download image directly
            const link = document.createElement('a')
            link.href = asset.imageUrl
            link.download = `${asset.name.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.png`
            document.body.appendChild(link)
            link.click()
            document.body.removeChild(link)
          } else {
            // Generate PDF from asset content
            const pdfResponse = await museAPI.generatePDF(asset.content, asset.name, asset.asset_type, {
              content: asset.content,
              title: asset.name,
              assetType: asset.asset_type,
              metadata: {
                generatedAt: asset.created_at,
                source: 'muse_page'
              }
            })

            if (pdfResponse.data.url) {
              // Download the PDF
              const link = document.createElement('a')
              link.href = pdfResponse.data.url
              link.download = `${asset.name.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.pdf`
              document.body.appendChild(link)
              link.click()
              document.body.removeChild(link)
            }
          }
        } catch (error) {
          console.error('Failed to download:', error)
          // TODO: Show error toast
        }
        break
      default:
        break
    }
  }

  // Filter assets
  const filteredAssets = assets.filter(asset => {
    if (filter !== 'all' && asset.status !== filter) return false
    if (categoryFilter !== 'all' && asset.category !== categoryFilter) return false
    if (search && !asset.name.toLowerCase().includes(search.toLowerCase())) return false
    return true
  })

  // Stats
  const stats = {
    total: assets.length,
    drafts: assets.filter(a => a.status === 'draft').length,
    approved: assets.filter(a => a.status === 'approved').length,
    deployed: assets.filter(a => a.status === 'deployed').length
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-xl flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-purple-400" />
            </div>
            <div>
              <h1 className="text-3xl font-light text-white">Muse</h1>
              <p className="text-white/40">AI-powered asset factory</p>
            </div>
          </div>
        </motion.div>

        <motion.button
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          whileHover={{ scale: 1.02 }}
          onClick={() => setShowGenerateModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-lg font-medium hover:opacity-90 transition-opacity"
        >
          <Wand2 className="w-4 h-4" />
          Generate
        </motion.button>
      </div>

      {/* Stats */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="grid grid-cols-4 gap-4 mb-8"
      >
        <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-4">
          <div className="text-2xl font-medium text-white">{stats.total}</div>
          <div className="text-sm text-white/40">Total Assets</div>
        </div>
        <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-4">
          <div className="text-2xl font-medium text-white">{stats.drafts}</div>
          <div className="text-sm text-white/40">Drafts</div>
        </div>
        <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-4">
          <div className="text-2xl font-medium text-white">{stats.approved}</div>
          <div className="text-sm text-white/40">Approved</div>
        </div>
        <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-4">
          <div className="text-2xl font-medium text-white">{stats.deployed}</div>
          <div className="text-sm text-white/40">Deployed</div>
        </div>
      </motion.div>

      {/* Toolbar */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15 }}
        className="flex items-center justify-between mb-6"
      >
        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/40" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search assets..."
            className="pl-10 pr-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white placeholder:text-white/30 focus:border-white/30 outline-none w-64"
          />
        </div>

        <div className="flex items-center gap-4">
          {/* Category filter */}
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white text-sm focus:border-white/30 outline-none"
          >
            <option value="all">All Categories</option>
            {Object.entries(ASSET_CATEGORIES).map(([key, cat]) => (
              <option key={key} value={key}>{cat.label}</option>
            ))}
          </select>

          {/* Status filter */}
          <div className="flex items-center gap-2">
            {['all', 'draft', 'approved', 'deployed'].map((status) => (
              <button
                key={status}
                onClick={() => setFilter(status)}
                className={`px-3 py-1.5 rounded-lg text-sm transition-colors ${
                  filter === status
                    ? 'bg-white/10 text-white'
                    : 'text-white/40 hover:text-white/60'
                }`}
              >
                {status.charAt(0).toUpperCase() + status.slice(1)}
              </button>
            ))}
          </div>

          {/* View toggle */}
          <div className="flex items-center bg-white/5 rounded-lg p-1">
            <button
              onClick={() => setView('grid')}
              className={`p-2 rounded ${view === 'grid' ? 'bg-white/10' : ''}`}
            >
              <Grid3X3 className={`w-4 h-4 ${view === 'grid' ? 'text-white' : 'text-white/40'}`} />
            </button>
            <button
              onClick={() => setView('list')}
              className={`p-2 rounded ${view === 'list' ? 'bg-white/10' : ''}`}
            >
              <List className={`w-4 h-4 ${view === 'list' ? 'text-white' : 'text-white/40'}`} />
            </button>
          </div>
        </div>
      </motion.div>

      {/* Assets grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3, 4, 5, 6].map(i => (
            <div key={i} className="h-48 bg-white/5 rounded-xl animate-pulse" />
          ))}
        </div>
      ) : filteredAssets.length > 0 ? (
        <div className={`grid ${view === 'grid' ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3' : 'grid-cols-1'} gap-4`}>
          <AnimatePresence mode="popLayout">
            {filteredAssets.map(asset => (
              <AssetCard
                key={asset.id}
                asset={asset}
                onClick={() => console.log('View asset:', asset)}
                onAction={handleAssetAction}
              />
            ))}
          </AnimatePresence>
        </div>
      ) : (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-16"
        >
          <div className="w-16 h-16 bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <Sparkles className="w-8 h-8 text-purple-400" />
          </div>
          <h3 className="text-lg font-medium text-white mb-2">No assets yet</h3>
          <p className="text-white/40 mb-6">Generate your first asset with Muse AI</p>
          <button
            onClick={() => setShowGenerateModal(true)}
            className="px-4 py-2 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-lg font-medium hover:opacity-90 transition-opacity"
          >
            Generate Asset
          </button>
        </motion.div>
      )}

      {/* Generate Modal */}
      <AnimatePresence>
        {showGenerateModal && (
          <GenerateModal
            isOpen={showGenerateModal}
            onClose={() => setShowGenerateModal(false)}
            onGenerate={handleGenerate}
          />
        )}
      </AnimatePresence>
    </div>
  )
}

export default Muse
