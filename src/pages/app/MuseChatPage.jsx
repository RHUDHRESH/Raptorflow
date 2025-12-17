import { useEffect, useMemo, useRef, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Sparkles,
  ArrowUpRight,
  Copy,
  Download,
  MoreHorizontal,
  X,
  ExternalLink,
  Paperclip,
  Trash2,
  ChevronDown,
  ChevronUp,
  Settings2,
  Square,
  CornerDownLeft,
  Check,
  Plus,
  Search,
  PanelRight,
  Pin,
  MessageSquareText,
  Pencil,
  Trash,
  FileText,
  History,
  Save,
  Undo2
} from 'lucide-react'
import { useAuth } from '../../contexts/AuthContext'
import useRaptorflowStore from '../../store/raptorflowStore'
import { museAPI } from '../../lib/api'
import { Modal } from '../../components/system/Modal'
 

const ASSET_REGISTRY = [
  // Content Creation
  { 
    category: 'Content',
    items: [
      { key: 'email', label: 'Email sequence', mode: 'native_text', backendAssetType: 'email_sequence' },
      { key: 'dm', label: 'DM / message template', mode: 'native_text', backendAssetType: 'linkedin_post' },
      { key: 'caption', label: 'Social caption', mode: 'native_text', backendAssetType: 'linkedin_post' },
      { key: 'blog-outline', label: 'Blog outline', mode: 'native_text', backendAssetType: 'pillar_whitepaper' },
      { key: 'one-liners', label: 'One-liners / elevator pitches', mode: 'native_text', backendAssetType: 'tagline' },
    ]
  },
  
  // Sales & Marketing
  {
    category: 'Sales & Marketing',
    items: [
      { key: 'sales-script', label: 'Sales script / call framework', mode: 'native_text', backendAssetType: 'battlecard' },
      { key: 'talking-points', label: 'Sales talking points', mode: 'native_text', backendAssetType: 'battlecard' },
      { key: 'landing-copy', label: 'Landing page copy', mode: 'native_text', backendAssetType: 'comparison_page' },
      { key: 'faq', label: 'FAQ section', mode: 'native_text', backendAssetType: 'comparison_page' },
      { key: 'video-script', label: 'Video script', mode: 'native_text', backendAssetType: 'pillar_webinar_script' },
    ]
  },
  
  // Design Assets
  {
    category: 'Design',
    items: [
      { key: 'instagram-post', label: 'Instagram post', mode: 'canva', backendAssetType: 'linkedin_post' },
      { key: 'instagram-carousel', label: 'Instagram carousel', mode: 'canva', backendAssetType: 'pillar_webinar_script' },
      { key: 'linkedin-carousel', label: 'LinkedIn carousel', mode: 'canva', backendAssetType: 'pillar_webinar_script' },
      { key: 'landing-hero', label: 'Landing page hero', mode: 'canva', backendAssetType: 'comparison_page' },
      { key: 'email-header', label: 'Email header', mode: 'canva', backendAssetType: 'comparison_page' },
    ]
  },
  
  // Advanced
  {
    category: 'Advanced',
    items: [
      { key: 'meme', label: 'Meme generator', mode: 'native_meme', backendAssetType: 'linkedin_post' },
      { key: 'ad-creative', label: 'Ad creative', mode: 'canva', backendAssetType: 'linkedin_post' },
      { key: 'presentation', label: 'Presentation deck', mode: 'canva', backendAssetType: 'pillar_webinar_script' },
      { key: 'lead-magnet', label: 'Lead magnet', mode: 'canva', backendAssetType: 'pillar_whitepaper' },
      { key: 'infographic', label: 'Infographic', mode: 'canva', backendAssetType: 'roi_calculator_spec' },
    ]
  }
]

const PROMPT_TEMPLATES = [
  {
    key: 'outline',
    label: 'Outline',
    detail: 'Turn the goal into a tight outline',
    template: 'Create a crisp outline with sections, bullets, and an explicit CTA. Keep it editorial and concrete.',
  },
  {
    key: 'rewrite',
    label: 'Rewrite (editorial)',
    detail: 'Rewrite with clarity, authority, and rhythm',
    template: 'Rewrite this with a premium editorial tone: clear, specific, no hype, short sentences where possible. Preserve meaning.',
  },
  {
    key: 'hooks',
    label: '5 hooks',
    detail: 'Generate multiple strong openings',
    template: 'Generate 5 hook options. Each should be punchy, specific, and avoid buzzwords. Provide 1 sentence per hook.',
  },
  {
    key: 'cta',
    label: 'CTA options',
    detail: 'Generate CTA variants',
    template: 'Generate 5 CTA options. Mix direct, curious, and low-friction CTAs. Keep them short.',
  },
]

const SKILL_REGISTRY = [
  {
    category: 'Analyze',
    items: [
      { key: 'analyze', label: 'Analyze content', description: 'Check tone and readability', icon: '🔍', kind: 'analyze' },
    ]
  },
  {
    category: 'Transform',
    items: [
      { key: 'shorten', label: 'Make concise', description: 'Shorten text while keeping key points', icon: '✂️', kind: 'transform' },
      { key: 'expand', label: 'Expand', description: 'Add more detail and depth', icon: '🔍', kind: 'transform' },
      { key: 'tone', label: 'Adjust tone', description: 'Change writing style', icon: '🎭', kind: 'transform' },
    ]
  },
  {
    category: 'Export',
    items: [
      { key: 'canva', label: 'To Canva', description: 'Design in Canva', icon: '🎨', kind: 'export' },
      { key: 'export', label: 'Export', description: 'Download as file', icon: '📥', kind: 'export' },
    ]
  }
]

function getGreeting() {
  const h = new Date().getHours()
  if (h < 12) return 'Good morning'
  if (h < 18) return 'Good afternoon'
  return 'Good evening'
}

function clamp(n, min, max) {
  return Math.min(max, Math.max(min, n))
}

function uniqBy(arr, keyFn) {
  const seen = new Set()
  const out = []
  for (const item of arr) {
    const key = keyFn(item)
    if (seen.has(key)) continue
    seen.add(key)
    out.push(item)
  }
  return out
}

function parseMentions(text) {
  const tokens = String(text || '').split(/\s+/).filter(Boolean)
  const at = []
  const slash = []
  for (const t of tokens) {
    if (t.startsWith('@')) at.push(t.slice(1))
    if (t.startsWith('/')) slash.push(t.slice(1))
  }
  return { at, slash }
}

function normalizeAssetKey(raw) {
  return String(raw || '')
    .trim()
    .toLowerCase()
    .replace(/^@/, '')
}

function inferSubjectLine(text) {
  const t = String(text || '').trim()
  if (!t) return ''
  const first = t.split(/\n+/)[0]
  return first.length > 90 ? `${first.slice(0, 90)}…` : first
}

function museName(profile) {
  const name = profile?.full_name || profile?.name || ''
  const first = String(name).trim().split(/\s+/)[0]
  return first || 'there'
}

function ShimmerBar() {
  return (
    <div className="relative h-3 w-full overflow-hidden rounded-full bg-paper-200 border border-border-light">
      <motion.div
        className="absolute inset-y-0 w-1/3 bg-gradient-to-r from-transparent via-white/70 to-transparent"
        animate={{ x: ['-40%', '140%'] }}
        transition={{ duration: 1.6, repeat: Infinity, ease: 'linear' }}
      />
    </div>
  )
}

function ProgressRow({ label, value }) {
  const pct = clamp(Math.round(Number(value || 0)), 0, 100)
  return (
    <div className="flex items-center justify-between text-[11px] text-ink-400">
      <span>{label}</span>
      <span className="font-mono">{pct}%</span>
    </div>
  )
}

function AssetCard({ asset, onOpen }) {
  const clickable = asset.status === 'complete'
  const a11yLabel = `${asset.title}. ${
    asset.status === 'generating'
      ? `Generating, ${Math.round(Number(asset.progress || 0))}% complete.`
      : asset.status === 'error'
        ? 'Generation failed.'
        : 'Ready. Activate to open.'
  }`

  return (
    <motion.button
      type="button"
      onClick={() => clickable && onOpen(asset.id)}
      disabled={!clickable}
      aria-disabled={!clickable}
      aria-label={a11yLabel}
      aria-busy={asset.status === 'generating' ? true : undefined}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`w-full text-left rounded-2xl border bg-card shadow-sm transition-editorial ${
        clickable
          ? 'border-border hover:border-border-dark hover:shadow-editorial cursor-pointer'
          : 'border-border-light opacity-95 cursor-default'
      }`}
    >
      <div className="p-5">
        <div className="flex items-start justify-between gap-4">
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <div className="w-9 h-9 rounded-xl bg-signal-muted border border-primary/20 flex items-center justify-center flex-shrink-0">
                <Sparkles className="w-4.5 h-4.5 text-primary" strokeWidth={1.5} />
              </div>
              <div className="min-w-0">
                <div className="text-body-xs text-ink-400">
                  {asset.status === 'generating' ? '✨ Generating…' : asset.status === 'error' ? 'Failed' : '✓ Ready'}
                </div>
                <div className="font-serif text-lg text-ink truncate">{asset.title}</div>
              </div>
            </div>
            <div className="mt-2 text-body-sm text-ink-400 line-clamp-2">{asset.subtitle}</div>
          </div>

          {asset.status === 'complete' && (
            <div className="flex items-center gap-1 text-body-xs text-primary flex-shrink-0">
              <span>Open</span>
              <ArrowUpRight className="w-4 h-4" strokeWidth={1.5} />
            </div>
          )}
        </div>

        {asset.status === 'generating' && (
          <div className="mt-4 space-y-3">
            <ShimmerBar />
            <div className="space-y-1.5">
              <ProgressRow label="Progress" value={asset.progress} />
              <div
                role="progressbar"
                aria-label="Generation progress"
                aria-valuemin={0}
                aria-valuemax={100}
                aria-valuenow={clamp(Math.round(Number(asset.progress || 0)), 0, 100)}
                aria-valuetext={`${clamp(Math.round(Number(asset.progress || 0)), 0, 100)}%`}
                className="sr-only"
              />
            </div>
          </div>
        )}

        {asset.status === 'error' && (
          <div className="mt-4 text-body-sm text-red-600">{asset.error || 'Generation failed. Try again.'}</div>
        )}
      </div>
    </motion.button>
  )
}

function ChatBubble({ role, children }) {
  const isUser = role === 'user'
  return (
    <div className={`group w-full flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`relative max-w-[min(92%,740px)] rounded-[14px] px-4 py-3 text-[15px] leading-[1.55] ${
          isUser
            ? 'bg-[rgba(0,0,0,0.04)] text-[var(--muse-text-primary)] border border-[var(--muse-border-soft)]'
            : 'bg-transparent text-[var(--muse-text-primary)]'
        }`}
      >
        <div className="max-w-none text-current">
          {children}
        </div>
      </div>
    </div>
  )
}

function TypingDots() {
  return (
    <div className="inline-flex items-center gap-1.5">
      <span className="w-1.5 h-1.5 rounded-full bg-current opacity-40 animate-bounce" style={{ animationDelay: '0ms' }} />
      <span className="w-1.5 h-1.5 rounded-full bg-current opacity-40 animate-bounce" style={{ animationDelay: '150ms' }} />
      <span className="w-1.5 h-1.5 rounded-full bg-current opacity-40 animate-bounce" style={{ animationDelay: '300ms' }} />
    </div>
  )
}

function safeJsonParse(raw, fallback) {
  try {
    return JSON.parse(raw)
  } catch {
    return fallback
  }
}

function downloadTextFile(filename, text) {
  const blob = new Blob([String(text || '')], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}

function nowIso() {
  return new Date().toISOString()
}

function truncateForPreview(text, maxChars = 800) {
  const s = String(text || '')
  if (s.length <= maxChars) return { preview: s, full: null }
  return { preview: s.slice(0, maxChars) + '…', full: s }
}

function createId(prefix = 'id') {
  return `${prefix}_${Date.now()}_${Math.random().toString(16).slice(2)}`
}

function defaultThreadName(firstMessage) {
  const s = String(firstMessage || '').trim().replace(/\s+/g, ' ')
  if (!s) return 'New chat'
  return s.length > 36 ? s.slice(0, 36) + '…' : s
}

function formatRelativeTime(iso) {
  if (!iso) return ''
  const ms = Date.now() - new Date(iso).getTime()
  if (!Number.isFinite(ms)) return ''
  const min = Math.floor(ms / 60000)
  if (min < 1) return 'now'
  if (min < 60) return `${min}m`
  const hr = Math.floor(min / 60)
  if (hr < 24) return `${hr}h`
  const d = Math.floor(hr / 24)
  return `${d}d`
}

function MuseChatPage() {
  const { user } = useAuth()
  const { addNotification } = useRaptorflowStore()

  const scrollRef = useRef(null)
  const inputRef = useRef(null)
  const fileInputRef = useRef(null)
  const abortRef = useRef(null)

  const STORAGE_KEY = 'rf.muse.chat.v2'

  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isAtBottom, setIsAtBottom] = useState(true)
  const [showRightPanel, setShowRightPanel] = useState(false)
  const [activeTab, setActiveTab] = useState('Artifacts')
  const [selectedModel, setSelectedModel] = useState('Muse (stub)')
  const [expandedById, setExpandedById] = useState(() => ({}))
  const [threadsQuery, setThreadsQuery] = useState('')
  const [editingThreadId, setEditingThreadId] = useState(null)
  const [draftThreadTitle, setDraftThreadTitle] = useState('')
  const [confirmDeleteThreadId, setConfirmDeleteThreadId] = useState(null)

  const [activeArtifactId, setActiveArtifactId] = useState(null)
  const [activeArtifactVersionId, setActiveArtifactVersionId] = useState(null)
  const [artifactDraftTitle, setArtifactDraftTitle] = useState('')
  const [artifactDraftContent, setArtifactDraftContent] = useState('')
  const [artifactRenameId, setArtifactRenameId] = useState(null)
  const [artifactRenameDraft, setArtifactRenameDraft] = useState('')
  const [confirmDeleteArtifactId, setConfirmDeleteArtifactId] = useState(null)

  const [pickerOpen, setPickerOpen] = useState(null)
  const [pickerQuery, setPickerQuery] = useState('')
  const [pickerIndex, setPickerIndex] = useState(0)

  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false)
  const [commandQuery, setCommandQuery] = useState('')
  const [commandIndex, setCommandIndex] = useState(0)

  const defaultWelcome = useMemo(() => {
    const first = user?.displayName?.split(' ')?.[0] || 'there'
    return {
      id: 'welcome',
      role: 'assistant',
      content: `Hi ${first}! I'm Muse, your AI content assistant. Tell me what you're trying to ship — and I’ll draft it while we chat.`,
      timestamp: new Date().toISOString(),
    }
  }, [user])

  const [threadsState, setThreadsState] = useState(() => {
    const raw = typeof window !== 'undefined' ? window.localStorage.getItem(STORAGE_KEY) : null
    const parsed = raw ? safeJsonParse(raw, null) : null
    if (parsed?.threadsById && parsed?.activeThreadId) return parsed

    const initialThreadId = createId('thread')
    return {
      version: 2,
      activeThreadId: initialThreadId,
      threadOrder: [initialThreadId],
      threadsById: {
        [initialThreadId]: {
          id: initialThreadId,
          title: 'Muse chat',
          updatedAt: new Date().toISOString(),
          selectedModel: 'Muse (stub)',
          activeCategory: 'Content',
          messages: [defaultWelcome],
          artifacts: [],
        },
      },
    }
  })

  const activeThread = threadsState?.threadsById?.[threadsState.activeThreadId]
  const messages = activeThread?.messages || [defaultWelcome]
  const threadArtifacts = activeThread?.artifacts || []

  const activeArtifact = useMemo(() => {
    if (!activeArtifactId) return null
    return threadArtifacts.find((a) => a.id === activeArtifactId) || null
  }, [threadArtifacts, activeArtifactId])

  const activeArtifactVersion = useMemo(() => {
    if (!activeArtifact) return null
    const versions = activeArtifact.versions || []
    const vid = activeArtifactVersionId || activeArtifact.currentVersionId || versions[0]?.id
    return versions.find((v) => v.id === vid) || versions[0] || null
  }, [activeArtifact, activeArtifactVersionId])

  const [activeAsset, setActiveAsset] = useState(null)
  const [activeSkill, setActiveSkill] = useState(null)
  const [isAssetModalOpen, setIsAssetModalOpen] = useState(false)
  const [isCanvaModalOpen, setIsCanvaModalOpen] = useState(false)
  const [isMemeModalOpen, setIsMemeModalOpen] = useState(false)
  const [activeCategory, setActiveCategory] = useState(() => activeThread?.activeCategory || 'Content')

  const closeAllModals = () => {
    setIsAssetModalOpen(false)
    setIsCanvaModalOpen(false)
    setIsMemeModalOpen(false)
    setActiveAsset(null)
  }
  
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus()
    }
  }, [])

  useEffect(() => {
    try {
      window.localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({
          ...threadsState,
          updatedAt: new Date().toISOString(),
        })
      )
    } catch {
      // ignore persistence failures
    }
  }, [threadsState])

  useEffect(() => {
    if (!activeThread) return
    setActiveCategory(activeThread.activeCategory || 'Content')
    setSelectedModel(activeThread.selectedModel || 'Muse (stub)')

    setActiveArtifactId(null)
    setActiveArtifactVersionId(null)
    setArtifactDraftTitle('')
    setArtifactDraftContent('')
    setArtifactRenameId(null)
    setArtifactRenameDraft('')
    setConfirmDeleteArtifactId(null)
  }, [threadsState.activeThreadId])

  useEffect(() => {
    if (!activeArtifact) return
    const title = String(activeArtifact.title || 'Draft')
    const content = String(activeArtifactVersion?.content || '')
    setArtifactDraftTitle(title)
    setArtifactDraftContent(content)
  }, [activeArtifactId, activeArtifactVersion?.id])

  const scrollToBottom = (behavior = 'smooth') => {
    const el = scrollRef.current
    if (!el) return
    el.scrollTo({ top: el.scrollHeight, behavior })
  }

  useEffect(() => {
    if (isAtBottom) {
      scrollToBottom(messages.length > 2 ? 'smooth' : 'auto')
    }
  }, [messages, isAtBottom])

  const activeAssets = useMemo(() => {
    const category = ASSET_REGISTRY.find(cat => cat.category === activeCategory)
    return category ? category.items : []
  }, [activeCategory])

  const createNewThread = () => {
    stopGenerating()
    const newId = createId('thread')
    setThreadsState((prev) => ({
      ...prev,
      activeThreadId: newId,
      threadOrder: [newId, ...prev.threadOrder],
      threadsById: {
        ...prev.threadsById,
        [newId]: {
          id: newId,
          title: 'New chat',
          updatedAt: new Date().toISOString(),
          selectedModel: prev.threadsById?.[prev.activeThreadId]?.selectedModel || 'Muse (stub)',
          activeCategory: prev.threadsById?.[prev.activeThreadId]?.activeCategory || 'Content',
          messages: [defaultWelcome],
          artifacts: [],
        },
      },
    }))
    setInput('')
    setTimeout(() => inputRef.current?.focus?.(), 0)
  }

  const COMMAND_ITEMS = useMemo(
    () => [
      { id: 'new-chat', label: 'New chat', detail: 'Start a new conversation', action: createNewThread },
      { id: 'search-chats', label: 'Search chats', detail: 'Find conversations', action: () => setThreadsQuery('') },
      {
        id: 'jump-artifacts',
        label: 'Jump to artifacts',
        detail: 'Open artifacts panel',
        action: () => {
          setActiveTab('Artifacts')
          setShowRightPanel(true)
        },
      },
      { id: 'export-chat', label: 'Export chat', detail: 'Download conversation as JSON', action: exportChat },
      { id: 'import-chat', label: 'Import chat', detail: 'Load conversation from JSON', action: () => fileInputRef.current?.click() },
      { id: 'clear-chat', label: 'Clear chat', detail: 'Start fresh conversation', action: clearChat },
      { id: 'toggle-panel', label: 'Toggle panel', detail: 'Show/hide right panel', action: () => setShowRightPanel((v) => !v) },
    ],
    [createNewThread, exportChat, clearChat]
  )

  const commandItems = useMemo(() => {
    const q = commandQuery.trim().toLowerCase()
    return q ? COMMAND_ITEMS.filter((i) => (i.label + ' ' + i.detail).toLowerCase().includes(q)) : COMMAND_ITEMS
  }, [commandQuery, COMMAND_ITEMS])

  const TOOL_ITEMS = useMemo(() => {
    const out = []
    for (const group of SKILL_REGISTRY) {
      for (const it of group.items) out.push({ ...it, group: group.category })
    }
    return out
  }, [])

  const pickerItems = useMemo(() => {
    const q = pickerQuery.trim().toLowerCase()

    if (pickerOpen === 'assets') {
      const cat = ASSET_REGISTRY.find((c) => c.category === activeCategory)
      const items = (cat?.items || []).map((a) => ({
        id: `asset:${a.key}`,
        label: a.label,
        detail: `@${a.key}`,
        value: a,
      }))
      return q ? items.filter((i) => i.label.toLowerCase().includes(q) || i.detail.toLowerCase().includes(q)) : items
    }

    if (pickerOpen === 'prompts') {
      const items = PROMPT_TEMPLATES.map((p) => ({
        id: `prompt:${p.key}`,
        label: p.label,
        detail: p.detail,
        value: p,
      }))
      return q ? items.filter((i) => (i.label + ' ' + i.detail).toLowerCase().includes(q)) : items
    }

    if (pickerOpen === 'tools') {
      const items = TOOL_ITEMS.map((t) => ({
        id: `tool:${t.key}`,
        label: t.label,
        detail: `${t.group} • &${t.key}`,
        value: t,
      }))
      return q ? items.filter((i) => (i.label + ' ' + i.detail).toLowerCase().includes(q)) : items
    }

    return []
  }, [pickerOpen, pickerQuery, activeCategory, PROMPT_TEMPLATES, TOOL_ITEMS])

  useEffect(() => {
    setPickerIndex(0)
  }, [pickerOpen, pickerQuery])

  const closePicker = () => {
    setPickerOpen(null)
    setPickerQuery('')
    setPickerIndex(0)
  }

  const closeCommandPalette = () => {
    setCommandPaletteOpen(false)
    setCommandQuery('')
    setCommandIndex(0)
  }

  const executeCommand = (item) => {
    if (!item) return
    item.action()
    closeCommandPalette()
  }

  const insertAtCursor = (text) => {
    const el = inputRef.current
    if (!el) {
      setInput((prev) => (prev ? prev + text : text))
      return
    }
    const start = el.selectionStart ?? input.length
    const end = el.selectionEnd ?? input.length
    const before = input.slice(0, start)
    const after = input.slice(end)
    const next = before + text + after
    setInput(next)
    setTimeout(() => {
      el.focus()
      const pos = start + text.length
      el.setSelectionRange(pos, pos)
    }, 0)
  }

  const applyPickerItem = (item) => {
    if (!item) return

    if (pickerOpen === 'assets') {
      const a = item.value
      insertAtCursor(`${input && !input.endsWith('\n') ? '\n' : ''}Create a ${a.label}.\n`)
      closePicker()
      return
    }

    if (pickerOpen === 'prompts') {
      const p = item.value
      insertAtCursor(`${input && !input.endsWith('\n') ? '\n' : ''}${p.template}\n`)
      closePicker()
      return
    }

    if (pickerOpen === 'tools') {
      const t = item.value
      insertAtCursor(`${input && !input.endsWith('\n') ? '\n' : ''}${t.label}: `)
      closePicker()
    }
  }

  const togglePinThread = (threadId) => {
    const t = threadsState.threadsById?.[threadId]
    if (!t) return
    setThreadPatch(threadId, { pinned: !t.pinned })
  }

  const beginRenameThread = (threadId) => {
    const t = threadsState.threadsById?.[threadId]
    if (!t) return
    setEditingThreadId(threadId)
    setDraftThreadTitle(t.title || 'Chat')
    setTimeout(() => {
      const el = document.getElementById(`muse-thread-rename-${threadId}`)
      el?.focus?.()
      el?.select?.()
    }, 0)
  }

  const commitRenameThread = () => {
    const threadId = editingThreadId
    if (!threadId) return
    const title = String(draftThreadTitle || '').trim() || 'Chat'
    setThreadPatch(threadId, { title })
    setEditingThreadId(null)
    setDraftThreadTitle('')
  }

  const deleteThread = (threadId) => {
    const exists = !!threadsState.threadsById?.[threadId]
    if (!exists) return

    stopGenerating()

    setThreadsState((prev) => {
      const nextThreadsById = { ...prev.threadsById }
      delete nextThreadsById[threadId]
      const nextOrder = prev.threadOrder.filter((id) => id !== threadId)

      let nextActive = prev.activeThreadId
      if (prev.activeThreadId === threadId) {
        nextActive = nextOrder[0] || null
      }

      if (!nextActive) {
        const newId = createId('thread')
        return {
          version: 2,
          activeThreadId: newId,
          threadOrder: [newId],
          threadsById: {
            [newId]: {
              id: newId,
              title: 'Muse chat',
              updatedAt: new Date().toISOString(),
              selectedModel: prev.threadsById?.[prev.activeThreadId]?.selectedModel || 'Muse (stub)',
              activeCategory: prev.threadsById?.[prev.activeThreadId]?.activeCategory || 'Content',
              messages: [defaultWelcome],
              artifacts: [],
            },
          },
        }
      }

      return {
        ...prev,
        activeThreadId: nextActive,
        threadOrder: nextOrder,
        threadsById: nextThreadsById,
      }
    })

    setConfirmDeleteThreadId(null)
    setEditingThreadId(null)
    setDraftThreadTitle('')
    addNotification?.({ level: 'success', title: 'Deleted', detail: 'Chat removed.' })
  }

  useEffect(() => {
    const onKeyDown = (e) => {
      const isMac = navigator.platform.toLowerCase().includes('mac')
      const mod = isMac ? e.metaKey : e.ctrlKey

      if (mod && e.key.toLowerCase() === 'k') {
        e.preventDefault()
        setCommandPaletteOpen(true)
        setCommandQuery('')
        return
      }

      if (mod && e.key.toLowerCase() === 'n') {
        e.preventDefault()
        createNewThread()
        return
      }

      if (e.key === 'Escape') {
        if (commandPaletteOpen) {
          closeCommandPalette()
          return
        }
        if (editingThreadId) {
          setEditingThreadId(null)
          setDraftThreadTitle('')
        }
        if (confirmDeleteThreadId) {
          setConfirmDeleteThreadId(null)
        }
      }
    }

    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [editingThreadId, confirmDeleteThreadId, commandPaletteOpen])

  const exportArtifact = (artifact) => {
    if (!artifact) return
    const versions = artifact.versions || []
    const current = versions.find((v) => v.id === artifact.currentVersionId) || versions[0]
    const content = current?.content || ''
    const base = String(artifact.title || 'muse-draft')
      .replace(/[^a-z0-9\-_\s]/gi, '')
      .trim()
      .replace(/\s+/g, '-')
    downloadTextFile(`${base || 'muse-draft'}.md`, content)
    addNotification?.({ level: 'success', title: 'Exported', detail: 'Artifact downloaded.' })
  }

  const createArtifactFromMessage = (message) => {
    const artifactId = createId('artifact')
    const vId = createId('v')
    const title = inferSubjectLine(message.content) || 'Muse draft'
    const artifact = {
      id: artifactId,
      title,
      type: activeCategory,
      createdAt: nowIso(),
      updatedAt: nowIso(),
      sourceMessageId: message.id,
      currentVersionId: vId,
      versions: [
        {
          id: vId,
          createdAt: nowIso(),
          content: String(message.content || ''),
        },
      ],
    }

    setThreadPatch(threadsState.activeThreadId, {
      artifacts: [artifact, ...threadArtifacts],
    })
    setActiveTab('Artifacts')
    setShowRightPanel(true)
    setActiveArtifactId(artifactId)
    setActiveArtifactVersionId(vId)
    addNotification?.({ level: 'success', title: 'Pinned', detail: 'Saved as an artifact draft.' })
  }

  const saveNewArtifactVersion = () => {
    if (!activeArtifact) return
    const title = String(artifactDraftTitle || 'Draft').trim() || 'Draft'
    const content = String(artifactDraftContent || '')
    const newVersionId = createId('v')

    const nextArtifact = {
      ...activeArtifact,
      title,
      updatedAt: nowIso(),
      currentVersionId: newVersionId,
      versions: [
        {
          id: newVersionId,
          createdAt: nowIso(),
          content,
        },
        ...(activeArtifact.versions || []),
      ],
    }

    setThreadPatch(threadsState.activeThreadId, {
      artifacts: [nextArtifact, ...threadArtifacts.filter((a) => a.id !== activeArtifact.id)],
    })
    setActiveArtifactVersionId(newVersionId)
    addNotification?.({ level: 'success', title: 'Saved', detail: 'New version created.' })
  }

  const revertToVersion = (versionId) => {
    setActiveArtifactVersionId(versionId)
    addNotification?.({ level: 'info', title: 'Version', detail: 'Switched version.' })
  }

  const beginRenameArtifact = (artifactId) => {
    const a = threadArtifacts.find((x) => x.id === artifactId)
    if (!a) return
    setArtifactRenameId(artifactId)
    setArtifactRenameDraft(a.title || 'Draft')
    setTimeout(() => {
      const el = document.getElementById(`muse-artifact-rename-${artifactId}`)
      el?.focus?.()
      el?.select?.()
    }, 0)
  }

  const commitRenameArtifact = () => {
    const id = artifactRenameId
    if (!id) return
    const nextTitle = String(artifactRenameDraft || '').trim() || 'Draft'
    const target = threadArtifacts.find((a) => a.id === id)
    if (!target) {
      setArtifactRenameId(null)
      setArtifactRenameDraft('')
      return
    }
    const patched = { ...target, title: nextTitle, updatedAt: nowIso() }
    setThreadPatch(threadsState.activeThreadId, {
      artifacts: [patched, ...threadArtifacts.filter((a) => a.id !== id)],
    })
    setArtifactRenameId(null)
    setArtifactRenameDraft('')
  }

  const deleteArtifact = (artifactId) => {
    const exists = threadArtifacts.some((a) => a.id === artifactId)
    if (!exists) return
    setThreadPatch(threadsState.activeThreadId, {
      artifacts: threadArtifacts.filter((a) => a.id !== artifactId),
    })
    if (activeArtifactId === artifactId) {
      setActiveArtifactId(null)
      setActiveArtifactVersionId(null)
      setArtifactDraftTitle('')
      setArtifactDraftContent('')
    }
    setConfirmDeleteArtifactId(null)
    addNotification?.({ level: 'success', title: 'Deleted', detail: 'Artifact removed.' })
  }

  const setThreadPatch = (threadId, patch) => {
    setThreadsState((prev) => {
      const t = prev.threadsById[threadId]
      if (!t) return prev
      return {
        ...prev,
        threadsById: {
          ...prev.threadsById,
          [threadId]: {
            ...t,
            ...patch,
            updatedAt: new Date().toISOString(),
          },
        },
      }
    })
  }

  const setActiveThreadId = (threadId) => {
    setThreadsState((prev) => ({ ...prev, activeThreadId: threadId }))
    setExpandedById({})
    setEditingThreadId(null)
    setDraftThreadTitle('')
    setIsAtBottom(true)
    setTimeout(() => scrollToBottom('auto'), 0)
  }

  const stopGenerating = () => {
    if (abortRef.current) {
      abortRef.current.abort?.()
    }
    setIsLoading(false)
    setThreadPatch(threadsState.activeThreadId, {
      messages: messages.map((m) => (m.id === 'typing' ? { ...m, isTyping: false } : m)),
    })
  }

  function clearChat() {
    stopGenerating()
    setExpandedById({})
    setThreadPatch(threadsState.activeThreadId, {
      messages: [defaultWelcome],
      artifacts: [],
    })
    setActiveArtifactId(null)
    setActiveArtifactVersionId(null)
    setInput('')
    setActiveCategory('Content')
    addNotification?.({ level: 'info', title: 'Muse cleared', detail: 'New conversation started.' })
    setTimeout(() => {
      scrollToBottom('auto')
      inputRef.current?.focus?.()
    }, 0)
  }

  function exportChat() {
    downloadTextFile(
      `muse-chat-${new Date().toISOString().slice(0, 19).replace(/[:T]/g, '-')}.json`,
      JSON.stringify({ ...threadsState }, null, 2)
    )
    addNotification?.({ level: 'success', title: 'Exported', detail: 'Downloaded conversation JSON.' })
  }

  const importChat = async () => {
    try {
      const file = fileInputRef.current?.files?.[0]
      if (!file) return
      const text = await file.text()
      const parsed = safeJsonParse(text, null)
      if (!parsed?.threadsById || !parsed?.activeThreadId) throw new Error('Invalid JSON file')
      setThreadsState(parsed)
      addNotification?.({ level: 'success', title: 'Imported', detail: 'Conversation loaded.' })
      setTimeout(() => scrollToBottom('auto'), 0)
    } catch (e) {
      addNotification?.({ level: 'error', title: 'Import failed', detail: 'Could not load conversation JSON.' })
    } finally {
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  const handleSubmit = async (e) => {
    e?.preventDefault?.()
    const text = input.trim()
    if (!text || isLoading) return

    const userMessage = {
      id: `user_${Date.now()}`,
      role: 'user',
      content: text,
      timestamp: new Date().toISOString(),
    }

    const typingId = 'typing'

    const threadId = threadsState.activeThreadId
    const currentMessages = messages
    const nextMessages = (() => {
      const next = [...currentMessages, userMessage]
      const hasTyping = next.some((m) => m.id === typingId)
      return hasTyping
        ? next.map((m) => (m.id === typingId ? { ...m, isTyping: true } : m))
        : [
            ...next,
            {
              id: typingId,
              role: 'assistant',
              content: '',
              isTyping: true,
              timestamp: new Date().toISOString(),
            },
          ]
    })()

    const nextTitle = activeThread?.title === 'New chat' ? defaultThreadName(text) : activeThread?.title

    setThreadPatch(threadId, {
      title: nextTitle || activeThread?.title || 'Muse chat',
      activeCategory,
      selectedModel,
      messages: nextMessages,
    })
    setInput('')
    setIsLoading(true)

    const controller = new AbortController()
    abortRef.current = controller

    try {
      // Stubbed streaming-style response (until museAPI is wired):
      const base = `Got it. Here’s a first draft plan + output skeleton.\n\n` +
        `1) Goal: ${text}\n` +
        `2) Deliverable: ${activeCategory} → ${activeAssets?.[0]?.label || 'asset'}\n` +
        `3) Next: tell me ICP + offer + channel.\n\n` +
        `Draft (v0):\n` +
        `- Hook: ...\n` +
        `- Body: ...\n` +
        `- CTA: ...\n`

      const words = base.split(/\s+/).filter(Boolean)
      let acc = ''

      for (let i = 0; i < words.length; i++) {
        if (controller.signal.aborted) throw new Error('aborted')
        acc += (i === 0 ? '' : ' ') + words[i]
        setThreadPatch(threadId, {
          messages: (threadsState.threadsById?.[threadId]?.messages || nextMessages).map((m) =>
            m.id === typingId ? { ...m, content: acc + ' ▌', isTyping: true, timestamp: m.timestamp } : m
          ),
        })
        // Fast “live typing” feel
        // eslint-disable-next-line no-await-in-loop
        await new Promise((r) => setTimeout(r, 18))
      }

      setThreadPatch(threadId, {
        messages: (threadsState.threadsById?.[threadId]?.messages || nextMessages).map((m) =>
          m.id === typingId ? { ...m, content: acc, isTyping: false, timestamp: m.timestamp } : m
        ),
      })
    } catch (error) {
      if (controller.signal.aborted) {
        addNotification?.({ level: 'info', title: 'Stopped', detail: 'Generation stopped.' })
      } else {
        console.error('Muse send failed:', error)
        addNotification?.({ level: 'error', title: 'Muse error', detail: 'Failed to send message.' })
        setThreadPatch(threadId, {
          messages: (threadsState.threadsById?.[threadId]?.messages || nextMessages).filter((m) => m.id !== typingId),
        })
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleScroll = () => {
    const el = scrollRef.current
    if (!el) return
    const threshold = 40
    const atBottom = el.scrollHeight - el.scrollTop - el.clientHeight <= threshold
    setIsAtBottom(atBottom)
  }

  const hasUserMessages = messages.some((m) => m.role === 'user')

  return (
    <div className="h-full muse-theme" style={{ backgroundColor: 'var(--muse-bg-base)' }}>
      <div className="h-full flex flex-col">
        <div className="h-14 border-b" style={{ borderColor: 'var(--muse-border-soft)', background: 'var(--muse-bg-surface-muted)', backdropFilter: 'blur(10px)' }}>
          <div className="h-full max-w-[740px] mx-auto px-4 flex items-center justify-between">
            <div className="text-[15px] font-medium" style={{ color: 'var(--muse-text-primary)' }}>
              Muse
            </div>
            <button
              type="button"
              onClick={() => {
                setCommandPaletteOpen(true)
                setCommandQuery('')
                setCommandIndex(0)
              }}
              className="h-9 w-9 inline-flex items-center justify-center rounded-[14px]"
              style={{ color: 'var(--muse-text-secondary)' }}
              aria-label="Menu"
              title="Menu"
            >
              <MoreHorizontal className="w-5 h-5" strokeWidth={1.5} />
            </button>
          </div>
          <input
            ref={fileInputRef}
            type="file"
            accept="application/json"
            className="hidden"
            onChange={importChat}
          />
        </div>

        <div className="flex-1 min-h-0 flex justify-center">
          <div className="w-[300px] border-r border-paper-100 bg-white/60 backdrop-blur-sm hidden flex-col">
            <div className="p-4 border-b border-paper-100">
              <div className="relative">
                <Search className="w-4 h-4 text-ink-400 absolute left-3 top-1/2 -translate-y-1/2" strokeWidth={1.5} />
                {threadsState.threadOrder
                  .map((id) => threadsState.threadsById[id])
                  .filter(Boolean)
                  .filter((t) => {
                    const q = threadsQuery.trim().toLowerCase()
                    if (!q) return true
                    const titleHit = String(t.title || '').toLowerCase().includes(q)
                    const contentHit = (t.messages || []).some((m) =>
                      String(m.content || '').toLowerCase().includes(q)
                    )
                    return titleHit || contentHit
                  })
                  .sort((a, b) => {
                    if (!!a.pinned !== !!b.pinned) return a.pinned ? -1 : 1
                    return new Date(b.updatedAt || 0).getTime() - new Date(a.updatedAt || 0).getTime()
                  })
                  .map((t) => {
                    const isActive = t.id === threadsState.activeThreadId
                    const preview = [...(t.messages || [])].slice(-1)[0]?.content || ''
                    const previewText = truncateForPreview(preview, 80).preview
                    return (
                      <button
                        key={t.id}
                        type="button"
                        onClick={() => setActiveThreadId(t.id)}
                        className={`w-full text-left px-4 py-3 rounded-2xl transition-editorial ${
                          isActive ? 'bg-paper-100 text-ink' : 'text-ink-600 hover:text-ink hover:bg-paper-50'
                        }`}
                      >
                        <div className="flex items-start justify-between gap-3">
                          <div className="min-w-0 flex-1">
                            <div className="text-sm font-medium truncate mb-1">{t.title || 'Untitled'}</div>
                            <div className="text-xs text-ink-500 truncate">{previewText}</div>
                            <div className="text-xs text-ink-400 mt-1 font-mono">{formatRelativeTime(t.updatedAt)}</div>
                          </div>
                          {t.pinned && (
                            <Pin className="w-4 h-4 text-primary flex-shrink-0 mt-1" strokeWidth={1.5} />
                          )}
                        </div>
                      </button>
                    )
                  })}
              </div>
            </div>

            <div className="p-4 border-t border-paper-100">
              <button
                type="button"
                onClick={createNewThread}
                className="w-full h-11 rounded-2xl bg-primary text-white hover:bg-primary/90 transition-editorial flex items-center justify-center gap-3 font-medium"
              >
                <Plus className="w-4 h-4" strokeWidth={1.5} />
                New conversation
              </button>
            </div>
          </div>

          <div className="flex-1 min-w-0 flex flex-col" style={{ maxWidth: 740 }}>
            <div
              ref={scrollRef}
              onScroll={handleScroll}
              className="flex-1 min-h-0 overflow-y-auto px-4 py-10"
            >
              <div className="mx-auto w-full space-y-6" style={{ maxWidth: 740 }}>
                {!hasUserMessages ? (
                  <div className="min-h-[60vh] flex flex-col items-center justify-center text-center">
                    <div className="text-[20px] font-medium" style={{ color: 'var(--muse-text-primary)' }}>
                      What are we making?
                    </div>
                    <div className="mt-2 text-[13px]" style={{ color: 'var(--muse-text-secondary)' }}>
                      Use @ for assets, / for skills, or just describe it.
                    </div>
                    <div className="mt-6 flex flex-wrap justify-center gap-2">
                      {['@email', '@linkedin', '@meme', '@carousel'].map((pill) => (
                        <button
                          key={pill}
                          type="button"
                          onClick={() => {
                            setInput((prev) => (prev ? prev + ' ' + pill : pill))
                            setTimeout(() => inputRef.current?.focus?.(), 0)
                          }}
                          className="px-3 py-1.5 rounded-[999px] text-[13px]"
                          style={{ border: '1px solid var(--muse-border-soft)', color: 'var(--muse-text-primary)', background: 'var(--muse-bg-surface)' }}
                        >
                          {pill}
                        </button>
                      ))}
                    </div>
                  </div>
                ) : (
                  messages
                  .filter((m) => m.id !== 'typing' || m.isTyping || m.content)
                  .map((message) => {
                    const { preview, full } = truncateForPreview(message.content, 900)
                    const isExpanded = !!expandedById[message.id]
                    const showToggle = !!full
                    const rendered = showToggle && !isExpanded ? preview : message.content

                    return (
                      <motion.div
                        key={message.id}
                        initial={{ opacity: 0, y: 8 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.3, ease: 'easeOut' }}
                        className="group"
                      >
                        <ChatBubble role={message.role}>
                          <div className="space-y-3">
                            {message.isTyping ? (
                              <div className="flex items-center justify-between gap-4">
                                <TypingDots />
                                <button
                                  type="button"
                                  onClick={stopGenerating}
                                  className="text-xs text-ink-500 hover:text-ink transition-editorial flex items-center gap-2 px-3 py-1.5 rounded-xl hover:bg-paper-50"
                                >
                                  <Square className="w-4 h-4" strokeWidth={1.5} />
                                  Stop
                                </button>
                              </div>
                            ) : (
                              <div className="max-w-none" style={{ color: 'var(--muse-text-primary)' }}>
                                {rendered}
                              </div>
                            )}

                            {!message.isTyping && (
                              <div className="flex items-center justify-between gap-4 pt-2 border-t border-paper-100">
                                <div className="text-xs font-mono" style={{ color: 'var(--muse-text-muted)' }}>
                                  {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                </div>

                                <div className="flex items-center gap-3 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                                  {showToggle && (
                                    <button
                                      type="button"
                                      onClick={() =>
                                        setExpandedById((prev) => ({
                                          ...prev,
                                          [message.id]: !prev[message.id],
                                        }))
                                      }
                                      className="text-xs text-ink-500 hover:text-ink transition-editorial flex items-center gap-1.5 px-2 py-1 rounded-lg hover:bg-paper-50"
                                    >
                                      {isExpanded ? (
                                        <>
                                          <ChevronUp className="w-3.5 h-3.5" strokeWidth={1.5} />
                                          Collapse
                                        </>
                                      ) : (
                                        <>
                                          <ChevronDown className="w-3.5 h-3.5" strokeWidth={1.5} />
                                          Expand
                                        </>
                                      )}
                                    </button>
                                  )}

                                  <button
                                    type="button"
                                    onClick={async () => {
                                      try {
                                        await navigator.clipboard.writeText(String(message.content || ''))
                                        addNotification?.({ level: 'success', title: 'Copied', detail: 'Message copied to clipboard.' })
                                      } catch {
                                        addNotification?.({ level: 'error', title: 'Copy failed', detail: 'Clipboard unavailable.' })
                                      }
                                    }}
                                    className="text-xs text-ink-500 hover:text-ink transition-editorial flex items-center gap-1.5 px-2 py-1 rounded-lg hover:bg-paper-50"
                                  >
                                    <Copy className="w-3.5 h-3.5" strokeWidth={1.5} />
                                    Copy
                                  </button>

                                  <button
                                    type="button"
                                    onClick={() =>
                                      downloadTextFile(
                                        `muse-message-${message.id}.txt`,
                                        message.content
                                      )
                                    }
                                    className="text-xs text-ink-500 hover:text-ink transition-editorial flex items-center gap-1.5 px-2 py-1 rounded-lg hover:bg-paper-50"
                                  >
                                    <Download className="w-3.5 h-3.5" strokeWidth={1.5} />
                                    Save
                                  </button>

                                  {message.role === 'assistant' && !message.isTyping && (
                                    <button
                                      type="button"
                                      onClick={() => {
                                        createArtifactFromMessage(message)
                                      }}
                                      className="text-xs text-ink-500 hover:text-ink transition-editorial flex items-center gap-1.5 px-2 py-1 rounded-lg hover:bg-paper-50"
                                    >
                                      <Pin className="w-3.5 h-3.5" strokeWidth={1.5} />
                                      Pin
                                    </button>
                                  )}
                                </div>
                              </div>
                            )}
                          </div>
                        </ChatBubble>
                      </motion.div>
                    )
                  })} 
              </div>

              {!isAtBottom && (
                <div className="fixed bottom-32 left-[calc(50%)] -translate-x-1/2 z-30">
                  <button
                    type="button"
                    onClick={() => scrollToBottom('smooth')}
                    className="px-4 py-2 rounded-2xl bg-white/90 border border-paper-100 shadow-lg text-sm text-ink flex items-center gap-2 hover:bg-white transition-editorial font-medium"
                  >
                    <CornerDownLeft className="w-4 h-4" strokeWidth={1.5} />
                    Jump to latest
                  </button>
                </div>
              )}
            </div>

            <div className="bg-transparent">
              <div className="mx-auto px-4 py-5" style={{ maxWidth: 740 }}>
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div
                    className="relative rounded-[18px] overflow-hidden"
                    style={{ border: '1px solid var(--muse-border-soft)', background: 'var(--muse-bg-surface)' }}
                  >
                    <div className="absolute left-4 top-4 text-ink-400 flex items-center gap-3">
                      <button
                        type="button"
                        className="p-2 rounded-xl hover:bg-paper-50 transition-editorial"
                        onClick={() => addNotification?.({ level: 'info', title: 'Attach', detail: 'File attachments are not wired up yet.' })}
                        aria-label="Attach"
                      >
                        <Paperclip className="w-4 h-4" strokeWidth={1.5} />
                      </button>
                    </div>

                    {pickerOpen && (
                      <div className="absolute left-0 right-0 bottom-[calc(100%+12px)] z-50">
                        <div className="mx-auto max-w-4xl">
                          <div className="rounded-2xl border border-paper-100 bg-white shadow-xl overflow-hidden">
                            <div className="px-4 py-3 border-b border-paper-100 flex items-center justify-between gap-3">
                              <div className="text-xs text-ink-500 font-medium">
                                {pickerOpen === 'assets' ? 'Assets (@)' : pickerOpen === 'prompts' ? 'Prompts (/)' : 'Tools (&)'}
                              </div>
                              <input
                                value={pickerQuery}
                                onChange={(e) => setPickerQuery(e.target.value)}
                                placeholder="Filter…"
                                className="w-[240px] text-sm px-3 py-2 rounded-xl border border-paper-100 bg-paper-50 focus:outline-none focus:border-paper-200 transition-editorial"
                              />
                            </div>
                            <div className="max-h-[300px] overflow-y-auto">
                              {pickerItems.length === 0 ? (
                                <div className="p-6 text-sm text-ink-400 text-center">No matches.</div>
                              ) : (
                                pickerItems.slice(0, 50).map((it, idx) => (
                                  <button
                                    key={it.id}
                                    type="button"
                                    onClick={() => applyPickerItem(it)}
                                    className={`w-full text-left px-4 py-3 border-b border-paper-50 hover:bg-paper-50 transition-editorial ${
                                      idx === pickerIndex ? 'bg-paper-100' : 'bg-white'
                                    }`}
                                  >
                                    <div className="flex items-start justify-between gap-4">
                                      <div className="min-w-0 flex-1">
                                        <div className="text-sm text-ink font-medium truncate mb-1">{it.label}</div>
                                        <div className="text-xs text-ink-500 leading-relaxed">{it.detail}</div>
                                      </div>
                                    </div>
                                  </button>
                                ))
                              )}
                            </div>
                          </div>
                        </div>
                      </div>
                    )}

                    <textarea
                      ref={inputRef}
                      id="muse-input"
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      placeholder='Try: "@email for @cohort:CTOs about budget objections"'
                      className="w-full resize-none bg-transparent px-16 pr-32 py-4 focus:outline-none text-[15px] leading-[1.55]"
                      rows={1}
                      disabled={isLoading}
                      onKeyDown={(e) => {
                        if (commandPaletteOpen) {
                          if (e.key === 'ArrowDown') {
                            e.preventDefault()
                            setCommandIndex((v) => Math.min(v + 1, Math.max(0, commandItems.length - 1)))
                            return
                          }
                          if (e.key === 'ArrowUp') {
                            e.preventDefault()
                            setCommandIndex((v) => Math.max(0, v - 1))
                            return
                          }
                          if (e.key === 'Enter' && !e.shiftKey) {
                            e.preventDefault()
                            executeCommand(commandItems[commandIndex])
                            return
                          }
                          if (e.key === 'Escape') {
                            e.preventDefault()
                            closeCommandPalette()
                            return
                          }
                          return
                        }

                        if (pickerOpen) {
                          if (e.key === 'ArrowDown') {
                            e.preventDefault()
                            setPickerIndex((v) => Math.min(v + 1, Math.max(0, pickerItems.length - 1)))
                            return
                          }
                          if (e.key === 'ArrowUp') {
                            e.preventDefault()
                            setPickerIndex((v) => Math.max(0, v - 1))
                            return
                          }
                          if (e.key === 'Enter' && !e.shiftKey) {
                            e.preventDefault()
                            applyPickerItem(pickerItems[pickerIndex])
                            return
                          }
                          if (e.key === 'Escape') {
                            e.preventDefault()
                            closePicker()
                            return
                          }
                        }

                        if (e.key === '@') {
                          setPickerOpen('assets')
                          setPickerQuery('')
                          return
                        }
                        if (e.key === '/') {
                          setPickerOpen('prompts')
                          setPickerQuery('')
                          return
                        }
                        if (e.key === '&') {
                          setPickerOpen('tools')
                          setPickerQuery('')
                          return
                        }

                        if (e.key === 'Enter' && !e.shiftKey) {
                          e.preventDefault()
                          handleSubmit(e)
                        }
                      }}
                    />

                    <div className="absolute right-4 top-4 flex items-center gap-3">
                      {isLoading ? (
                        <button
                          type="button"
                          onClick={stopGenerating}
                          className="h-10 px-4 rounded-xl bg-paper-100 border border-paper-200 text-ink-600 hover:text-ink flex items-center gap-2 font-medium transition-editorial"
                        >
                          <Square className="w-4 h-4" strokeWidth={1.5} />
                          Stop
                        </button>
                      ) : (
                        <button
                          type="submit"
                          disabled={!input.trim()}
                          className={`h-10 px-5 rounded-xl font-medium transition-all duration-300 flex items-center gap-2 ${
                            !input.trim()
                              ? 'bg-paper-100 text-paper-400 cursor-not-allowed'
                              : 'bg-primary text-white hover:bg-primary/90 shadow-lg hover:shadow-xl'
                          }`}
                        >
                          <Check className="w-4 h-4" strokeWidth={1.5} />
                          {input.trim() ? 'Send' : null}
                        </button>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center justify-between gap-4 text-xs text-ink-500">
                    <div className="truncate font-mono">
                      Quick: <span className="text-primary font-medium">@</span> assets, <span className="text-primary font-medium">/</span> prompts, <span className="text-primary font-medium">&amp;</span> tools. <span className="text-ink-400">•</span> <kbd className="px-1.5 py-0.5 bg-paper-100 rounded text-xs">⌘K</kbd> for commands.
                    </div>
                    <div className="flex items-center gap-2 flex-shrink-0">
                      <span className="px-3 py-1 rounded-xl bg-paper-100 border border-paper-100 text-ink-600 font-medium">{activeCategory}</span>
                    </div>
                  </div>
                </form>
              </div>
            </div>
          </div>
          {showRightPanel && (
            <div className="w-[380px] border-l border-paper-100 bg-white/70 backdrop-blur-sm hidden lg:flex flex-col">
              <div className="p-5 border-b border-paper-100">
                <div className="flex items-center gap-1">
                  {['Artifacts', 'Assets', 'Skills'].map((t) => (
                    <button
                      key={t}
                      type="button"
                      onClick={() => setActiveTab(t)}
                      className={`px-4 py-2 text-sm font-medium transition-editorial ${
                        activeTab === t ? 'text-primary' : 'text-ink-500 hover:text-ink'
                      }`}
                    >
                      {t}
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex-1 overflow-y-auto">
                {activeTab === 'Artifacts' ? (
                  <div className="p-5 space-y-4">
                    <div className="text-sm text-ink-500 leading-relaxed">Artifacts are living documents. Pin a message, then refine it here with versions.</div>
                    {threadArtifacts.length === 0 ? (
                      <div className="p-6 rounded-2xl bg-paper-50 border border-paper-100 text-sm text-ink-500 text-center">
                        No artifacts yet. Pin an assistant message to start a draft library.
                      </div>
                    ) : (
                      <div className="space-y-3">
                        {threadArtifacts.map((a) => {
                          const isActive = a.id === activeArtifactId
                          const versions = a.versions || []
                          const current = versions.find((v) => v.id === a.currentVersionId) || versions[0]
                          const preview = truncateForPreview(current?.content || '', 120).preview
                          return (
                            <div
                              key={a.id}
                              className={`rounded-2xl border transition-editorial ${
                                isActive ? 'border-paper-200 bg-paper-50' : 'border-paper-100 bg-white'
                              }`}
                            >
                              <button
                                type="button"
                                onClick={() => {
                                  setActiveArtifactId(a.id)
                                  setActiveArtifactVersionId(a.currentVersionId || versions[0]?.id || null)
                                }}
                                className="w-full text-left p-4"
                              >
                                <div className="flex items-start justify-between gap-3">
                                  <div className="min-w-0 flex-1">
                                    <div className="text-sm text-ink font-medium line-clamp-1 mb-1">{a.title || 'Draft'}</div>
                                    <div className="text-xs text-ink-500 line-clamp-2 leading-relaxed">{preview}</div>
                                    <div className="text-xs text-ink-400 mt-2 font-mono flex items-center gap-2">
                                      <span className="inline-flex items-center gap-1">
                                        <History className="w-3 h-3" strokeWidth={1.5} />
                                        {versions.length}v
                                      </span>
                                      <span>•</span>
                                      <span>{formatRelativeTime(a.updatedAt || a.createdAt)}</span>
                                    </div>
                                  </div>
                                  <FileText className="w-5 h-5 text-ink-300 flex-shrink-0 mt-1" strokeWidth={1.5} />
                                </div>
                              </button>

                              <div className="px-4 pb-4 flex items-center justify-between gap-3">
                                <div className="flex items-center gap-2">
                                  <button
                                    type="button"
                                    onClick={() => beginRenameArtifact(a.id)}
                                    className="text-xs text-ink-500 hover:text-ink transition-editorial flex items-center gap-1"
                                  >
                                    <Pencil className="w-3.5 h-3.5" strokeWidth={1.5} />
                                    Rename
                                  </button>
                                  <button
                                    type="button"
                                    onClick={() => exportArtifact(a)}
                                    className="text-xs text-ink-500 hover:text-ink transition-editorial flex items-center gap-1"
                                  >
                                    <Download className="w-3.5 h-3.5" strokeWidth={1.5} />
                                    Export
                                  </button>
                                </div>
                                <button
                                  type="button"
                                  onClick={() => setConfirmDeleteArtifactId(a.id)}
                                  className="text-xs text-ink-500 hover:text-ink transition-editorial flex items-center gap-1"
                                >
                                  <Trash className="w-3.5 h-3.5" strokeWidth={1.5} />
                                  Delete
                                </button>
                              </div>

                              {confirmDeleteArtifactId === a.id && (
                                <div className="px-4 pb-4">
                                  <div className="p-3 rounded-2xl border border-paper-100 bg-paper-50">
                                    <div className="text-xs text-ink-500">Delete artifact?</div>
                                    <div className="mt-3 flex items-center justify-end gap-2">
                                      <button
                                        type="button"
                                        onClick={() => setConfirmDeleteArtifactId(null)}
                                        className="px-3 py-1.5 rounded-xl border border-paper-100 bg-white text-xs text-ink-500 hover:text-ink"
                                      >
                                        Cancel
                                      </button>
                                      <button
                                        type="button"
                                        onClick={() => deleteArtifact(a.id)}
                                        className="px-3 py-1.5 rounded-xl border border-red-200 bg-red-50 text-xs text-red-700 hover:bg-red-100"
                                      >
                                        Delete
                                      </button>
                                    </div>
                                  </div>
                                </div>
                              )}
                            </div>
                          )
                        })}
                      </div>
                    )}

                    {activeArtifact && (
                      <div className="mt-6 rounded-2xl border border-paper-100 bg-white">
                        <div className="p-4 border-b border-paper-100">
                          {artifactRenameId === activeArtifact.id ? (
                            <input
                              id={`muse-artifact-rename-${activeArtifact.id}`}
                              value={artifactRenameDraft}
                              onChange={(e) => setArtifactRenameDraft(e.target.value)}
                              onBlur={commitRenameArtifact}
                              onKeyDown={(e) => {
                                if (e.key === 'Enter') {
                                  e.preventDefault()
                                  commitRenameArtifact()
                                }
                                if (e.key === 'Escape') {
                                  e.preventDefault()
                                  setArtifactRenameId(null)
                                  setArtifactRenameDraft('')
                                }
                              }}
                              className="w-full text-sm text-ink font-medium bg-white border border-paper-200 rounded-xl px-3 py-2 focus:outline-none"
                            />
                          ) : (
                            <div className="flex items-center justify-between gap-3">
                              <div className="min-w-0">
                                <div className="font-serif text-sm text-ink truncate">{activeArtifact.title || 'Draft'}</div>
                                <div className="text-xs text-ink-400 mt-1">{(activeArtifact.versions || []).length} versions • {formatRelativeTime(activeArtifact.updatedAt || activeArtifact.createdAt)}</div>
                              </div>
                              <div className="flex items-center gap-2">
                                <button
                                  type="button"
                                  onClick={() => beginRenameArtifact(activeArtifact.id)}
                                  className="h-8 w-8 inline-flex items-center justify-center rounded-xl border border-paper-100 text-ink-500 hover:text-ink"
                                  title="Rename"
                                  aria-label="Rename"
                                >
                                  <Pencil className="w-4 h-4" strokeWidth={1.5} />
                                </button>
                                <button
                                  type="button"
                                  onClick={() => exportArtifact(activeArtifact)}
                                  className="h-8 w-8 inline-flex items-center justify-center rounded-xl border border-paper-100 text-ink-500 hover:text-ink"
                                  title="Export"
                                  aria-label="Export"
                                >
                                  <Download className="w-4 h-4" strokeWidth={1.5} />
                                </button>
                              </div>
                            </div>
                          )}
                        </div>

                        <div className="p-4 border-b border-paper-100 flex items-center justify-between gap-3">
                          <div className="flex items-center gap-3">
                            <select
                              value={activeArtifactVersion?.id || ''}
                              onChange={(e) => revertToVersion(e.target.value)}
                              className="text-xs px-3 py-2 rounded-xl border border-paper-100 bg-paper-50 focus:outline-none"
                            >
                              {(activeArtifact.versions || []).map((v, idx) => (
                                <option key={v.id} value={v.id}>
                                  v{(activeArtifact.versions || []).length - idx} • {formatRelativeTime(v.createdAt)}
                                </option>
                              ))}
                            </select>
                            <div className="text-xs text-ink-400">Editing creates a new version.</div>
                          </div>

                          <div className="flex items-center gap-2">
                            <button
                              type="button"
                              onClick={() => {
                                setArtifactDraftTitle(activeArtifact.title || 'Draft')
                                setArtifactDraftContent(activeArtifactVersion?.content || '')
                                addNotification?.({ level: 'info', title: 'Reset', detail: 'Draft reset to selected version.' })
                              }}
                              className="h-9 px-3 rounded-xl border border-paper-100 bg-paper-50 text-xs text-ink-500 hover:text-ink flex items-center gap-2"
                            >
                              <Undo2 className="w-4 h-4" strokeWidth={1.5} />
                              Reset
                            </button>
                            <button
                              type="button"
                              onClick={saveNewArtifactVersion}
                              className="h-9 px-4 rounded-xl bg-primary text-white hover:bg-primary/90 text-xs font-medium flex items-center gap-2"
                            >
                              <Save className="w-4 h-4" strokeWidth={1.5} />
                              Save v+
                            </button>
                          </div>
                        </div>

                        <div className="p-4 space-y-3">
                          <input
                            value={artifactDraftTitle}
                            onChange={(e) => setArtifactDraftTitle(e.target.value)}
                            placeholder="Artifact title"
                            className="w-full text-sm px-3 py-2 rounded-xl border border-paper-100 bg-white focus:outline-none"
                          />
                          <textarea
                            value={artifactDraftContent}
                            onChange={(e) => setArtifactDraftContent(e.target.value)}
                            placeholder="Write the draft…"
                            className="w-full min-h-[240px] resize-y text-sm leading-relaxed px-3 py-2 rounded-xl border border-paper-100 bg-white focus:outline-none font-mono"
                          />
                        </div>
                      </div>
                    )}
                  </div>
                ) : activeTab === 'Assets' ? (
                  <div className="p-5 space-y-4">
                    <div className="text-sm text-ink-500 leading-relaxed">Choose a category. Then ask Muse for a specific asset.</div>
                    <div className="flex flex-wrap gap-2">
                      {ASSET_REGISTRY.map((category) => (
                        <button
                          key={category.category}
                          type="button"
                          onClick={() => setActiveCategory(category.category)}
                          className={`px-4 py-2 text-sm rounded-2xl border transition-editorial ${
                            activeCategory === category.category ? 'border-primary/20 text-primary bg-primary/5' : 'border-paper-100 text-ink-500 hover:text-ink hover:bg-paper-50'
                          }`}
                        >
                          {category.category}
                        </button>
                      ))}
                    </div>

                    <div className="space-y-2">
                      {activeAssets.map((asset) => (
                        <button
                          key={asset.key}
                          type="button"
                          onClick={() => {
                            setInput((prev) => {
                              const base = prev.trim()
                              const hint = `Create a ${asset.label}.`
                              return base ? base + '\n' + hint : hint
                            })
                            inputRef.current?.focus?.()
                          }}
                          className="w-full text-left px-4 py-3 rounded-2xl border border-paper-100 bg-white hover:bg-paper-50 transition-editorial"
                        >
                          <div className="text-sm text-ink font-medium">{asset.label}</div>
                          <div className="text-xs text-ink-400 mt-1 font-mono">@{asset.key}</div>
                        </button>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="p-5 space-y-4">
                    <div className="text-sm text-ink-500 leading-relaxed">Quick transforms (stub). Click to insert as a prompt hint.</div>
                    {SKILL_REGISTRY.map((group) => (
                      <div key={group.category} className="space-y-3">
                        <div className="font-serif text-sm text-ink">{group.category}</div>
                        <div className="space-y-2">
                          {group.items.map((it) => (
                            <button
                              key={it.key}
                              type="button"
                              onClick={() => {
                                setInput((prev) => {
                                  const base = prev.trim()
                                  const hint = `${it.label}: `
                                  return base ? base + '\n' + hint : hint
                                })
                                inputRef.current?.focus?.()
                              }}
                              className="w-full text-left px-4 py-3 rounded-2xl border border-paper-100 bg-white hover:bg-paper-50 transition-editorial"
                            >
                              <div className="flex items-center justify-between gap-3">
                                <div className="text-sm text-ink font-medium">{it.label}</div>
                                <div className="text-sm font-mono text-ink-400">{it.icon}</div>
                              </div>
                              <div className="text-xs text-ink-400 mt-2 leading-relaxed">{it.description}</div>
                            </button>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        <AnimatePresence>
          {activeAsset?.mode === 'native_meme' && (
            <Modal
              open={isMemeModalOpen}
              onOpenChange={(o) => (!o ? closeAllModals() : null)}
              title={activeAsset?.label || 'Meme generator'}
              description="Meme editor is not wired up yet."
            >
              <div className="p-4 text-sm text-muted-foreground">Coming soon.</div>
            </Modal>
          )}

          {activeAsset?.mode === 'canva' && (
            <Modal
              open={isCanvaModalOpen}
              onOpenChange={(o) => (!o ? closeAllModals() : null)}
              title={activeAsset?.label || 'Canva brief'}
              description="Canva export is not wired up yet."
            >
              <div className="p-4 text-sm text-muted-foreground">Coming soon.</div>
            </Modal>
          )}

          {activeAsset?.mode === 'native_text' && (
            <Modal
              open={isAssetModalOpen}
              onOpenChange={(o) => (!o ? closeAllModals() : null)}
              title={activeAsset?.label || 'Text asset'}
              description="Text asset editor is not wired up yet."
            >
              <div className="p-4 text-sm text-muted-foreground">Coming soon.</div>
            </Modal>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}

function stripMentions(text) {
  return String(text || '')
    .replace(/(^|\s)@[^\s]+/g, ' ')
    .replace(/(^|\s)\/[^\s]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
}

function inferCanvaSpecs(assetKey) {
  switch (assetKey) {
    case 'instagram-post':
      return { platform: 'instagram', dimensions: '1080x1350' }
    case 'instagram-carousel':
      return { platform: 'instagram', dimensions: '1080x1350 (per slide)' }
    case 'linkedin-carousel':
      return { platform: 'linkedin', dimensions: '1080x1350 (per slide)' }
    case 'email-header':
      return { platform: 'email', dimensions: '600x150' }
    case 'landing-hero':
      return { platform: 'web', dimensions: '1440x600' }
    default:
      return { platform: 'design', dimensions: '' }
  }
}

function inferTitleFromAssetKey(assetKey) {
  const hit = ASSET_REGISTRY.find(a => a.key === assetKey)
  return hit?.label || 'Muse asset'
}

export default MuseChatPage
