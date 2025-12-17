import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  X, 
  Sparkles, 
  FileText, 
  Mail, 
  MessageSquare, 
  Layout,
  RefreshCw,
  Copy,
  Check,
  Loader2
} from 'lucide-react'
import useRaptorflowStore from '../store/raptorflowStore'

const ASSET_TYPES = [
  { id: 'post', label: 'Post', icon: FileText, description: 'Social media post' },
  { id: 'email', label: 'Email', icon: Mail, description: 'Email copy' },
  { id: 'dm', label: 'DM', icon: MessageSquare, description: 'Direct message' },
  { id: 'landing', label: 'Landing', icon: Layout, description: 'Landing page section' }
]

const MuseDrawer = () => {
  const { 
    museDrawerOpen, 
    museContext, 
    closeMuseDrawer, 
    generateAsset,
    getMove,
    getCampaign,
    canUseMuse,
    usage,
    getPlanLimits
  } = useRaptorflowStore()

  const [selectedType, setSelectedType] = useState('post')
  const [generatedContent, setGeneratedContent] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const [copied, setCopied] = useState(false)

  const move = museContext?.moveId ? getMove(museContext.moveId) : null
  const campaign = museContext?.campaignId ? getCampaign(museContext.campaignId) : null
  const planLimits = getPlanLimits()

  const handleGenerate = async () => {
    if (!canUseMuse()) {
      alert('You have reached your Muse generation limit for this month')
      return
    }

    setIsGenerating(true)
    
    // Simulate generation delay
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    const asset = generateAsset(
      museContext?.moveId || 'standalone',
      selectedType,
      move?.channel || 'linkedin'
    )
    
    setGeneratedContent(asset.content)
    setIsGenerating(false)
  }

  const handleCopy = () => {
    navigator.clipboard.writeText(generatedContent)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleRegenerate = () => {
    setGeneratedContent('')
    handleGenerate()
  }

  if (!museDrawerOpen) return null

  return (
    <AnimatePresence>
      {museDrawerOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-ink/20 z-40"
            onClick={closeMuseDrawer}
          />
          
          {/* Drawer */}
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 30, stiffness: 300 }}
            className="fixed right-0 top-0 h-full w-full max-w-lg bg-paper border-l border-border-light z-50 flex flex-col"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-border-light">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-signal-muted rounded-xl flex items-center justify-center">
                  <Sparkles className="w-5 h-5 text-primary" strokeWidth={1.5} />
                </div>
                <div>
                  <h2 className="font-serif text-xl text-ink">Muse</h2>
                  <p className="text-body-xs text-ink-400">Generate assets</p>
                </div>
              </div>
              <button
                onClick={closeMuseDrawer}
                className="p-2 text-ink-400 hover:text-ink hover:bg-paper-200 rounded-lg transition-editorial"
              >
                <X className="w-5 h-5" strokeWidth={1.5} />
              </button>
            </div>

            {/* Context info */}
            {(move || campaign) && (
              <div className="px-6 py-4 bg-paper-200 border-b border-border-light">
                <div className="text-body-xs text-ink-400 mb-1">Context</div>
                {move && (
                  <div className="text-body-sm text-ink font-medium">{move.name}</div>
                )}
                {campaign && !move && (
                  <div className="text-body-sm text-ink font-medium">{campaign.name}</div>
                )}
                {move && (
                  <div className="flex items-center gap-2 mt-1">
                    <span className="px-2 py-0.5 bg-paper-300 rounded text-body-xs text-ink-400 capitalize">
                      {move.channel}
                    </span>
                    <span className="px-2 py-0.5 bg-paper-300 rounded text-body-xs text-ink-400">
                      {move.cta}
                    </span>
                  </div>
                )}
              </div>
            )}

            {/* Asset type selector */}
            <div className="p-6 border-b border-border-light">
              <div className="text-body-xs text-ink-400 mb-3">Asset type</div>
              <div className="grid grid-cols-4 gap-2">
                {ASSET_TYPES.map(type => (
                  <button
                    key={type.id}
                    onClick={() => setSelectedType(type.id)}
                    className={`flex flex-col items-center gap-2 p-3 rounded-xl border transition-editorial ${
                      selectedType === type.id
                        ? 'border-primary bg-signal-muted'
                        : 'border-border hover:border-border-dark bg-paper'
                    }`}
                  >
                    <type.icon 
                      className={`w-5 h-5 ${selectedType === type.id ? 'text-primary' : 'text-ink-400'}`} 
                      strokeWidth={1.5} 
                    />
                    <span className={`text-body-xs ${selectedType === type.id ? 'text-primary' : 'text-ink-400'}`}>
                      {type.label}
                    </span>
                  </button>
                ))}
              </div>
            </div>

            {/* Content area */}
            <div className="flex-1 p-6 overflow-auto">
              {!generatedContent && !isGenerating && (
                <div className="h-full flex flex-col items-center justify-center text-center">
                  <div className="w-16 h-16 bg-paper-200 rounded-2xl flex items-center justify-center mb-4">
                    <Sparkles className="w-8 h-8 text-ink-300" strokeWidth={1.5} />
                  </div>
                  <h3 className="font-serif text-lg text-ink mb-2">Ready to generate</h3>
                  <p className="text-body-sm text-ink-400 max-w-xs">
                    Select an asset type and click generate to create content based on your strategy and move context.
                  </p>
                </div>
              )}

              {isGenerating && (
                <div className="h-full flex flex-col items-center justify-center text-center">
                  <Loader2 className="w-8 h-8 text-primary animate-spin mb-4" strokeWidth={1.5} />
                  <h3 className="font-serif text-lg text-ink mb-2">Generating...</h3>
                  <p className="text-body-sm text-ink-400">
                    Creating your {selectedType} asset
                  </p>
                </div>
              )}

              {generatedContent && !isGenerating && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-body-xs text-ink-400">Generated content</span>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={handleRegenerate}
                        className="flex items-center gap-1 px-3 py-1.5 text-body-xs text-ink-400 hover:text-ink rounded-lg hover:bg-paper-200 transition-editorial"
                      >
                        <RefreshCw className="w-3.5 h-3.5" strokeWidth={1.5} />
                        Regenerate
                      </button>
                      <button
                        onClick={handleCopy}
                        className="flex items-center gap-1 px-3 py-1.5 text-body-xs text-primary hover:bg-signal-muted rounded-lg transition-editorial"
                      >
                        {copied ? (
                          <>
                            <Check className="w-3.5 h-3.5" strokeWidth={1.5} />
                            Copied
                          </>
                        ) : (
                          <>
                            <Copy className="w-3.5 h-3.5" strokeWidth={1.5} />
                            Copy
                          </>
                        )}
                      </button>
                    </div>
                  </div>
                  <div className="p-4 bg-paper-200 border border-border rounded-xl">
                    <pre className="whitespace-pre-wrap text-body-sm text-ink font-sans">
                      {generatedContent}
                    </pre>
                  </div>
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="p-6 border-t border-border-light bg-paper">
              <div className="flex items-center justify-between mb-4">
                <span className="text-body-xs text-ink-400">
                  {usage.museGenerationsThisMonth} / {planLimits.museGenerationsPerMonth} generations this month
                </span>
              </div>
              <button
                onClick={handleGenerate}
                disabled={isGenerating || !canUseMuse()}
                className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-primary text-primary-foreground rounded-xl font-medium hover:opacity-95 transition-editorial disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" strokeWidth={1.5} />
                    Generating...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" strokeWidth={1.5} />
                    Generate {selectedType}
                  </>
                )}
              </button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}

export default MuseDrawer
