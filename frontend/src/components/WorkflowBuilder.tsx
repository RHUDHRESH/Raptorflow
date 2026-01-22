/**
 * Workflow Builder Component
 * Visual workflow builder for LangGraph workflows
 */
"use client"

import { useState, useCallback, useRef, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { BlueprintCard } from "@/components/ui/BlueprintCard"
import { BlueprintAvatar } from "@/components/ui/BlueprintAvatar"
import { BlueprintLoader } from "@/components/ui/BlueprintLoader"
import { BlueprintProgress } from "@/components/ui/BlueprintProgress"
import {
  Plus,
  Play,
  Pause,
  Square,
  Settings,
  Zap,
  Brain,
  TrendingUp,
  BarChart3,
  Users,
  ArrowRight,
  Circle,
  Diamond,
  Square as SquareIcon,
  GitBranch,
  Save,
  Download,
  Upload,
  Trash2,
  Edit,
  Copy,
  CheckCircle,
  AlertTriangle,
  Clock
} from "lucide-react"

interface WorkflowNode {
  id: string
  type: "agent" | "condition" | "action" | "parallel" | "merge"
  name: string
  description: string
  position: { x: number; y: number }
  config: Record<string, any>
  status: "idle" | "running" | "completed" | "error"
  metadata: {
    agentId?: string
    agentName?: string
    condition?: string
    action?: string
    timeout?: number
    retryCount?: number
  }
}

interface WorkflowEdge {
  id: string
  from: string
  to: string
  type: "default" | "condition" | "parallel"
  condition?: string
  label?: string
}

interface Workflow {
  id: string
  name: string
  description: string
  nodes: WorkflowNode[]
  edges: WorkflowEdge[]
  status: "draft" | "active" | "paused" | "completed" | "error"
  createdAt: string
  updatedAt: string
  executionHistory: Array<{
    id: string
    startTime: string
    endTime?: string
    status: string
    results: Record<string, any>
  }>
}

interface WorkflowTemplate {
  id: string
  name: string
  description: string
  category: string
  nodes: Omit<WorkflowNode, 'id' | 'position'>[]
  edges: Omit<WorkflowEdge, 'id'>[]
}

export default function WorkflowBuilder() {
  const [workflows, setWorkflows] = useState<Workflow[]>([])
  const [currentWorkflow, setCurrentWorkflow] = useState<Workflow | null>(null)
  const [templates, setTemplates] = useState<WorkflowTemplate[]>([])
  const [selectedNode, setSelectedNode] = useState<WorkflowNode | null>(null)
  const [isExecuting, setIsExecuting] = useState(false)
  const [executionProgress, setExecutionProgress] = useState(0)
  const [showTemplates, setShowTemplates] = useState(false)
  const [draggedNode, setDraggedNode] = useState<WorkflowNode | null>(null)
  const [isConnecting, setIsConnecting] = useState(false)
  const [connectionStart, setConnectionStart] = useState<string | null>(null)
  const canvasRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    loadWorkflows()
    loadTemplates()
  }, [])

  const loadWorkflows = async () => {
    try {
      const response = await fetch('/api/workflows')
      const data = await response.json()
      setWorkflows(data)
    } catch (error) {
      console.error('Failed to load workflows:', error)
    }
  }

  const loadTemplates = async () => {
    try {
      const response = await fetch('/api/workflows/templates')
      const data = await response.json()
      setTemplates(data)
    } catch (error) {
      console.error('Failed to load templates:', error)
    }
  }

  const createNewWorkflow = () => {
    const newWorkflow: Workflow = {
      id: `workflow_${Date.now()}`,
      name: "New Workflow",
      description: "Describe your workflow here",
      nodes: [],
      edges: [],
      status: "draft",
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      executionHistory: []
    }
    setCurrentWorkflow(newWorkflow)
  }

  const createFromTemplate = (template: WorkflowTemplate) => {
    const newWorkflow: Workflow = {
      id: `workflow_${Date.now()}`,
      name: template.name,
      description: template.description,
      nodes: template.nodes.map((node, index) => ({
        ...node,
        id: `node_${index}`,
        position: { x: 100 + (index % 3) * 200, y: 100 + Math.floor(index / 3) * 150 }
      })),
      edges: template.edges.map((edge, index) => ({
        ...edge,
        id: `edge_${index}`
      })),
      status: "draft",
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      executionHistory: []
    }
    setCurrentWorkflow(newWorkflow)
    setShowTemplates(false)
  }

  const addNode = (type: WorkflowNode['type'], position: { x: number; y: number }) => {
    if (!currentWorkflow) return

    const newNode: WorkflowNode = {
      id: `node_${Date.now()}`,
      type,
      name: `${type.charAt(0).toUpperCase() + type.slice(1)} Node`,
      description: `New ${type} node`,
      position,
      config: {},
      status: "idle",
      metadata: {}
    }

    setCurrentWorkflow(prev => ({
      ...prev!,
      nodes: [...prev!.nodes, newNode]
    }))
  }

  const updateNode = (nodeId: string, updates: Partial<WorkflowNode>) => {
    if (!currentWorkflow) return

    setCurrentWorkflow(prev => ({
      ...prev!,
      nodes: prev!.nodes.map(node =>
        node.id === nodeId ? { ...node, ...updates } : node
      )
    }))
  }

  const deleteNode = (nodeId: string) => {
    if (!currentWorkflow) return

    setCurrentWorkflow(prev => ({
      ...prev!,
      nodes: prev!.nodes.filter(node => node.id !== nodeId),
      edges: prev!.edges.filter(edge => edge.from !== nodeId && edge.to !== nodeId)
    }))
  }

  const addEdge = (from: string, to: string, type: WorkflowEdge['type'] = 'default') => {
    if (!currentWorkflow) return

    const newEdge: WorkflowEdge = {
      id: `edge_${Date.now()}`,
      from,
      to,
      type
    }

    setCurrentWorkflow(prev => ({
      ...prev!,
      edges: [...prev!.edges, newEdge]
    }))
  }

  const deleteEdge = (edgeId: string) => {
    if (!currentWorkflow) return

    setCurrentWorkflow(prev => ({
      ...prev!,
      edges: prev!.edges.filter(edge => edge.id !== edgeId)
    }))
  }

  const executeWorkflow = async () => {
    if (!currentWorkflow) return

    setIsExecuting(true)
    setExecutionProgress(0)

    try {
      const response = await fetch('/api/workflows/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          workflowId: currentWorkflow.id,
          workflow: currentWorkflow
        })
      })

      const data = await response.json()

      // Update workflow with execution results
      setCurrentWorkflow(prev => ({
        ...prev!,
        status: data.status,
        executionHistory: [...prev!.executionHistory, data.execution]
      }))

      // Update node statuses
      if (data.nodeResults) {
        Object.entries(data.nodeResults).forEach(([nodeId, result]: [string, any]) => {
          updateNode(nodeId, { status: result.status })
        })
      }

    } catch (error) {
      console.error('Failed to execute workflow:', error)
      setCurrentWorkflow(prev => ({
        ...prev!,
        status: "error"
      }))
    } finally {
      setIsExecuting(false)
      setExecutionProgress(100)
    }
  }

  const pauseWorkflow = async () => {
    if (!currentWorkflow) return

    try {
      await fetch('/api/workflows/pause', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          workflowId: currentWorkflow.id
        })
      })

      setCurrentWorkflow(prev => ({
        ...prev!,
        status: "paused"
      }))
    } catch (error) {
      console.error('Failed to pause workflow:', error)
    }
  }

  const stopWorkflow = async () => {
    if (!currentWorkflow) return

    try {
      await fetch('/api/workflows/stop', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          workflowId: currentWorkflow.id
        })
      })

      setCurrentWorkflow(prev => ({
        ...prev!,
        status: "draft"
      }))
    } catch (error) {
      console.error('Failed to stop workflow:', error)
    }
  }

  const saveWorkflow = async () => {
    if (!currentWorkflow) return

    try {
      await fetch('/api/workflows/save', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          workflow: currentWorkflow
        })
      })

      setCurrentWorkflow(prev => ({
        ...prev!,
        updatedAt: new Date().toISOString()
      }))
    } catch (error) {
      console.error('Failed to save workflow:', error)
    }
  }

  const getNodeIcon = (type: WorkflowNode['type']) => {
    switch (type) {
      case 'agent': return <Brain className="w-4 h-4" />
      case 'condition': return <Diamond className="w-4 h-4" />
      case 'action': return <SquareIcon className="w-4 h-4" />
      case 'parallel': return <GitBranch className="w-4 h-4" />
      case 'merge': return <Circle className="w-4 h-4" />
      default: return <Zap className="w-4 h-4" />
    }
  }

  const getNodeColor = (status: WorkflowNode['status']) => {
    switch (status) {
      case 'idle': return 'bg-gray-100 border-gray-300'
      case 'running': return 'bg-blue-100 border-blue-300'
      case 'completed': return 'bg-green-100 border-green-300'
      case 'error': return 'bg-red-100 border-red-300'
      default: return 'bg-gray-100 border-gray-300'
    }
  }

  const getStatusIcon = (status: WorkflowNode['status']) => {
    switch (status) {
      case 'idle': return <Clock className="w-3 h-3" />
      case 'running': return <div className="w-3 h-3 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
      case 'completed': return <CheckCircle className="w-3 h-3" />
      case 'error': return <AlertTriangle className="w-3 h-3" />
      default: return <Clock className="w-3 h-3" />
    }
  }

  const handleNodeDragStart = (node: WorkflowNode) => {
    setDraggedNode(node)
  }

  const handleNodeDrop = (e: React.DragEvent, position: { x: number; y: number }) => {
    e.preventDefault()
    if (draggedNode) {
      updateNode(draggedNode.id, { position })
      setDraggedNode(null)
    }
  }

  const handleNodeClick = (node: WorkflowNode) => {
    setSelectedNode(node)
  }

  const handleCanvasClick = (e: React.MouseEvent) => {
    if (e.target === canvasRef.current) {
      setSelectedNode(null)
      setIsConnecting(false)
      setConnectionStart(null)
    }
  }

  const handleNodeConnect = (nodeId: string) => {
    if (!isConnecting) {
      setIsConnecting(true)
      setConnectionStart(nodeId)
    } else {
      if (connectionStart && connectionStart !== nodeId) {
        addEdge(connectionStart, nodeId)
      }
      setIsConnecting(false)
      setConnectionStart(null)
    }
  }

  return (
    <div className="min-h-screen bg-[var(--paper)] p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-[var(--ink)]">Workflow Builder</h1>
            <p className="text-[var(--muted)]">Create and manage LangGraph workflows</p>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" onClick={() => setShowTemplates(!showTemplates)}>
              <Upload className="w-4 h-4 mr-2" />
              Templates
            </Button>
            <Button variant="outline" onClick={createNewWorkflow}>
              <Plus className="w-4 h-4 mr-2" />
              New Workflow
            </Button>
          </div>
        </div>

        {/* Templates Panel */}
        {showTemplates && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Workflow Templates</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {templates.map((template) => (
                  <BlueprintCard
                    key={template.id}
                    className="p-4 cursor-pointer hover:ring-2 hover:ring-[var(--blueprint)]"
                    showCorners
                    onClick={() => createFromTemplate(template)}
                  >
                    <h3 className="font-semibold text-[var(--ink)]">{template.name}</h3>
                    <p className="text-sm text-[var(--muted)] mt-1">{template.description}</p>
                    <Badge variant="secondary" className="mt-2">
                      {template.category}
                    </Badge>
                  </BlueprintCard>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Workflow Canvas */}
        {currentWorkflow ? (
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            {/* Canvas */}
            <div className="lg:col-span-3">
              <Card className="h-[600px]">
                <CardHeader className="flex items-center justify-between">
                  <div>
                    <CardTitle className="text-lg">{currentWorkflow.name}</CardTitle>
                    <p className="text-sm text-[var(--muted)]">{currentWorkflow.description}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant={currentWorkflow.status === 'active' ? 'default' : 'secondary'}>
                      {currentWorkflow.status}
                    </Badge>
                    <div className="flex items-center gap-1">
                      <Button variant="outline" size="sm" onClick={saveWorkflow}>
                        <Save className="w-4 h-4" />
                      </Button>
                      <Button variant="outline" size="sm">
                        <Download className="w-4 h-4" />
                      </Button>
                      <Button variant="outline" size="sm">
                        <Copy className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="p-0">
                  <div
                    ref={canvasRef}
                    className="relative h-[500px] bg-[var(--paper)] border border-[var(--border)] rounded-lg overflow-hidden"
                    onClick={handleCanvasClick}
                    onDrop={(e) => handleNodeDrop(e, { x: 0, y: 0 })}
                    onDragOver={(e) => e.preventDefault()}
                  >
                    {/* Grid Background */}
                    <div className="absolute inset-0 opacity-5">
                      <div className="grid grid-cols-12 grid-rows-12 h-full">
                        {Array.from({ length: 144 }).map((_, i) => (
                          <div key={i} className="border border-[var(--border)]" />
                        ))}
                      </div>
                    </div>

                    {/* Nodes */}
                    {currentWorkflow.nodes.map((node) => (
                      <div
                        key={node.id}
                        className={`absolute cursor-move ${getNodeColor(node.status)} border-2 rounded-lg p-3 transition-all ${
                          selectedNode?.id === node.id ? 'ring-2 ring-[var(--blueprint)]' : ''
                        } ${isConnecting && connectionStart === node.id ? 'ring-2 ring-blue-500' : ''}`}
                        style={{
                          left: `${node.position.x}px`,
                          top: `${node.position.y}px`,
                          minWidth: '120px'
                        }}
                        draggable
                        onDragStart={() => handleNodeDragStart(node)}
                        onClick={() => handleNodeClick(node)}
                        onDoubleClick={() => handleNodeConnect(node.id)}
                      >
                        <div className="flex items-center gap-2">
                          {getNodeIcon(node.type)}
                          <div className="flex-1">
                            <div className="font-medium text-sm">{node.name}</div>
                            <div className="text-xs text-[var(--muted)]">{node.description}</div>
                          </div>
                          {getStatusIcon(node.status)}
                        </div>
                      </div>
                    ))}

                    {/* Edges */}
                    <svg className="absolute inset-0 pointer-events-none">
                      {currentWorkflow.edges.map((edge) => {
                        const fromNode = currentWorkflow.nodes.find(n => n.id === edge.from)
                        const toNode = currentWorkflow.nodes.find(n => n.id === edge.to)

                        if (!fromNode || !toNode) return null

                        const x1 = fromNode.position.x + 60
                        const y1 = fromNode.position.y + 30
                        const x2 = toNode.position.x + 60
                        const y2 = toNode.position.y + 30

                        return (
                          <g key={edge.id}>
                            <line
                              x1={x1}
                              y1={y1}
                              x2={x2}
                              y2={y2}
                              stroke={edge.type === 'condition' ? '#f59e0b' : '#6b7280'}
                              strokeWidth="2"
                              markerEnd="url(#arrowhead)"
                            />
                            {edge.label && (
                              <text
                                x={(x1 + x2) / 2}
                                y={(y1 + y2) / 2}
                                textAnchor="middle"
                                className="text-xs fill-[var(--muted)]"
                              >
                                {edge.label}
                              </text>
                            )}
                          </g>
                        )
                      })}
                      <defs>
                        <marker
                          id="arrowhead"
                          markerWidth="10"
                          markerHeight="10"
                          refX="9"
                          refY="3"
                          orient="auto"
                        >
                          <polygon
                            points="0 0, 10 3, 0 6"
                            fill="#6b7280"
                          />
                        </marker>
                      </defs>
                    </svg>

                    {/* Connection Mode Indicator */}
                    {isConnecting && (
                      <div className="absolute top-4 left-4 bg-blue-500 text-white px-3 py-1 rounded-lg text-sm">
                        Click a node to connect
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Properties Panel */}
            <div className="lg:col-span-1">
              <Card className="h-[600px]">
                <CardHeader>
                  <CardTitle className="text-lg">Properties</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {selectedNode ? (
                    <div className="space-y-4">
                      <div>
                        <label className="text-sm font-medium text-[var(--ink)]">Node Name</label>
                        <Input
                          value={selectedNode.name}
                          onChange={(e) => updateNode(selectedNode.id, { name: e.target.value })}
                          className="mt-1"
                        />
                      </div>
                      <div>
                        <label className="text-sm font-medium text-[var(--ink)]">Description</label>
                        <Input
                          value={selectedNode.description}
                          onChange={(e) => updateNode(selectedNode.id, { description: e.target.value })}
                          className="mt-1"
                        />
                      </div>
                      <div>
                        <label className="text-sm font-medium text-[var(--ink)]">Type</label>
                        <Badge variant="secondary" className="mt-1">
                          {selectedNode.type}
                        </Badge>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-[var(--ink)]">Status</label>
                        <Badge variant="secondary" className="mt-1">
                          {selectedNode.status}
                        </Badge>
                      </div>
                      <div className="flex items-center gap-2">
                        <Button variant="outline" size="sm">
                          <Edit className="w-4 h-4 mr-1" />
                          Edit
                        </Button>
                        <Button variant="outline" size="sm" onClick={() => deleteNode(selectedNode.id)}>
                          <Trash2 className="w-4 h-4 mr-1" />
                          Delete
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center text-[var(--muted)]">
                      <div className="mb-4">
                        <Zap className="w-8 h-8 mx-auto" />
                      </div>
                      <p>Select a node to edit properties</p>
                    </div>
                  )}

                  {/* Node Palette */}
                  <div className="border-t border-[var(--border)] pt-4">
                    <h4 className="font-medium text-[var(--ink)] mb-3">Add Nodes</h4>
                    <div className="space-y-2">
                      <Button
                        variant="outline"
                        size="sm"
                        className="w-full justify-start"
                        onClick={() => addNode('agent', { x: 100, y: 100 })}
                      >
                        <Brain className="w-4 h-4 mr-2" />
                        Agent Node
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        className="w-full justify-start"
                        onClick={() => addNode('condition', { x: 100, y: 100 })}
                      >
                        <Diamond className="w-4 h-4 mr-2" />
                        Condition Node
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        className="w-full justify-start"
                        onClick={() => addNode('action', { x: 100, y: 100 })}
                      >
                        <SquareIcon className="w-4 h-4 mr-2" />
                        Action Node
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        className="w-full justify-start"
                        onClick={() => addNode('parallel', { x: 100, y: 100 })}
                      >
                        <GitBranch className="w-4 h-4 mr-2" />
                        Parallel Node
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        className="w-full justify-start"
                        onClick={() => addNode('merge', { x: 100, y: 100 })}
                      >
                        <Circle className="w-4 h-4 mr-2" />
                        Merge Node
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        ) : (
          <div className="text-center py-12">
            <Zap className="w-16 h-16 mx-auto mb-4 text-[var(--muted)]" />
            <h2 className="text-xl font-semibold text-[var(--ink)] mb-2">No Workflow Selected</h2>
            <p className="text-[var(--muted)] mb-4">Create a new workflow or select an existing one</p>
            <Button onClick={createNewWorkflow}>
              <Plus className="w-4 h-4 mr-2" />
              Create New Workflow
            </Button>
          </div>
        )}

        {/* Execution Controls */}
        {currentWorkflow && (
          <Card className="mt-6">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <Button
                    onClick={executeWorkflow}
                    disabled={isExecuting || currentWorkflow.status === 'active'}
                  >
                    <Play className="w-4 h-4 mr-2" />
                    Execute
                  </Button>
                  <Button
                    variant="outline"
                    onClick={pauseWorkflow}
                    disabled={!isExecuting || currentWorkflow.status !== 'active'}
                  >
                    <Pause className="w-4 h-4 mr-2" />
                    Pause
                  </Button>
                  <Button
                    variant="outline"
                    onClick={stopWorkflow}
                    disabled={!isExecuting || currentWorkflow.status === 'draft'}
                  >
                    <Square className="w-4 h-4 mr-2" />
                    Stop
                  </Button>
                </div>
                {isExecuting && (
                  <div className="flex items-center gap-2">
                    <BlueprintLoader size="sm" />
                    <span className="text-sm text-[var(--muted)]">Executing...</span>
                    <BlueprintProgress value={executionProgress} className="w-32" />
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
