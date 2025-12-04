import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Target, 
  Edit3, 
  Save,
  Sparkles,
  Users,
  Zap,
  TrendingUp,
  CheckCircle2
} from 'lucide-react'

const PositionCard = ({ title, content, onEdit, isEditing, onSave, onChange }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    className="bg-zinc-900/50 border border-white/5 rounded-xl p-6"
  >
    <div className="flex items-start justify-between mb-4">
      <h3 className="text-white font-medium">{title}</h3>
      <button
        onClick={isEditing ? onSave : onEdit}
        className="p-2 hover:bg-white/5 rounded-lg transition-colors text-white/40 hover:text-white"
      >
        {isEditing ? <Save className="w-4 h-4" /> : <Edit3 className="w-4 h-4" />}
      </button>
    </div>
    {isEditing ? (
      <textarea
        value={content}
        onChange={(e) => onChange(e.target.value)}
        className="w-full bg-white/5 border border-white/10 rounded-lg p-3 text-white/80 text-sm leading-relaxed resize-none focus:border-amber-500/50 focus:outline-none min-h-[120px]"
      />
    ) : (
      <p className="text-white/60 text-sm leading-relaxed">{content}</p>
    )}
  </motion.div>
)

const Position = () => {
  const [editing, setEditing] = useState(null)
  const [position, setPosition] = useState({
    statement: "Raptorflow is the strategic operating system that transforms scattered startup ideas into precision 90-day execution plans, trusted by founders who ship.",
    audience: "Early-stage founders (0-50 employees) who are overwhelmed by tactical noise and need strategic clarity to achieve product-market fit faster.",
    problem: "Founders waste 6-12 months on scattered tactics without a coherent strategy. They're drowning in advice, frameworks, and tools but lack a clear path forward.",
    solution: "A systematic methodology that extracts your unique strategy, maps it to a 90-day war plan, and gives you the AI-powered tools to execute with precision.",
    differentiator: "Unlike consultants who deliver PDFs that gather dust, or tools that add more noise, Raptorflow combines strategic methodology with actionable execution planning.",
  })

  const handleEdit = (field) => setEditing(field)
  const handleSave = () => setEditing(null)
  const handleChange = (field, value) => setPosition({ ...position, [field]: value })

  const completeness = Object.values(position).filter(v => v.length > 20).length / 5 * 100

  return (
    <div className="max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h1 className="text-3xl font-light text-white">Position</h1>
          <p className="text-white/40 mt-1">
            Define how you stand out in the market
          </p>
        </motion.div>

        <motion.button
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="flex items-center gap-2 px-5 py-2.5 bg-amber-500 hover:bg-amber-400 text-black font-medium rounded-lg transition-colors"
        >
          <Sparkles className="w-4 h-4" />
          AI Refine
        </motion.button>
      </div>

      {/* Completeness */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-zinc-900/50 border border-white/5 rounded-xl p-5 mb-8"
      >
        <div className="flex items-center justify-between mb-3">
          <span className="text-white/60 text-sm">Position Completeness</span>
          <span className="text-amber-400 font-medium">{completeness}%</span>
        </div>
        <div className="h-2 bg-white/10 rounded-full overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${completeness}%` }}
            transition={{ delay: 0.3, duration: 0.8 }}
            className="h-full bg-gradient-to-r from-amber-500 to-amber-400 rounded-full"
          />
        </div>
      </motion.div>

      {/* Main positioning statement */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15 }}
        className="bg-gradient-to-br from-amber-500/10 to-amber-600/5 border border-amber-500/20 rounded-xl p-6 mb-6"
      >
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-amber-500/20 rounded-lg">
              <Target className="w-5 h-5 text-amber-400" />
            </div>
            <h3 className="text-white font-medium">Positioning Statement</h3>
          </div>
          <button
            onClick={() => editing === 'statement' ? handleSave() : handleEdit('statement')}
            className="p-2 hover:bg-white/5 rounded-lg transition-colors text-white/40 hover:text-white"
          >
            {editing === 'statement' ? <Save className="w-4 h-4" /> : <Edit3 className="w-4 h-4" />}
          </button>
        </div>
        {editing === 'statement' ? (
          <textarea
            value={position.statement}
            onChange={(e) => handleChange('statement', e.target.value)}
            className="w-full bg-black/30 border border-white/10 rounded-lg p-4 text-white text-lg leading-relaxed resize-none focus:border-amber-500/50 focus:outline-none min-h-[100px]"
          />
        ) : (
          <p className="text-white text-lg leading-relaxed italic">
            "{position.statement}"
          </p>
        )}
      </motion.div>

      {/* Position components */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <PositionCard
          title="Target Audience"
          content={position.audience}
          isEditing={editing === 'audience'}
          onEdit={() => handleEdit('audience')}
          onSave={handleSave}
          onChange={(value) => handleChange('audience', value)}
        />
        <PositionCard
          title="Core Problem"
          content={position.problem}
          isEditing={editing === 'problem'}
          onEdit={() => handleEdit('problem')}
          onSave={handleSave}
          onChange={(value) => handleChange('problem', value)}
        />
        <PositionCard
          title="Our Solution"
          content={position.solution}
          isEditing={editing === 'solution'}
          onEdit={() => handleEdit('solution')}
          onSave={handleSave}
          onChange={(value) => handleChange('solution', value)}
        />
        <PositionCard
          title="Key Differentiator"
          content={position.differentiator}
          isEditing={editing === 'differentiator'}
          onEdit={() => handleEdit('differentiator')}
          onSave={handleSave}
          onChange={(value) => handleChange('differentiator', value)}
        />
      </div>

      {/* Quick stats */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="mt-8 grid grid-cols-3 gap-4"
      >
        {[
          { icon: Users, label: 'Cohorts Using', value: '5' },
          { icon: Zap, label: 'Moves Aligned', value: '12' },
          { icon: TrendingUp, label: 'Message Variants', value: '8' },
        ].map((stat, i) => (
          <div key={i} className="bg-zinc-900/30 border border-white/5 rounded-lg p-4 text-center">
            <stat.icon className="w-5 h-5 text-amber-400 mx-auto mb-2" />
            <p className="text-xl font-light text-white">{stat.value}</p>
            <p className="text-xs text-white/40">{stat.label}</p>
          </div>
        ))}
      </motion.div>
    </div>
  )
}

export default Position

