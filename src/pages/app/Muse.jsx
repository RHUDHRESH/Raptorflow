import React, { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Send, 
  Sparkles, 
  User,
  Lightbulb,
  Target,
  TrendingUp,
  Users,
  MessageSquare,
  Trash2,
  Copy,
  Check
} from 'lucide-react'

const suggestedPrompts = [
  { icon: Target, text: "Help me refine my positioning statement" },
  { icon: Users, text: "Analyze my target cohort segments" },
  { icon: TrendingUp, text: "Suggest moves for my Q1 campaign" },
  { icon: Lightbulb, text: "What's missing from my strategy?" },
]

const Message = ({ message, isLast }) => {
  const [copied, setCopied] = useState(false)

  const copyToClipboard = () => {
    navigator.clipboard.writeText(message.content)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex gap-4 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
    >
      {message.role === 'assistant' && (
        <div className="w-8 h-8 bg-gradient-to-br from-amber-500 to-amber-600 rounded-lg flex items-center justify-center flex-shrink-0">
          <Sparkles className="w-4 h-4 text-black" />
        </div>
      )}
      
      <div className={`group max-w-2xl ${message.role === 'user' ? 'order-first' : ''}`}>
        <div className={`p-4 rounded-2xl ${
          message.role === 'user'
            ? 'bg-amber-500 text-black rounded-br-md'
            : 'bg-zinc-900 border border-white/5 text-white rounded-bl-md'
        }`}>
          <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
        </div>
        
        {message.role === 'assistant' && (
          <div className="mt-2 flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
            <button 
              onClick={copyToClipboard}
              className="p-1.5 hover:bg-white/5 rounded text-white/40 hover:text-white/60"
            >
              {copied ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
            </button>
          </div>
        )}
      </div>

      {message.role === 'user' && (
        <div className="w-8 h-8 bg-white/10 rounded-lg flex items-center justify-center flex-shrink-0">
          <User className="w-4 h-4 text-white/60" />
        </div>
      )}
    </motion.div>
  )
}

const Muse = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: 'assistant',
      content: "Hey there! I'm Muse, your strategic thinking partner. I can help you with positioning, campaign strategy, move planning, and cohort analysis.\n\nWhat would you like to work on today?"
    }
  ])
  const [input, setInput] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async () => {
    if (!input.trim()) return

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: input
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsTyping(true)

    // Simulate AI response
    setTimeout(() => {
      const responses = [
        "Great question! Based on your positioning, I'd suggest focusing on the 'Tech Founders' cohort first. They have the highest problem awareness and are actively seeking solutions.\n\nHere's what I recommend:\n\n1. **Sharpen your hook** - Lead with the pain point of 'scattered strategy' rather than features\n2. **Social proof** - Your '47% faster GTM' stat is compelling, make it more visible\n3. **Create urgency** - Consider a time-bound offer for early adopters",
        "Looking at your current campaign structure, I see an opportunity to bridge the gap between your awareness moves and conversion.\n\nYour LinkedIn content is building authority, but you need a stronger 'bridge' to move people from Solution Aware to Product Aware. Consider:\n\n- A webinar or live workshop\n- An interactive strategy assessment\n- Case study with specific metrics",
        "Your positioning is solid, but I notice some overlap between your cohorts. Let me help you segment more precisely.\n\n**Primary Cohort:** Solo founders, 0-2 employees, pre-revenue or early revenue, high-intensity problem awareness\n\n**Secondary Cohort:** Small teams (3-10), some traction, looking to systematize their GTM approach\n\nThe messaging for each should be distinct. Want me to draft specific value props for each?"
      ]
      
      const aiMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: responses[Math.floor(Math.random() * responses.length)]
      }
      
      setMessages(prev => [...prev, aiMessage])
      setIsTyping(false)
    }, 1500)
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleSuggestedPrompt = (text) => {
    setInput(text)
  }

  return (
    <div className="max-w-4xl mx-auto h-[calc(100vh-8rem)] flex flex-col">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-6"
      >
        <div className="flex items-center gap-3">
          <div className="p-2 bg-gradient-to-br from-amber-500/20 to-amber-600/20 rounded-lg">
            <Sparkles className="w-6 h-6 text-amber-400" />
          </div>
          <div>
            <h1 className="text-2xl font-light text-white">Muse</h1>
            <p className="text-white/40 text-sm">Your AI strategy partner</p>
          </div>
        </div>
      </motion.div>

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto space-y-6 mb-4 pr-2">
        {messages.map((message, index) => (
          <Message 
            key={message.id} 
            message={message} 
            isLast={index === messages.length - 1}
          />
        ))}
        
        {isTyping && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex gap-4"
          >
            <div className="w-8 h-8 bg-gradient-to-br from-amber-500 to-amber-600 rounded-lg flex items-center justify-center">
              <Sparkles className="w-4 h-4 text-black" />
            </div>
            <div className="bg-zinc-900 border border-white/5 rounded-2xl rounded-bl-md p-4">
              <div className="flex gap-1">
                <span className="w-2 h-2 bg-white/40 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <span className="w-2 h-2 bg-white/40 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <span className="w-2 h-2 bg-white/40 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </motion.div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Suggested prompts (show when few messages) */}
      {messages.length < 3 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-4"
        >
          <p className="text-xs text-white/30 mb-2">Suggested prompts</p>
          <div className="grid grid-cols-2 gap-2">
            {suggestedPrompts.map((prompt, i) => (
              <button
                key={i}
                onClick={() => handleSuggestedPrompt(prompt.text)}
                className="flex items-center gap-2 p-3 bg-zinc-900/50 border border-white/5 rounded-lg text-left hover:border-amber-500/30 transition-colors group"
              >
                <prompt.icon className="w-4 h-4 text-white/40 group-hover:text-amber-400" />
                <span className="text-sm text-white/60 group-hover:text-white/80">{prompt.text}</span>
              </button>
            ))}
          </div>
        </motion.div>
      )}

      {/* Input area */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-zinc-900/50 border border-white/10 rounded-xl p-2"
      >
        <div className="flex items-end gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask Muse anything about your strategy..."
            rows={1}
            className="flex-1 bg-transparent text-white placeholder:text-white/30 resize-none focus:outline-none p-2 max-h-32"
            style={{ minHeight: '44px' }}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isTyping}
            className="p-3 bg-amber-500 hover:bg-amber-400 disabled:bg-white/10 disabled:text-white/30 text-black rounded-lg transition-colors"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </motion.div>
    </div>
  )
}

export default Muse

