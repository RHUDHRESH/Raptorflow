'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Input } from '@/components/ui/input';
import {
  CheckCircle2,
  Circle,
  Clock,
  AlertTriangle,
  TrendingUp,
  Layout,
  FileText,
  BarChart3,
  MoreHorizontal,
  Calendar as CalendarIcon,
  ChevronDown,
  ChevronUp,
  ChevronRight,
  BrainCircuit,
  X,
  Play,
  Pause,
  Edit2,
  Save,
} from 'lucide-react';
import { Move, CouncilResponse } from '@/lib/campaigns-types';
import { updateMove, updateMoveTasks } from '@/lib/api';
import { cn } from '@/lib/utils';
import { PedigreeVisualizer } from '@/components/council/PedigreeVisualizer';
import { ConfidenceHeatmap } from '@/components/council/ConfidenceHeatmap';
import { EXPERTS } from '@/components/council/CouncilChamber';
import { toast } from 'sonner';
import { createMuseAsset } from '@/lib/muse/api';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

interface MoveDetailProps {
  move: Move | null;
  rationale: CouncilResponse | null;
  open?: boolean;
  onClose?: () => void;
  onUpdate: (updates: Partial<Move>) => void;
  onToggleTask: (taskId: string) => void;
  onRefresh?: () => void;
  standalone?: boolean;
}

export function MoveDetail({
  move,
  rationale,
  open = true,
  onClose = () => { },
  onUpdate,
  onToggleTask,
  onRefresh,
  standalone = false,
}: MoveDetailProps) {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState('rationale');
  const [showExperts, setShowExperts] = useState(false);
  const [showRejected, setShowRejected] = useState(false);
  const [selectedTask, setSelectedTask] = useState<string | null>(null);

  // Editing State
  const [isEditing, setIsEditing] = useState(false);
  const [editName, setEditName] = useState('');
  const [editGoal, setEditGoal] = useState('');
  const [editDuration, setEditDuration] = useState(0);

  useEffect(() => {
    if (move) {
      setEditName(move.name);
      setEditGoal(move.goal);
      setEditDuration(move.duration);
    }
  }, [move?.id]);

  if (!move) return null;

  const handleSaveEdit = async () => {
    onUpdate({
      name: editName,
      goal: editGoal as any,
      duration: editDuration as any,
    });
    setIsEditing(false);
  };

  const handleStatusChange = (newStatus: Move['status']) => {
    onUpdate({ status: newStatus });
  };

  // Mock metrics data with confidence trend
  const metricsData = [
    { day: 'Mon', leads: 2, calls: 0, confidence: 85 },
    { day: 'Tue', leads: 4, calls: 1, confidence: 88 },
    { day: 'Wed', leads: 3, calls: 1, confidence: 82 },
    { day: 'Thu', leads: 8, calls: 3, confidence: 90 },
    { day: 'Fri', leads: 12, calls: 5, confidence: 94 },
    { day: 'Sat', leads: 5, calls: 2, confidence: 91 },
    { day: 'Sun', leads: 3, calls: 1, confidence: 89 },
  ];

  const selectedChecklistItem = move.checklist.find(
    (t) => t.id === selectedTask
  );

  const Content = (
    <div
      className={cn(
        'flex flex-col h-full bg-canvas',
        standalone ? 'min-h-screen' : 'max-w-5xl h-[90vh]'
      )}
    >
      {/* Header */}
      <div className="p-6 border-b border-borders/50 flex justify-between items-start bg-background/50 backdrop-blur-sm z-10">
        <div className="space-y-2 flex-1 mr-8">
          <div className="flex items-center gap-3 mb-1">
            <span className="text-[10px] uppercase tracking-widest font-mono text-muted-foreground">
              {move.campaignName || 'Uncategorized Move'}
            </span>
            <ChevronRight className="w-3 h-3 text-muted-foreground/50" />
            <Badge
              variant="outline"
              className="uppercase tracking-widest text-[10px] font-mono border-accent/20 text-accent"
            >
              {move.channel}
            </Badge>
          </div>

          <div className="flex items-center gap-3">
            <div className={cn(
              "w-2.5 h-2.5 rounded-full",
              move.rag === 'green' ? "bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.4)]" :
                move.rag === 'amber' ? "bg-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.4)]" :
                  "bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.4)]"
            )} title={`RAG Status: ${move.rag || 'green'}`} />
            <span
              className={cn(
                'text-[10px] uppercase tracking-widest font-bold',
                move.status === 'active'
                  ? 'text-emerald-500'
                  : 'text-muted-foreground'
              )}
            >
              {move.status} status
            </span>
          </div>

          {isEditing ? (
            <div className="space-y-4 max-w-md animate-in fade-in slide-in-from-left-2">
              <Input
                value={editName}
                onChange={(e) => setEditName(e.target.value)}
                className="text-2xl font-serif h-12"
                placeholder="Move Name"
              />
              <div className="flex gap-4">
                <div className="flex-1">
                  <label className="text-[10px] uppercase tracking-wider text-muted-foreground font-bold">
                    Strategic Goal
                  </label>
                  <select
                    value={editGoal}
                    onChange={(e) => setEditGoal(e.target.value)}
                    className="w-full h-9 rounded-md border border-borders bg-surface px-3 py-1 text-sm shadow-sm focus:ring-1 focus:ring-accent outline-none"
                  >
                    <option value="leads">Leads</option>
                    <option value="calls">Calls</option>
                    <option value="sales">Sales</option>
                    <option value="proof">Proof</option>
                    <option value="distribution">Distribution</option>
                  </select>
                </div>
                <div className="flex-1">
                  <label className="text-[10px] uppercase tracking-wider text-muted-foreground font-bold">
                    Duration (Days)
                  </label>
                  <Input
                    type="number"
                    value={editDuration}
                    onChange={(e) => setEditDuration(parseInt(e.target.value))}
                    className="h-9"
                  />
                </div>
              </div>
              <div className="flex gap-2">
                <Button
                  size="sm"
                  onClick={handleSaveEdit}
                  className="bg-ink text-white"
                >
                  Save Changes
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => setIsEditing(false)}
                >
                  Cancel
                </Button>
              </div>
            </div>
          ) : (
            <>
              {standalone ? (
                <h1 className="text-3xl font-serif text-ink flex items-center gap-2 group">
                  {move.name}
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity"
                    onClick={() => setIsEditing(true)}
                  >
                    <Edit2 className="w-3 h-3 text-muted-foreground" />
                  </Button>
                </h1>
              ) : (
                <DialogTitle className="text-3xl font-serif text-ink flex items-center gap-2 group">
                  {move.name}
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity"
                    onClick={() => setIsEditing(true)}
                  >
                    <Edit2 className="w-3 h-3 text-muted-foreground" />
                  </Button>
                </DialogTitle>
              )}
              <div className="flex items-center gap-4 text-sm text-muted-foreground">
                <span className="flex items-center gap-1.5">
                  <Clock className="w-4 h-4" />
                  {move.duration} Day Protocol
                </span>
                <span className="flex items-center gap-1.5">
                  <TrendingUp className="w-4 h-4" />
                  Target: {move.goal}
                </span>
                <span className="flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4" />
                  {Math.round(
                    (move.checklist.filter((t) => t.completed).length /
                      move.checklist.length) *
                    100 || 0
                  )}
                  % Execution
                </span>
              </div>
            </>
          )}
        </div>

        <div className="flex items-center gap-2">
          {onRefresh && (
            <Button variant="ghost" size="sm" onClick={onRefresh} className="text-secondary-text h-9">
              Refresh Data
            </Button>
          )}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" className="gap-2 border-borders bg-surface h-9">
                {move.status === 'active' ? (
                  <Pause className="w-4 h-4" />
                ) : (
                  <Play className="w-4 h-4" />
                )}
                {move.status === 'active' ? 'Pause' : 'Start'} Objective
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="bg-surface border-borders">
              <DropdownMenuItem onClick={() => handleStatusChange('active')}>
                Resume Active
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => handleStatusChange('paused')}>
                Enter Pause State
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => handleStatusChange('completed')} className="text-emerald-500 font-bold">
                Archive as Complete
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
          {!standalone && (
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X className="w-5 h-5" />
            </Button>
          )}
        </div>
      </div>

      <div className="flex-1 overflow-hidden flex flex-col">
        <Tabs
          value={activeTab}
          onValueChange={setActiveTab}
          className="h-full flex flex-col"
        >
          <div className="px-6 border-b border-borders/50 bg-background/30">
            <TabsList className="bg-transparent h-14 w-full justify-start gap-8 p-0">
              <TabsTrigger
                value="rationale"
                className="data-[state=active]:bg-transparent data-[state=active]:border-b-2 data-[state=active]:border-accent rounded-none h-full px-0 font-display text-base"
              >
                Council Rationale
              </TabsTrigger>
              <TabsTrigger
                value="execution"
                className="data-[state=active]:bg-transparent data-[state=active]:border-b-2 data-[state=active]:border-accent rounded-none h-full px-0 font-display text-base"
              >
                Execution Plan
              </TabsTrigger>
              <TabsTrigger
                value="metrics"
                className="data-[state=active]:bg-transparent data-[state=active]:border-b-2 data-[state=active]:border-accent rounded-none h-full px-0 font-display text-base"
              >
                Activity & Metrics
              </TabsTrigger>
            </TabsList>
          </div>

          <ScrollArea className="flex-1 bg-muted/20">
            <div className="p-8 max-w-5xl mx-auto space-y-8 pb-32">
              <TabsContent
                value="rationale"
                className="m-0 space-y-8 animate-in fade-in slide-in-from-bottom-2"
              >
                {!rationale ? (
                  <div className="flex items-center justify-center h-64">
                    <div className="animate-pulse flex flex-col items-center gap-4">
                      <BrainCircuit className="w-8 h-8 text-accent/50" />
                      <span className="text-sm text-muted-foreground font-mono">
                        Strategizing...
                      </span>
                    </div>
                  </div>
                ) : (
                  <>
                    {/* Strategic Decree */}
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                      <div className="lg:col-span-2 space-y-6">
                        <section className="bg-surface border border-borders/50 rounded-2xl p-8 shadow-sm">
                          <h3 className="text-xs font-bold uppercase tracking-widest text-muted-fill mb-4 flex items-center gap-2">
                            <BrainCircuit className="h-4 w-4" />
                            Strategic Decree
                          </h3>
                          <p className="text-xl font-serif italic text-ink leading-relaxed">
                            "{rationale?.strategicDecree}"
                          </p>
                          <div className="mt-8">
                            <PedigreeVisualizer />
                          </div>
                        </section>

                        {/* Collapsible Expert Perspectives */}
                        <section className="space-y-4">
                          <button
                            onClick={() => setShowExperts(!showExperts)}
                            className="flex items-center justify-between w-full group"
                          >
                            <h3 className="text-xs font-bold uppercase tracking-widest text-muted-fill flex items-center gap-2 group-hover:text-ink transition-colors">
                              <MoreHorizontal className="h-3 w-3" />
                              Expert Perspectives
                            </h3>
                            {showExperts ? (
                              <ChevronUp className="w-4 h-4 text-muted-foreground" />
                            ) : (
                              <ChevronDown className="w-4 h-4 text-muted-foreground" />
                            )}
                          </button>

                          {showExperts && (
                            <div className="grid gap-3 animate-in slide-in-from-top-2 fade-in">
                              {rationale?.debateTranscript?.map((item, i) => (
                                <div
                                  key={i}
                                  className="bg-surface border border-borders/30 rounded-xl p-4 flex gap-4"
                                >
                                  <Avatar className="h-8 w-8 shrink-0">
                                    <AvatarFallback className="bg-accent/10 text-accent font-bold text-xs">
                                      {item.role[0]}
                                    </AvatarFallback>
                                  </Avatar>
                                  <div>
                                    <p className="text-xs font-bold text-ink uppercase tracking-wider mb-1">
                                      {item.role}
                                    </p>
                                    <p className="text-sm text-secondary-text leading-relaxed">
                                      "{item.argument}"
                                    </p>
                                  </div>
                                </div>
                              ))}
                            </div>
                          )}
                        </section>
                      </div>

                      <div className="space-y-6">
                        {/* Alignment */}
                        <div className="bg-surface border border-borders/50 rounded-2xl p-6">
                          <div className="grid grid-cols-2 gap-4 mb-6">
                            <div>
                              <p className="text-[10px] uppercase tracking-widest text-muted-foreground mb-1">
                                Confidence
                              </p>
                              <p className="text-3xl font-mono text-ink">
                                {(rationale?.confidence || 0) * 100}%
                              </p>
                            </div>
                            <div>
                              <p className="text-[10px] uppercase tracking-widest text-muted-foreground mb-1">
                                Risk Level
                              </p>
                              <p className="text-3xl font-mono text-amber-600">
                                Low
                              </p>
                            </div>
                          </div>
                          <ConfidenceHeatmap />
                        </div>

                        {/* Discarded Paths */}
                        <div className="bg-surface border border-borders/50 rounded-2xl p-6">
                          <button
                            onClick={() => setShowRejected(!showRejected)}
                            className="flex items-center justify-between w-full mb-4 group"
                          >
                            <h3 className="text-xs font-bold uppercase tracking-widest text-muted-fill flex items-center gap-2 group-hover:text-ink transition-colors">
                              <AlertTriangle className="h-3 w-3" />
                              Rejected Paths
                            </h3>
                            {showRejected ? (
                              <ChevronUp className="w-4 h-4 text-muted-foreground" />
                            ) : (
                              <ChevronDown className="w-4 h-4 text-muted-foreground" />
                            )}
                          </button>

                          {showRejected && (
                            <div className="space-y-4 animate-in slide-in-from-top-2 fade-in">
                              {rationale?.rejectedPaths?.map((path, i) => (
                                <div
                                  key={i}
                                  className="p-3 bg-muted/30 rounded-lg border border-borders/20"
                                >
                                  <p className="text-xs font-bold text-ink mb-1">
                                    {path.path}
                                  </p>
                                  <p className="text-[11px] text-muted-foreground">
                                    {path.reason}
                                  </p>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </>
                )}
              </TabsContent>

              <TabsContent
                value="execution"
                className="m-0 animate-in fade-in slide-in-from-bottom-2 h-full flex flex-col lg:flex-row gap-6"
              >
                <div className="flex-1 space-y-6">
                  <div className="bg-surface border border-borders/50 rounded-2xl p-8">
                    <h3 className="text-lg font-display font-medium mb-6">
                      Tactical Checklist
                    </h3>
                    <div className="space-y-1">
                      {move.checklist.map((task) => (
                        <div
                          key={task.id}
                          className={cn(
                            'group flex items-center gap-4 p-4 rounded-xl transition-all duration-200 border border-transparent cursor-pointer',
                            task.completed
                              ? 'bg-muted/10 opacity-60'
                              : 'hover:bg-muted/20 hover:border-borders/30',
                            selectedTask === task.id
                              ? 'bg-muted/20 border-accent/30 ring-1 ring-accent/30'
                              : ''
                          )}
                          onClick={() => setSelectedTask(task.id)}
                        >
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              onToggleTask(task.id);
                            }}
                            className={cn(
                              'flex-shrink-0 w-6 h-6 rounded-full border-2 flex items-center justify-center transition-colors',
                              task.completed
                                ? 'bg-accent border-accent text-white'
                                : 'border-muted-foreground/30 hover:border-accent'
                            )}
                          >
                            {task.completed && (
                              <CheckCircle2 className="w-4 h-4" />
                            )}
                          </button>
                          <div className="flex-1 min-w-0">
                            <p
                              className={cn(
                                'text-sm font-medium truncate transition-all',
                                task.completed
                                  ? 'text-muted-foreground line-through'
                                  : 'text-ink'
                              )}
                            >
                              {task.label}
                            </p>
                            <div className="flex items-center gap-3 mt-1">
                              <p className="text-xs text-muted-foreground capitalize">
                                {task.group} Phase
                              </p>
                              {task.completed && (
                                <span className="text-[10px] text-emerald-600 bg-emerald-50 px-1.5 rounded-sm">
                                  Done
                                </span>
                              )}
                            </div>
                          </div>
                          <Button
                            variant="ghost"
                            size="sm"
                            className={cn(
                              'transition-opacity text-xs h-7 text-muted-foreground',
                              selectedTask === task.id
                                ? 'opacity-100'
                                : 'opacity-0 group-hover:opacity-100'
                            )}
                          >
                            Details <ChevronRight className="w-3 h-3 ml-1" />
                          </Button>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="w-full lg:w-[350px] shrink-0 space-y-6">
                  {selectedChecklistItem ? (
                    <div className="bg-surface border border-borders/50 rounded-2xl p-6 animate-in slide-in-from-right-4 fade-in duration-300">
                      <div className="flex items-center justify-between mb-6">
                        <h3 className="text-sm font-bold uppercase tracking-widest text-muted-fill">
                          Task Details
                        </h3>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-6 w-6"
                          onClick={() => setSelectedTask(null)}
                        >
                          <X className="w-4 h-4 text-muted-foreground" />
                        </Button>
                      </div>

                      <div className="space-y-6">
                        <div>
                          <h4 className="text-lg font-serif text-ink mb-2">
                            {selectedChecklistItem.label}
                          </h4>
                          <Badge variant="outline" className="capitalize">
                            {selectedChecklistItem.group}
                          </Badge>
                        </div>

                        <div className="space-y-2">
                          <p className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
                            Proposed By
                          </p>
                          <div className="flex items-center gap-2">
                            <Avatar className="h-6 w-6">
                              <AvatarFallback className="bg-ink text-white text-[10px]">
                                ST
                              </AvatarFallback>
                            </Avatar>
                            <span className="text-sm font-medium text-ink">
                              The Strategist
                            </span>
                          </div>
                        </div>

                        {/* Muse Prompt Display */}
                        <div className="space-y-2">
                          <p className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
                            Muse Prompt
                          </p>
                          <div className="text-xs font-mono text-secondary-text bg-muted/30 p-3 rounded-lg border border-borders/20 overflow-x-auto whitespace-pre-wrap">
                            {selectedChecklistItem.muse_prompt ||
                              'No prompt available.'}
                          </div>
                        </div>

                        <div className="pt-4 border-t border-borders/20">
                          <Button
                            className="w-full bg-surface border border-borders hover:bg-muted/10 text-ink"
                            onClick={async () => {
                              const refinementPrompt =
                                typeof move.refinementData?.muse_prompt === 'string'
                                  ? move.refinementData.muse_prompt
                                  : '';
                              const prompt =
                                selectedChecklistItem.muse_prompt ||
                                refinementPrompt ||
                                move.description ||
                                `Create asset for ${move.name}`;
                              try {
                                toast.loading('Creating Muse asset...', {
                                  id: 'muse-create',
                                });
                                const asset = await createMuseAsset(
                                  prompt,
                                  'email',
                                  JSON.stringify({
                                    move_id: move.id,
                                    campaign_id: move.campaignId,
                                    source: 'move-task',
                                  })
                                );
                                toast.success('Muse asset ready.', {
                                  id: 'muse-create',
                                });
                                router.push(`/muse?asset_id=${asset.id}`);
                              } catch (error) {
                                toast.error('Failed to create Muse asset.', {
                                  id: 'muse-create',
                                });
                              }
                            }}
                          >
                            Open Workspace
                          </Button>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <>
                      <div className="bg-surface border border-borders/50 rounded-2xl p-6">
                        <h3 className="text-sm font-bold mb-4">Requirements</h3>
                        <div className="flex flex-wrap gap-2">
                          {move.toolRequirements?.map((tool) => (
                            <Badge
                              key={tool}
                              variant="secondary"
                              className="bg-muted text-muted-foreground font-mono text-[10px]"
                            >
                              {tool}
                            </Badge>
                          ))}
                        </div>
                      </div>

                      <div className="bg-gradient-to-br from-accent/10 to-transparent border border-accent/20 rounded-2xl p-6">
                        <h3 className="text-sm font-bold text-accent mb-2">
                          Micro-Win
                        </h3>
                        <p className="text-sm text-secondary-text leading-relaxed">
                          Completing this move contributes to the{' '}
                          <span className="font-bold text-ink">
                            "Authority Builder"
                          </span>{' '}
                          milestone.
                        </p>
                      </div>
                    </>
                  )}
                </div>
              </TabsContent>

              <TabsContent
                value="metrics"
                className="m-0 animate-in fade-in slide-in-from-bottom-2"
              >
                <div className="bg-surface border border-borders/50 rounded-2xl p-8">
                  <div className="flex items-center justify-between mb-8">
                    <div>
                      <h3 className="text-lg font-display font-medium">
                        Performance Velocity
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        Real-time impact tracking
                      </p>
                    </div>
                    <div className="flex gap-4">
                      <div className="text-right">
                        <p className="text-2xl font-mono font-bold text-ink">
                          37
                        </p>
                        <p className="text-xs text-muted-foreground uppercase tracking-wider">
                          Leads
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-2xl font-mono font-bold text-ink">
                          12
                        </p>
                        <p className="text-xs text-muted-foreground uppercase tracking-wider">
                          Calls
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="h-[400px] w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={metricsData}>
                        <CartesianGrid
                          strokeDasharray="3 3"
                          opacity={0.05}
                          vertical={false}
                        />
                        <XAxis
                          dataKey="day"
                          axisLine={false}
                          tickLine={false}
                          tick={{ fontSize: 12, fill: '#9ca3af' }}
                          dy={10}
                        />
                        <YAxis
                          yAxisId="left"
                          axisLine={false}
                          tickLine={false}
                          tick={{ fontSize: 12, fill: '#9ca3af' }}
                        />
                        <YAxis
                          yAxisId="right"
                          orientation="right"
                          domain={[0, 100]}
                          axisLine={false}
                          tickLine={false}
                          tick={{ fontSize: 10, fill: '#D7C9AE' }}
                        />
                        <Tooltip
                          contentStyle={{
                            backgroundColor: '#141A1C',
                            borderRadius: '12px',
                            border: '1px solid #2B3437',
                            color: '#E9ECE6',
                          }}
                          itemStyle={{ fontSize: '12px' }}
                        />
                        <Line
                          yAxisId="left"
                          type="monotone"
                          dataKey="leads"
                          stroke="#E9ECE6"
                          strokeWidth={3}
                          dot={{
                            r: 4,
                            fill: '#141A1C',
                            strokeWidth: 2,
                            stroke: '#E9ECE6'
                          }}
                          activeDot={{ r: 6, fill: '#D7C9AE' }}
                        />
                        <Line
                          yAxisId="right"
                          type="monotone"
                          dataKey="calls"
                          stroke="#10B981"
                          strokeWidth={3}
                          dot={{
                            r: 4,
                            fill: '#141A1C',
                            strokeWidth: 2,
                            stroke: '#10B981',
                          }}
                        />
                        <Line
                          yAxisId="right"
                          type="monotone"
                          dataKey="confidence"
                          stroke="#D7C9AE"
                          strokeWidth={2}
                          strokeDasharray="5 5"
                          dot={false}
                          activeDot={{ r: 4, fill: '#D7C9AE' }}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </TabsContent>
            </div>
          </ScrollArea>
        </Tabs>
      </div>

      {!standalone && (
        <DialogFooter className="p-6 border-t border-borders/50 bg-background/50 backdrop-blur-sm z-10 flex justify-between items-center sm:justify-between">
          <div className="text-xs text-muted-foreground font-mono">
            ID: {move.id} • Created:{' '}
            {new Date(move.createdAt).toLocaleDateString()}
          </div>
          <Button
            onClick={onClose}
            className="px-8 bg-ink text-white hover:bg-ink/90"
          >
            Close Detail View
          </Button>
        </DialogFooter>
      )}
    </div>
  );

  if (standalone) {
    return Content;
  }

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-5xl h-[90vh] p-0 overflow-hidden flex flex-col bg-canvas sm:rounded-2xl">
        {Content}
      </DialogContent>
    </Dialog>
  );
}
