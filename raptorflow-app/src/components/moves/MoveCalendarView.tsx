'use client';

import React, { useState } from 'react';
import { Move } from '@/lib/campaigns-types';
import { Calendar } from '@/components/ui/calendar';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
    X, Check, MessageSquare, Send, Sparkles, AlertCircle,
    Clock, Target, Linkedin, Twitter, FileText, Image,
    Video, Users
} from 'lucide-react';
import { toast } from 'sonner';

interface MoveCalendarViewProps {
    move: Move;
    onClose: () => void;
    onUpdateTask: (moveId: string, taskId: string, completed: boolean) => void;
}

interface RichTask {
    id: string;
    label: string;
    completed: boolean;
    type: 'create' | 'publish' | 'engage' | 'analyze';
    platform: 'linkedin' | 'twitter' | 'email' | 'blog';
    scheduledTime: string;
    assets?: { type: 'post' | 'image' | 'video' | 'carousel' | 'thread'; name: string }[];
    targetAudience: string;
    goal: string;
    why: string;
}

interface DayPlan {
    day: number;
    date: Date;
    theme: string;
    focus: string;
    tasks: RichTask[];
}

function generateRichDayPlans(move: Move): DayPlan[] {
    const startDate = move.startedAt ? new Date(move.startedAt) : new Date();

    const richPlans: DayPlan[] = [
        {
            day: 1, date: new Date(startDate.getTime()), theme: "The Setup", focus: "Hook your audience with a relatable pain point",
            tasks: [
                { id: 't1-1', label: 'Write "Pricing Confusion" pain point post', completed: true, type: 'create', platform: 'linkedin', scheduledTime: '8:30 AM EST', assets: [{ type: 'post', name: 'Pricing Pain Post' }, { type: 'image', name: 'Pricing Diagram' }], goal: 'Hook founders who struggle with pricing', targetAudience: 'B2B SaaS Founders', why: 'Pricing is the #1 searched problem' },
                { id: 't1-2', label: 'Schedule post for morning feed', completed: true, type: 'publish', platform: 'linkedin', scheduledTime: '8:30 AM EST', goal: 'Catch morning scrollers', targetAudience: 'B2B SaaS Founders', why: 'Engagement peaks 8-10 AM' },
                { id: 't1-3', label: 'Engage with 10 target accounts', completed: false, type: 'engage', platform: 'linkedin', scheduledTime: '11:00 AM EST', targetAudience: 'SaaS community founders', goal: 'Build visibility before posts', why: 'Pre-engagement warms algorithm' }
            ]
        },
        {
            day: 2, date: new Date(startDate.getTime() + 86400000), theme: "Double Down", focus: "Capitalize on Day 1 momentum",
            tasks: [
                { id: 't2-1', label: 'Reply to all Day 1 comments', completed: false, type: 'engage', platform: 'linkedin', scheduledTime: '9:00 AM EST', goal: 'Build rapport + algorithm boost', targetAudience: 'Day 1 engagers', why: 'Quick replies signal activity' },
                { id: 't2-2', label: 'Create "Hiring First Marketer" post', completed: false, type: 'create', platform: 'linkedin', scheduledTime: '10:00 AM EST', assets: [{ type: 'post', name: 'Hiring Struggle Post' }, { type: 'carousel', name: '5 Red Flags' }], goal: 'Relate to solo founder pain', targetAudience: 'Bootstrapped founders', why: 'Second most common struggle' },
                { id: 't2-3', label: 'DM 3 warm leads', completed: false, type: 'engage', platform: 'linkedin', scheduledTime: '2:00 PM EST', goal: 'Start private conversations', targetAudience: 'High-engagers', why: 'Warm DMs convert 8x better' }
            ]
        },
        {
            day: 3, date: new Date(startDate.getTime() + 2 * 86400000), theme: "Cross-Platform Push", focus: "Expand reach by repurposing to Twitter",
            tasks: [
                { id: 't3-1', label: 'Repurpose Day 1 post as Twitter thread', completed: false, type: 'create', platform: 'twitter', scheduledTime: '9:30 AM EST', assets: [{ type: 'thread', name: '7-Tweet Thread' }], goal: 'Test message on different audience', targetAudience: 'Twitter SaaS community', why: 'Validates message cross-platform' },
                { id: 't3-2', label: 'Create "Tool Fatigue" problem post', completed: false, type: 'create', platform: 'linkedin', scheduledTime: '11:00 AM EST', assets: [{ type: 'post', name: 'Tool Fatigue Post' }, { type: 'image', name: 'Stack Meme' }], goal: 'Position against complexity', targetAudience: 'Overwhelmed founders', why: 'Sets up your solution' },
                { id: 't3-3', label: 'Analyze Day 1-2 metrics', completed: false, type: 'analyze', platform: 'linkedin', scheduledTime: '4:00 PM EST', goal: 'Identify what resonates', targetAudience: 'Your data', why: 'Data shows what to double down' }
            ]
        },
        {
            day: 4, date: new Date(startDate.getTime() + 3 * 86400000), theme: "Social Proof", focus: "Build credibility with results",
            tasks: [
                { id: 't4-1', label: 'Share mini case study', completed: false, type: 'create', platform: 'linkedin', scheduledTime: '9:00 AM EST', assets: [{ type: 'post', name: 'Case Study' }, { type: 'image', name: 'Results Screenshot' }], goal: 'Build credibility through proof', targetAudience: 'Skeptical prospects', why: 'Proof converts skeptics' },
                { id: 't4-2', label: 'Batch reply to comments (2x/day)', completed: false, type: 'engage', platform: 'linkedin', scheduledTime: '10 AM + 4 PM', goal: 'Maintain momentum', targetAudience: 'All commenters', why: 'Keeps posts in feed' }
            ]
        },
        {
            day: 5, date: new Date(startDate.getTime() + 4 * 86400000), theme: "The Promise", focus: "Shift from pain to possibility",
            tasks: [
                { id: 't5-1', label: 'Create "What if..." possibility post', completed: false, type: 'create', platform: 'linkedin', scheduledTime: '9:00 AM EST', assets: [{ type: 'post', name: 'Vision Post' }], goal: 'Paint the better future', targetAudience: 'Engaged followers', why: 'Pain builds awareness, promise builds desire' },
                { id: 't5-2', label: 'Create teaser for Day 7 offer', completed: false, type: 'create', platform: 'linkedin', scheduledTime: '2:00 PM EST', assets: [{ type: 'post', name: 'Teaser Post' }], goal: 'Build anticipation', targetAudience: 'Warm audience', why: 'Anticipation increases conversion' }
            ]
        },
        {
            day: 6, date: new Date(startDate.getTime() + 5 * 86400000), theme: "Authority Day", focus: "Position as the expert",
            tasks: [
                { id: 't6-1', label: 'Share your framework/methodology', completed: false, type: 'create', platform: 'linkedin', scheduledTime: '9:00 AM EST', assets: [{ type: 'carousel', name: '5-Step Framework' }], goal: 'Position as thought leader', targetAudience: 'Solution-seekers', why: 'Frameworks create authority' },
                { id: 't6-2', label: 'Engage with 15 target accounts', completed: false, type: 'engage', platform: 'linkedin', scheduledTime: '11:00 AM EST', goal: 'Prime for tomorrow CTA', targetAudience: 'ICPs', why: 'Pre-CTA engagement warms' }
            ]
        },
        {
            day: 7, date: new Date(startDate.getTime() + 6 * 86400000), theme: "The Ask", focus: "Convert with clear call-to-action",
            tasks: [
                { id: 't7-1', label: 'Create final CTA post', completed: false, type: 'create', platform: 'linkedin', scheduledTime: '9:00 AM EST', assets: [{ type: 'post', name: 'CTA Post' }, { type: 'image', name: 'Offer Graphic' }], goal: 'Convert audience to leads', targetAudience: 'Warmed audience', why: 'Nurturing is done. Be direct.' },
                { id: 't7-2', label: 'DM all warm leads from week', completed: false, type: 'engage', platform: 'linkedin', scheduledTime: '11:00 AM EST', goal: 'Personal outreach', targetAudience: 'Most engaged', why: 'Personal touch converts' },
                { id: 't7-3', label: 'Sprint retrospective', completed: false, type: 'analyze', platform: 'linkedin', scheduledTime: '4:00 PM EST', goal: 'Document learnings', targetAudience: 'Future you', why: 'Every sprint teaches' }
            ]
        }
    ];
    return richPlans.slice(0, move.duration);
}

function PlatformIcon({ platform }: { platform?: string }) {
    switch (platform) {
        case 'linkedin': return <Linkedin className="w-4 h-4" />;
        case 'twitter': return <Twitter className="w-4 h-4" />;
        default: return <FileText className="w-4 h-4" />;
    }
}

function AssetIcon({ type }: { type: string }) {
    switch (type) {
        case 'image': case 'carousel': return <Image className="w-3.5 h-3.5" />;
        case 'video': return <Video className="w-3.5 h-3.5" />;
        default: return <FileText className="w-3.5 h-3.5" />;
    }
}

function getTaskTypeBadge(type: string) {
    switch (type) {
        case 'create': return 'bg-[#2D3538] text-white';
        case 'publish': return 'bg-[#22C55E]/10 text-[#22C55E] border border-[#22C55E]/30';
        case 'engage': return 'bg-[#3B82F6]/10 text-[#3B82F6] border border-[#3B82F6]/30';
        case 'analyze': return 'bg-[#F59E0B]/10 text-[#F59E0B] border border-[#F59E0B]/30';
        default: return 'bg-[#E5E6E3] text-[#5B5F61]';
    }
}

export function MoveCalendarView({ move, onClose, onUpdateTask }: MoveCalendarViewProps) {
    const [selectedDay, setSelectedDay] = useState(1);
    const [chatMessage, setChatMessage] = useState('');
    const [isProcessing, setIsProcessing] = useState(false);
    const [activeTab, setActiveTab] = useState('tasks');

    const dayPlans = generateRichDayPlans(move);
    const startDate = move.startedAt ? new Date(move.startedAt) : new Date();
    const currentDayPlan = dayPlans.find(p => p.day === selectedDay) || dayPlans[0];
    const today = new Date();
    const currentDayNumber = Math.floor((today.getTime() - startDate.getTime()) / 86400000) + 1;

    const handleSendMessage = async () => {
        if (!chatMessage.trim()) return;
        setIsProcessing(true);
        await new Promise(r => setTimeout(r, 1500));
        toast.success('Plan updated');
        setChatMessage('');
        setIsProcessing(false);
    };

    const handleToggleTask = (taskId: string) => {
        const task = currentDayPlan?.tasks.find(t => t.id === taskId);
        if (task) onUpdateTask(move.id, taskId, !task.completed);
    };

    const allTasks = dayPlans.flatMap(d => d.tasks);
    const completedTasks = allTasks.filter(t => t.completed).length;
    const totalTasks = allTasks.length;
    const progressPercent = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;
    const dayCompletedTasks = currentDayPlan?.tasks.filter(t => t.completed).length || 0;
    const dayTotalTasks = currentDayPlan?.tasks.length || 0;

    return (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
            <div className="bg-[#F8F9F7] rounded-2xl w-full max-w-5xl h-[85vh] flex flex-col">

                {/* HEADER: Move name + progress + close */}
                <div className="flex items-center justify-between px-5 py-3 border-b border-[#E5E6E3]">
                    <div className="flex items-center gap-4">
                        <h2 className="font-serif text-[22px] text-[#2D3538]">{move.name}</h2>
                        <Badge variant="outline" className="text-[10px]">{move.duration} days</Badge>
                    </div>
                    <div className="flex items-center gap-4">
                        <span className="text-[13px] font-mono text-[#2D3538]">{progressPercent}%</span>
                        <Progress value={progressPercent} className="w-20 h-1.5" />
                        <button onClick={onClose} className="w-8 h-8 rounded-lg hover:bg-white flex items-center justify-center">
                            <X className="w-5 h-5 text-[#5B5F61]" />
                        </button>
                    </div>
                </div>

                {/* TOP SECTION: Day pills LEFT | Day info CENTER | Calendar RIGHT */}
                <div className="flex items-start gap-6 px-5 py-4 border-b border-[#E5E6E3] bg-white">
                    {/* Day Pills - LEFT */}
                    <div className="flex items-center gap-1.5">
                        {dayPlans.map((plan) => {
                            const isToday = plan.day === currentDayNumber;
                            const dayDone = plan.tasks.filter(t => t.completed).length;
                            const dayTotal = plan.tasks.length;
                            const dayComplete = dayDone === dayTotal && dayTotal > 0;

                            return (
                                <button
                                    key={plan.day}
                                    onClick={() => setSelectedDay(plan.day)}
                                    className={`
                                        flex flex-col items-center px-3 py-1.5 rounded-lg transition-all
                                        ${selectedDay === plan.day
                                            ? 'bg-[#2D3538] text-white'
                                            : dayComplete
                                                ? 'bg-[#F0FDF4] text-[#22C55E] border border-[#22C55E]/30'
                                                : isToday
                                                    ? 'border-2 border-[#2D3538] text-[#2D3538]'
                                                    : 'bg-[#F8F9F7] border border-[#E5E6E3] text-[#5B5F61] hover:border-[#C0C1BE]'
                                        }
                                    `}
                                >
                                    <span className="text-[10px] uppercase opacity-70">Day</span>
                                    <span className="text-[16px] font-semibold leading-none">{plan.day}</span>
                                </button>
                            );
                        })}
                    </div>

                    {/* Day Info - CENTER */}
                    <div className="flex-1">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-xl bg-[#2D3538] text-white flex items-center justify-center text-[15px] font-semibold">
                                {selectedDay}
                            </div>
                            <div>
                                <h3 className="text-[17px] font-medium text-[#2D3538]">{currentDayPlan?.theme}</h3>
                                <p className="text-[12px] text-[#9D9F9F]">
                                    {currentDayPlan?.date.toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' })}
                                </p>
                            </div>
                        </div>
                        <p className="text-[13px] text-[#5B5F61] mt-2">{currentDayPlan?.focus}</p>
                        <div className="flex items-center gap-2 mt-2">
                            <span className="text-[11px] text-[#9D9F9F]">{dayCompletedTasks}/{dayTotalTasks} complete</span>
                            <Progress value={dayTotalTasks > 0 ? (dayCompletedTasks / dayTotalTasks) * 100 : 0} className="w-20 h-1.5" />
                        </div>
                    </div>

                    {/* Calendar - RIGHT */}
                    <div className="shrink-0">
                        <Calendar
                            mode="single"
                            selected={currentDayPlan?.date}
                            onSelect={(date) => {
                                if (date) {
                                    const dayDiff = Math.floor((date.getTime() - startDate.getTime()) / 86400000) + 1;
                                    if (dayDiff >= 1 && dayDiff <= move.duration) setSelectedDay(dayDiff);
                                }
                            }}
                            className="rounded-lg border border-[#E5E6E3] p-2"
                            disabled={(date) => {
                                const dayDiff = Math.floor((date.getTime() - startDate.getTime()) / 86400000) + 1;
                                return dayDiff < 1 || dayDiff > move.duration;
                            }}
                        />
                    </div>
                </div>

                {/* BOTTOM 60%: Tasks & Assets */}
                <div className="flex-1 flex flex-col min-h-0">
                    <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col min-h-0">
                        <div className="px-5 border-b border-[#E5E6E3] bg-white shrink-0">
                            <TabsList className="bg-transparent h-10 p-0 gap-6">
                                <TabsTrigger value="tasks" className="data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:border-b-2 data-[state=active]:border-[#2D3538] rounded-none h-10 px-0 text-[13px]">
                                    Tasks ({dayTotalTasks})
                                </TabsTrigger>
                                <TabsTrigger value="assets" className="data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:border-b-2 data-[state=active]:border-[#2D3538] rounded-none h-10 px-0 text-[13px]">
                                    Assets ({currentDayPlan?.tasks.reduce((acc, t) => acc + (t.assets?.length || 0), 0) || 0})
                                </TabsTrigger>
                            </TabsList>
                        </div>

                        {/* SCROLLABLE Tasks */}
                        <TabsContent value="tasks" className="flex-1 overflow-y-auto p-4 mt-0">
                            <div className="space-y-3">
                                {currentDayPlan?.tasks.map((task) => (
                                    <div key={task.id} className={`rounded-xl ${task.completed ? 'bg-[#F0FDF4] border border-[#22C55E]/20' : 'bg-white border border-[#E5E6E3]'}`}>
                                        <div className="p-4">
                                            <div className="flex items-start gap-3">
                                                <button
                                                    onClick={() => handleToggleTask(task.id)}
                                                    className={`w-5 h-5 rounded-full border-2 flex items-center justify-center transition-all shrink-0 mt-0.5 ${task.completed ? 'bg-[#22C55E] border-[#22C55E] text-white' : 'border-[#C0C1BE] hover:border-[#2D3538]'}`}
                                                >
                                                    {task.completed && <Check className="w-3 h-3" />}
                                                </button>

                                                <div className="flex-1 min-w-0">
                                                    <span className={`text-[14px] font-medium ${task.completed ? 'text-[#5B5F61] line-through' : 'text-[#2D3538]'}`}>
                                                        {task.label}
                                                    </span>

                                                    <div className="flex items-center gap-3 mt-2 flex-wrap">
                                                        <Badge className={`text-[10px] h-5 ${getTaskTypeBadge(task.type)}`}>{task.type}</Badge>
                                                        <div className="flex items-center gap-1 text-[11px] text-[#5B5F61]">
                                                            <PlatformIcon platform={task.platform} />
                                                            <span className="capitalize">{task.platform}</span>
                                                        </div>
                                                        <div className="flex items-center gap-1 text-[11px] text-[#2D3538] font-medium">
                                                            <Clock className="w-3.5 h-3.5" />
                                                            <span>{task.scheduledTime}</span>
                                                        </div>
                                                        <div className="flex items-center gap-1 text-[11px] text-[#5B5F61]">
                                                            <Users className="w-3.5 h-3.5" />
                                                            <span>{task.targetAudience}</span>
                                                        </div>
                                                    </div>

                                                    <div className="mt-2 space-y-1">
                                                        <div className="flex items-start gap-1.5">
                                                            <Target className="w-3 h-3 text-[#9D9F9F] mt-0.5 shrink-0" />
                                                            <span className="text-[12px] text-[#5B5F61]">{task.goal}</span>
                                                        </div>
                                                        <p className="text-[12px] text-[#9D9F9F] italic pl-4">💡 {task.why}</p>
                                                    </div>

                                                    {task.assets && task.assets.length > 0 && (
                                                        <div className="flex items-center gap-2 mt-2 flex-wrap">
                                                            {task.assets.map((asset, i) => (
                                                                <div key={i} className="flex items-center gap-1 px-2 py-0.5 bg-[#F8F9F7] rounded text-[10px] text-[#5B5F61] border border-[#E5E6E3]">
                                                                    <AssetIcon type={asset.type} />
                                                                    {asset.name}
                                                                </div>
                                                            ))}
                                                        </div>
                                                    )}
                                                </div>

                                                {task.type === 'create' && !task.completed && (
                                                    <a href="/muse" className="inline-flex items-center gap-1 px-3 py-1.5 bg-[#2D3538] text-white rounded-lg text-[11px] font-medium hover:bg-black shrink-0">
                                                        <Sparkles className="w-3 h-3" />
                                                        Create
                                                    </a>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                ))}

                                {(!currentDayPlan?.tasks || currentDayPlan.tasks.length === 0) && (
                                    <div className="text-center py-12">
                                        <AlertCircle className="w-8 h-8 mx-auto text-[#E5E6E3] mb-2" />
                                        <p className="text-[13px] text-[#9D9F9F]">No tasks for this day</p>
                                    </div>
                                )}
                            </div>
                        </TabsContent>

                        {/* SCROLLABLE Assets */}
                        <TabsContent value="assets" className="flex-1 overflow-y-auto p-4 mt-0">
                            <div className="grid grid-cols-3 gap-3">
                                {currentDayPlan?.tasks.flatMap(task =>
                                    task.assets?.map((asset, i) => (
                                        <div key={`${task.id}-${i}`} className="p-3 bg-white border border-[#E5E6E3] rounded-xl hover:border-[#C0C1BE]">
                                            <div className="flex items-center gap-2 mb-2">
                                                <div className="w-8 h-8 rounded-lg bg-[#F8F9F7] flex items-center justify-center">
                                                    <AssetIcon type={asset.type} />
                                                </div>
                                                <div>
                                                    <p className="text-[13px] font-medium text-[#2D3538]">{asset.name}</p>
                                                    <p className="text-[10px] text-[#9D9F9F] capitalize">{asset.type}</p>
                                                </div>
                                            </div>
                                            <a href="/muse" className="w-full inline-flex items-center justify-center gap-1 px-2 py-1.5 bg-[#2D3538] text-white rounded-lg text-[11px] font-medium hover:bg-black">
                                                <Sparkles className="w-3 h-3" />
                                                Create in Muse
                                            </a>
                                        </div>
                                    )) || []
                                )}
                                {currentDayPlan?.tasks.reduce((acc, t) => acc + (t.assets?.length || 0), 0) === 0 && (
                                    <div className="col-span-3 text-center py-12">
                                        <Image className="w-8 h-8 mx-auto text-[#E5E6E3] mb-2" />
                                        <p className="text-[13px] text-[#9D9F9F]">No assets to create today</p>
                                    </div>
                                )}
                            </div>
                        </TabsContent>
                    </Tabs>

                    {/* Chat Input - FIXED at bottom */}
                    <div className="shrink-0 p-3 border-t border-[#E5E6E3] bg-white">
                        <div className="flex items-center gap-3">
                            <MessageSquare className="w-4 h-4 text-[#9D9F9F]" />
                            <input
                                type="text"
                                value={chatMessage}
                                onChange={(e) => setChatMessage(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
                                placeholder="Modify today's plan... e.g. 'Skip carousel, move DMs to tomorrow'"
                                className="flex-1 text-[13px] text-[#2D3538] placeholder:text-[#9D9F9F] bg-transparent focus:outline-none"
                                disabled={isProcessing}
                            />
                            <button
                                onClick={handleSendMessage}
                                disabled={!chatMessage.trim() || isProcessing}
                                className="w-8 h-8 rounded-lg bg-[#2D3538] text-white flex items-center justify-center hover:bg-black disabled:opacity-50"
                            >
                                {isProcessing ? <div className="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : <Send className="w-3.5 h-3.5" />}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
