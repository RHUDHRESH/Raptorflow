/**
 * Agent Chat Interface Component
 * Interactive chat interface for AI agents
 */
"use client"

import { useState, useEffect, useRef } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { BlueprintCard } from "@/components/ui/BlueprintCard"
import { BlueprintAvatar } from "@/components/ui/BlueprintAvatar"
import { BlueprintLoader } from "@/components/ui/BlueprintLoader"
import { BlueprintProgress } from "@/components/ui/BlueprintProgress"
import {
  Send,
  Mic,
  Paperclip,
  Settings,
  Brain,
  Zap,
  TrendingUp,
  Users,
  BarChart3,
  MessageSquare,
  Clock,
  CheckCircle,
  AlertTriangle,
  X
} from "lucide-react"

interface Message {
  id: string
  type: "user" | "agent" | "system"
  content: string
  timestamp: string
  agentId?: string
  agentName?: string
  status?: "sending" | "sent" | "delivered" | "error"
  metadata?: {
    tokens?: number
    cost?: number
    latency?: number
  }
}

interface Agent {
  id: string
  name: string
  description: string
  category: string
  status: "active" | "idle" | "error"
  capabilities: string[]
}

interface ChatSession {
  id: string
  agentId: string
  agentName: string
  messages: Message[]
  startTime: string
  status: "active" | "completed" | "error"
}

export default function AgentChat() {
  const [sessions, setSessions] = useState<ChatSession[]>([])
  const [currentSession, setCurrentSession] = useState<ChatSession | null>(null)
  const [agents, setAgents] = useState<Agent[]>([])
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null)
  const [input, setInput] = useState("")
  const [isTyping, setIsTyping] = useState(false)
  const [isRecording, setIsRecording] = useState(false)
  const [showAgentSelector, setShowAgentSelector] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    loadAgents()
    loadSessions()
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [currentSession?.messages])

  const loadAgents = async () => {
    try {
      const response = await fetch('/api/agents')
      const data = await response.json()
      setAgents(data)
    } catch (error) {
      console.error('Failed to load agents:', error)
    }
  }

  const loadSessions = async () => {
    try {
      const response = await fetch('/api/chat/sessions')
      const data = await response.json()
      setSessions(data)
    } catch (error) {
      console.error('Failed to load sessions:', error)
    }
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  const startNewSession = (agent: Agent) => {
    const newSession: ChatSession = {
      id: `session_${Date.now()}`,
      agentId: agent.id,
      agentName: agent.name,
      messages: [],
      startTime: new Date().toISOString(),
      status: "active"
    }
    setCurrentSession(newSession)
    setSelectedAgent(agent)
    setShowAgentSelector(false)
  }

  const sendMessage = async () => {
    if (!input.trim() || !currentSession) return

    const userMessage: Message = {
      id: `msg_${Date.now()}`,
      type: "user",
      content: input,
      timestamp: new Date().toISOString(),
      status: "sent"
    }

    // Add user message to session
    const updatedSession = {
      ...currentSession,
      messages: [...currentSession.messages, userMessage]
    }
    setCurrentSession(updatedSession)

    // Clear input
    setInput("")
    setIsTyping(true)

    try {
      // Send message to agent
      const response = await fetch('/api/agents/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          agentId: currentSession.agentId,
          message: input,
          sessionId: currentSession.id
        })
      })

      const data = await response.json()

      // Add agent response
      const agentMessage: Message = {
        id: `msg_${Date.now() + 1}`,
        type: "agent",
        content: data.output,
        timestamp: new Date().toISOString(),
        agentId: currentSession.agentId,
        agentName: currentSession.agentName,
        status: "delivered",
        metadata: {
          tokens: data.tokens_used,
          cost: data.cost_usd,
          latency: data.latency_ms
        }
      }

      setCurrentSession(prev => ({
        ...prev!,
        messages: [...prev!.messages, agentMessage]
      }))

    } catch (error) {
      console.error('Failed to send message:', error)

      // Add error message
      const errorMessage: Message = {
        id: `msg_${Date.now() + 1}`,
        type: "system",
        content: "Sorry, I encountered an error. Please try again.",
        timestamp: new Date().toISOString(),
        status: "error"
      }

      setCurrentSession(prev => ({
        ...prev!,
        messages: [...prev!.messages, errorMessage]
      }))
    } finally {
      setIsTyping(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const toggleRecording = () => {
    setIsRecording(!isRecording)
    // Implement voice recording logic
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'text-green-600'
      case 'idle': return 'text-yellow-600'
      case 'error': return 'text-red-600'
      default: return 'text-gray-600'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <CheckCircle className="w-4 h-4" />
      case 'idle': return <Clock className="w-4 h-4" />
      case 'error': return <AlertTriangle className="w-4 h-4" />
      default: return <MessageSquare className="w-4 h-4" />
    }
  }

  const getAgentIcon = (category: string) => {
    switch (category) {
      case 'content': return <MessageSquare className="w-4 h-4" />
      case 'strategy': return <TrendingUp className="w-4 h-4" />
      case 'research': return <BarChart3 className="w-4 h-4" />
      case 'analytics': return <BarChart3 className="w-4 h-4" />
      default: return <Brain className="w-4 h-4" />
    }
  }

  return (
    <div className="min-h-screen bg-[var(--paper)] p-6">
      <div className="max-w-7xl mx-auto h-[calc(100vh-3rem)]">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-full">

          {/* Sidebar - Agent Selection */}
          <div className="lg:col-span-1">
            <Card className="h-full">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Brain className="w-5 h-5" />
                  AI Agents
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {agents.map((agent) => (
                  <BlueprintCard
                    key={agent.id}
                    className={`p-4 cursor-pointer transition-all ${
                      selectedAgent?.id === agent.id ? 'ring-2 ring-[var(--blueprint)]' : ''
                    }`}
                    showCorners
                    onClick={() => startNewSession(agent)}
                  >
                    <div className="flex items-start gap-3">
                      <BlueprintAvatar
                        size="sm"
                        initials={agent.name.charAt(0)}
                        className="bg-[var(--ink)] text-[var(--paper)]"
                      />
                      <div className="flex-1">
                        <h3 className="font-semibold text-[var(--ink)]">{agent.name}</h3>
                        <p className="text-sm text-[var(--muted)] mt-1">{agent.description}</p>
                        <div className="flex items-center gap-2 mt-2">
                          <Badge variant="secondary" className="text-xs">
                            {agent.category}
                          </Badge>
                          <div className={`flex items-center gap-1 ${getStatusColor(agent.status)}`}>
                            {getStatusIcon(agent.status)}
                            <span className="text-xs">{agent.status}</span>
                          </div>
                        </div>
                        <div className="flex flex-wrap gap-1 mt-2">
                          {agent.capabilities.slice(0, 2).map((cap, idx) => (
                            <Badge key={idx} variant="outline" className="text-xs">
                              {cap}
                            </Badge>
                          ))}
                          {agent.capabilities.length > 2 && (
                            <Badge variant="outline" className="text-xs">
                              +{agent.capabilities.length - 2}
                            </Badge>
                          )}
                        </div>
                      </div>
                    </div>
                  </BlueprintCard>
                ))}
              </CardContent>
            </Card>
          </div>

          {/* Main Chat Area */}
          <div className="lg:col-span-3">
            <Card className="h-full flex flex-col">
              <CardHeader className="flex-shrink-0">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    {selectedAgent ? (
                      <>
                        <BlueprintAvatar
                          size="sm"
                          initials={selectedAgent.name.charAt(0)}
                          className="bg-[var(--ink)] text-[var(--paper)]"
                        />
                        <div>
                          <CardTitle className="text-lg">{selectedAgent.name}</CardTitle>
                          <p className="text-sm text-[var(--muted)]">{selectedAgent.description}</p>
                        </div>
                      </>
                    ) : (
                      <div>
                        <CardTitle className="text-lg">Select an Agent</CardTitle>
                        <p className="text-sm text-[var(--muted)]">Choose an AI agent to start chatting</p>
                      </div>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    {currentSession && (
                      <Button variant="outline" size="sm">
                        <Settings className="w-4 h-4" />
                      </Button>
                    )}
                  </div>
                </div>
              </CardHeader>

              <CardContent className="flex-1 flex flex-col p-0">
                {currentSession ? (
                  <>
                    {/* Messages Area */}
                    <div className="flex-1 overflow-y-auto p-6 space-y-4">
                      {currentSession.messages.map((message) => (
                        <div
                          key={message.id}
                          className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                        >
                          <div className={`max-w-[70%] ${message.type === 'user' ? 'order-2' : 'order-1'}`}>
                            <BlueprintCard
                              className={`p-4 ${
                                message.type === 'user'
                                  ? 'bg-[var(--ink)] text-[var(--paper)]'
                                  : 'bg-[var(--paper)] text-[var(--ink)]'
                              }`}
                              showCorners
                            >
                              <div className="space-y-2">
                                <div className="flex items-center gap-2">
                                  {message.type === 'agent' && (
                                    <BlueprintAvatar
                                      size="xs"
                                      initials={message.agentName?.charAt(0)}
                                      className="bg-[var(--ink)] text-[var(--paper)]"
                                    />
                                  )}
                                  <span className="font-medium">{message.agentName || 'You'}</span>
                                  <span className="text-xs opacity-70">
                                    {new Date(message.timestamp).toLocaleTimeString()}
                                  </span>
                                </div>
                                <div className="whitespace-pre-wrap">{message.content}</div>
                                {message.metadata && (
                                  <div className="flex items-center gap-4 text-xs opacity-70">
                                    <span>Tokens: {message.metadata.tokens}</span>
                                    <span>Cost: ${message.metadata.cost?.toFixed(4)}</span>
                                    <span>Latency: {message.metadata.latency}ms</span>
                                  </div>
                                )}
                              </div>
                            </BlueprintCard>
                          </div>
                        </div>
                      ))}

                      {isTyping && (
                        <div className="flex justify-start">
                          <div className="max-w-[70%]">
                            <BlueprintCard className="p-4">
                              <div className="flex items-center gap-2">
                                <BlueprintLoader size="sm" />
                                <span className="text-sm text-[var(--muted)]">Agent is thinking...</span>
                              </div>
                            </BlueprintCard>
                          </div>
                        </div>
                      )}

                      <div ref={messagesEndRef} />
                    </div>

                    {/* Input Area */}
                    <div className="border-t border-[var(--border)] p-4">
                      <div className="flex items-end gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          className="shrink-0"
                          onClick={() => setShowAgentSelector(!showAgentSelector)}
                        >
                          <Brain className="w-4 h-4" />
                        </Button>

                        <div className="flex-1">
                          <Textarea
                            ref={inputRef}
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyPress={handleKeyPress}
                            placeholder="Type your message..."
                            className="min-h-[40px] max-h-[120px] resize-none"
                            rows={1}
                          />
                        </div>

                        <Button
                          variant="outline"
                          size="sm"
                          className={`shrink-0 ${isRecording ? 'bg-red-500 text-white' : ''}`}
                          onClick={toggleRecording}
                        >
                          <Mic className="w-4 h-4" />
                        </Button>

                        <Button
                          size="sm"
                          className="shrink-0"
                          onClick={sendMessage}
                          disabled={!input.trim() || isTyping}
                        >
                          <Send className="w-4 h-4" />
                        </Button>
                      </div>

                      {showAgentSelector && (
                        <div className="mt-2 p-2 border border-[var(--border)] rounded-lg bg-[var(--paper)]">
                          <div className="text-sm text-[var(--muted)] mb-2">Switch to:</div>
                          <div className="grid grid-cols-2 gap-2">
                            {agents.map((agent) => (
                              <Button
                                key={agent.id}
                                variant="outline"
                                size="sm"
                                onClick={() => startNewSession(agent)}
                                className="justify-start"
                              >
                                <div className="flex items-center gap-2">
                                  {getAgentIcon(agent.category)}
                                  <span>{agent.name}</span>
                                </div>
                              </Button>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </>
                ) : (
                  <div className="flex-1 flex items-center justify-center">
                    <div className="text-center">
                      <Brain className="w-12 h-12 mx-auto mb-4 text-[var(--muted)]" />
                      <h3 className="text-lg font-semibold text-[var(--ink)] mb-2">
                        Select an Agent to Start
                      </h3>
                      <p className="text-[var(--muted)]">
                        Choose an AI agent from the sidebar to begin your conversation
                      </p>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
