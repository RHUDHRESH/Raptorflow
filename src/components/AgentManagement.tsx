/**
 * Agent Management Component
 * Manage and configure AI agents
 */
"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { BlueprintCard } from "@/components/ui/BlueprintCard"
import { BlueprintAvatar } from "@/components/ui/BlueprintAvatar"
import { BlueprintLoader } from "@/components/ui/BlueprintLoader"
import { BlueprintProgress } from "@/components/ui/BlueprintProgress"
import { BlueprintModal } from "@/components/ui/BlueprintModal"
import { PageHeader } from "@/components/ui/PageHeader"
import {
  Brain,
  Plus,
  Edit,
  Trash2,
  Settings,
  Play,
  Pause,
  Square,
  CheckCircle,
  AlertTriangle,
  Clock,
  Zap,
  TrendingUp,
  Users,
  BarChart3,
  MessageSquare,
  Search,
  Filter,
  Download,
  Upload,
  RefreshCw,
  MoreVertical,
  Eye,
  Copy,
  Archive
} from "lucide-react"

interface Agent {
  id: string
  name: string
  description: string
  type: string
  category: string
  status: "active" | "idle" | "error" | "disabled"
  model_tier: "flash_lite" | "flash" | "pro"
  capabilities: string[]
  tools: string[]
  config: Record<string, any>
  performance: {
    execution_count: number
    avg_response_time: number
    success_rate: number
    total_tokens: number
    total_cost: number
    last_execution: string
  }
  created_at: string
  updated_at: string
}

interface AgentTemplate {
  id: string
  name: string
  description: string
  type: string
  category: string
  model_tier: string
  capabilities: string[]
  tools: string[]
  config: Record<string, any>
}

export default function AgentManagement() {
  const [agents, setAgents] = useState<Agent[]>([])
  const [templates, setTemplates] = useState<AgentTemplate[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedCategory, setSelectedCategory] = useState("all")
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [showTemplateModal, setShowTemplateModal] = useState(false)
  const [filterStatus, setFilterStatus] = useState("all")

  useEffect(() => {
    loadAgents()
    loadTemplates()
  }, [])

  const loadAgents = async () => {
    try {
      const response = await fetch('/api/agents')
      const data = await response.json()
      setAgents(data)
    } catch (error) {
      console.error('Failed to load agents:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadTemplates = async () => {
    try {
      const response = await fetch('/api/agents/templates')
      const data = await response.json()
      setTemplates(data)
    } catch (error) {
      console.error('Failed to load templates:', error)
    }
  }

  const createAgent = async (agentData: Partial<Agent>) => {
    try {
      const response = await fetch('/api/agents/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(agentData)
      })

      if (response.ok) {
        const newAgent = await response.json()
        setAgents(prev => [...prev, newAgent])
        setShowCreateModal(false)
      }
    } catch (error) {
      console.error('Failed to create agent:', error)
    }
  }

  const updateAgent = async (agentId: string, updates: Partial<Agent>) => {
    try {
      const response = await fetch(`/api/agents/${agentId}/update`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updates)
      })

      if (response.ok) {
        const updatedAgent = await response.json()
        setAgents(prev => prev.map(agent =>
          agent.id === agentId ? updatedAgent : agent
        ))
        setShowEditModal(false)
      }
    } catch (error) {
      console.error('Failed to update agent:', error)
    }
  }

  const deleteAgent = async (agentId: string) => {
    try {
      const response = await fetch(`/api/agents/${agentId}/delete`, {
        method: 'DELETE'
      })

      if (response.ok) {
        setAgents(prev => prev.filter(agent => agent.id !== agentId))
      }
    } catch (error) {
      console.error('Failed to delete agent:', error)
    }
  }

  const toggleAgentStatus = async (agentId: string, status: Agent['status']) => {
    try {
      const response = await fetch(`/api/agents/${agentId}/status`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status })
      })

      if (response.ok) {
        setAgents(prev => prev.map(agent =>
          agent.id === agentId ? { ...agent, status } : agent
        ))
      }
    } catch (error) {
      console.error('Failed to toggle agent status:', error)
    }
  }

  const testAgent = async (agentId: string) => {
    try {
      const response = await fetch(`/api/agents/${agentId}/test`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          test_message: "Hello, this is a test message."
        })
      })

      if (response.ok) {
        const result = await response.json()
        console.log('Agent test result:', result)
      }
    } catch (error) {
      console.error('Failed to test agent:', error)
    }
  }

  const createFromTemplate = (template: AgentTemplate) => {
    const newAgent: Partial<Agent> = {
      name: template.name,
      description: template.description,
      type: template.type,
      category: template.category,
      model_tier: template.model_tier as Agent['model_tier'],
      capabilities: template.capabilities,
      tools: template.tools,
      config: template.config,
      status: "idle"
    }

    createAgent(newAgent)
    setShowTemplateModal(false)
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'text-green-600'
      case 'idle': return 'text-yellow-600'
      case 'error': return 'text-red-600'
      case 'disabled': return 'text-gray-600'
      default: return 'text-gray-600'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <CheckCircle className="w-4 h-4" />
      case 'idle': return <Clock className="w-4 h-4" />
      case 'error': return <AlertTriangle className="w-4 h-4" />
      case 'disabled': return <Square className="w-4 h-4" />
      default: return <Clock className="w-4 h-4" />
    }
  }

  const getModelTierColor = (tier: string) => {
    switch (tier) {
      case 'flash_lite': return 'bg-blue-100 text-blue-800'
      case 'flash': return 'bg-green-100 text-green-800'
      case 'pro': return 'bg-purple-100 text-purple-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'content': return <MessageSquare className="w-4 h-4" />
      case 'strategy': return <TrendingUp className="w-4 h-4" />
      case 'research': return <BarChart3 className="w-4 h-4" />
      case 'analytics': return <BarChart3 className="w-4 h-4" />
      case 'onboarding': return <Users className="w-4 h-4" />
      default: return <Brain className="w-4 h-4" />
    }
  }

  const filteredAgents = agents.filter(agent => {
    const matchesSearch = agent.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         agent.description.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesCategory = selectedCategory === "all" || agent.category === selectedCategory
    const matchesStatus = filterStatus === "all" || agent.status === filterStatus

    return matchesSearch && matchesCategory && matchesStatus
  })

  const categories = Array.from(new Set(agents.map(agent => agent.category)))

  if (loading) {
    return (
      <div className="min-h-screen bg-[var(--paper)] p-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center h-64">
              <BlueprintLoader size="lg" />
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[var(--paper)] p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <PageHeader
          title="Agent Management"
          descriptor="Manage and configure your AI agents"
          moduleCode="agents"
          actions={
            <div className="flex items-center gap-2">
              <Button variant="outline" onClick={() => setShowTemplateModal(true)}>
                <Upload className="w-4 h-4 mr-2" />
                Templates
              </Button>
              <Button variant="outline" onClick={loadAgents}>
                <RefreshCw className="w-4 h-4 mr-2" />
                Refresh
              </Button>
              <Button onClick={() => setShowCreateModal(true)}>
                <Plus className="w-4 h-4 mr-2" />
                Create Agent
              </Button>
            </div>
          }
        />

        {/* Filters */}
        <Card>
          <CardContent className="p-4">
            <div className="flex flex-wrap items-center gap-4">
              <div className="flex items-center gap-2">
                <Search className="w-4 h-4 text-[var(--muted)]" />
                <Input
                  placeholder="Search agents..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-64"
                />
              </div>

              <div className="flex items-center gap-2">
                <Filter className="w-4 h-4 text-[var(--muted)]" />
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="px-3 py-2 border border-[var(--border)] rounded-lg bg-[var(--paper)] text-[var(--ink)]"
                >
                  <option value="all">All Categories</option>
                  {categories.map(category => (
                    <option key={category} value={category}>
                      {category.charAt(0).toUpperCase() + category.slice(1)}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex items-center gap-2">
                <Filter className="w-4 h-4 text-[var(--muted)]" />
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  className="px-3 py-2 border border-[var(--border)] rounded-lg bg-[var(--paper)] text-[var(--ink)]"
                >
                  <option value="all">All Status</option>
                  <option value="active">Active</option>
                  <option value="idle">Idle</option>
                  <option value="error">Error</option>
                  <option value="disabled">Disabled</option>
                </select>
              </div>

              <div className="ml-auto text-sm text-[var(--muted)]">
                {filteredAgents.length} agents
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Agent Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredAgents.map((agent) => (
            <BlueprintCard
              key={agent.id}
              className="p-6 hover:ring-2 hover:ring-[var(--blueprint)] transition-all cursor-pointer"
              onClick={() => setSelectedAgent(agent)}
            >
              <div className="space-y-4">
                {/* Header */}
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-[var(--ink)] text-[var(--paper)] rounded-full flex items-center justify-center font-semibold">
                      {agent.name.charAt(0)}
                    </div>
                    <div>
                      <h3 className="font-semibold text-[var(--ink)]">{agent.name}</h3>
                      <p className="text-sm text-[var(--muted)]">{agent.description}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-1">
                    <div className={getStatusColor(agent.status)}>
                      {getStatusIcon(agent.status)}
                    </div>
                  </div>
                </div>

                {/* Badges */}
                <div className="flex flex-wrap gap-2">
                  <Badge variant="secondary" className="text-xs">
                    {agent.category}
                  </Badge>
                  <Badge className={`text-xs ${getModelTierColor(agent.model_tier)}`}>
                    {agent.model_tier}
                  </Badge>
                  <Badge variant="outline" className="text-xs">
                    {agent.type}
                  </Badge>
                </div>

                {/* Capabilities */}
                <div>
                  <h4 className="text-sm font-medium text-[var(--ink)] mb-2">Capabilities</h4>
                  <div className="flex flex-wrap gap-1">
                    {agent.capabilities.slice(0, 3).map((capability, index) => (
                      <Badge key={index} variant="outline" className="text-xs">
                        {capability}
                      </Badge>
                    ))}
                    {agent.capabilities.length > 3 && (
                      <Badge variant="outline" className="text-xs">
                        +{agent.capabilities.length - 3}
                      </Badge>
                    )}
                  </div>
                </div>

                {/* Performance */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-[var(--muted)]">Success Rate</span>
                    <div className="flex items-center gap-2">
                      <BlueprintProgress value={agent.performance.success_rate} className="w-16 h-2" />
                      <span className="text-sm font-medium text-[var(--ink)]">
                        {agent.performance.success_rate}%
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-[var(--muted)]">Avg Response</span>
                    <span className="text-sm font-medium text-[var(--ink)]">
                      {agent.performance.avg_response_time}ms
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-[var(--muted)]">Executions</span>
                    <span className="text-sm font-medium text-[var(--ink)]">
                      {agent.performance.execution_count.toLocaleString()}
                    </span>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center justify-between pt-4 border-t border-[var(--border)]">
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation()
                        testAgent(agent.id)
                      }}
                    >
                      <Play className="w-3 h-3" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation()
                        toggleAgentStatus(agent.id, agent.status === 'active' ? 'idle' : 'active')
                      }}
                    >
                      {agent.status === 'active' ? <Pause className="w-3 h-3" /> : <Play className="w-3 h-3" />}
                    </Button>
                  </div>
                  <div className="flex items-center gap-1">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation()
                        setShowEditModal(true)
                      }}
                    >
                      <Edit className="w-3 h-3" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation()
                        deleteAgent(agent.id)
                      }}
                    >
                      <Trash2 className="w-3 h-3" />
                    </Button>
                  </div>
                </div>
              </div>
            </BlueprintCard>
          ))}
        </div>

        {/* Empty State */}
        {filteredAgents.length === 0 && (
          <div className="text-center py-12">
            <Brain className="w-16 h-16 mx-auto mb-4 text-[var(--muted)]" />
            <h3 className="text-xl font-semibold text-[var(--ink)] mb-2">No agents found</h3>
            <p className="text-[var(--muted)] mb-4">Create your first AI agent to get started</p>
            <Button onClick={() => setShowCreateModal(true)}>
              <Plus className="w-4 h-4 mr-2" />
              Create Agent
            </Button>
          </div>
        )}

        {/* Create Agent Modal */}
        {showCreateModal && (
          <BlueprintModal
            isOpen={showCreateModal}
            onClose={() => setShowCreateModal(false)}
            title="Create New Agent"
            size="lg"
          >
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-[var(--ink)] mb-1">Name</label>
                <Input placeholder="Agent name" />
              </div>
              <div>
                <label className="block text-sm font-medium text-[var(--ink)] mb-1">Description</label>
                <Input placeholder="Agent description" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-[var(--ink)] mb-1">Type</label>
                  <select className="w-full px-3 py-2 border border-[var(--border)] rounded-lg bg-[var(--paper)] text-[var(--ink)]">
                    <option>specialist</option>
                    <option>general</option>
                    <option>custom</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-[var(--ink)] mb-1">Category</label>
                  <select className="w-full px-3 py-2 border border-[var(--border)] rounded-lg bg-[var(--paper)] text-[var(--ink)]">
                    <option>content</option>
                    <option>strategy</option>
                    <option>research</option>
                    <option>analytics</option>
                    <option>onboarding</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-[var(--ink)] mb-1">Model Tier</label>
                <select className="w-full px-3 py-2 border border-[var(--border)] rounded-lg bg-[var(--paper)] text-[var(--ink)]">
                  <option>flash_lite</option>
                  <option>flash</option>
                  <option>pro</option>
                </select>
              </div>
              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={() => setShowCreateModal(false)}>
                  Cancel
                </Button>
                <Button onClick={() => createAgent({})}>
                  Create Agent
                </Button>
              </div>
            </div>
          </BlueprintModal>
        )}

        {/* Template Modal */}
        {showTemplateModal && (
          <BlueprintModal
            isOpen={showTemplateModal}
            onClose={() => setShowTemplateModal(false)}
            title="Agent Templates"
            size="lg"
          >
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {templates.map((template) => (
                <BlueprintCard
                  key={template.id}
                  className="p-4 cursor-pointer hover:ring-2 hover:ring-[var(--blueprint)] transition-all"
                  onClick={() => createFromTemplate(template)}
                >
                  <div className="space-y-2">
                    <h3 className="font-semibold text-[var(--ink)]">{template.name}</h3>
                    <p className="text-sm text-[var(--muted)]">{template.description}</p>
                    <div className="flex flex-wrap gap-2">
                      <Badge variant="secondary" className="text-xs">
                        {template.category}
                      </Badge>
                      <Badge className={`text-xs ${getModelTierColor(template.model_tier)}`}>
                        {template.model_tier}
                      </Badge>
                    </div>
                  </div>
                </BlueprintCard>
              ))}
            </div>
          </BlueprintModal>
        )}
      </div>
    </div>
  )
}
