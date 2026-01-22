"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Bot, User, StopCircle, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";
import { BlueprintButton } from "@/components/ui/BlueprintButton";
import { useBCMStore } from "@/stores/bcmStore";

interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: number;
    tokens_used?: number;
    cost_usd?: number;
    suggestions?: string[];
}

interface MuseChatProps {
    initialContext?: {
        topic: string;
        prompt: string;
        platform?: string;
    } | null;
}

export default function MuseChat({ initialContext }: MuseChatProps) {
    const { bcm } = useBCMStore();
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [apiStatus, setApiStatus] = useState<'loading' | 'connected' | 'error'>('loading');
    const [hasAutoSent, setHasAutoSent] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLInputElement>(null);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    useEffect(() => {
        checkApiStatus();
    }, []);

    // Auto-send initial message when context is provided
    useEffect(() => {
        if (initialContext?.prompt && apiStatus === 'connected' && !hasAutoSent && messages.length === 0) {
            setHasAutoSent(true);
            sendMessage(initialContext.prompt);
        }
    }, [initialContext, apiStatus, hasAutoSent, messages.length]);

    const checkApiStatus = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/v1/muse/status');
            const data = await response.json();

            if (data.status === 'available') {
                setApiStatus('connected');
                console.log('Γ£à Muse API connected:', data.model);
            } else {
                setApiStatus('error');
            }
        } catch (error) {
            setApiStatus('error');
            console.error('Γ¥î API connection failed:', error);
        }
    };

    const sendMessage = async (messageText: string) => {
        if (!messageText.trim() || isLoading) return;

        const userMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: messageText,
            timestamp: Date.now()
        };

        setMessages(prev => [...prev, userMessage]);
        setIsLoading(true);
        setInput("");

        try {
            // Build BCM context for enhanced responses
            const bcmContext = bcm ? {
                company: bcm.foundation.company,
                mission: bcm.foundation.mission,
                value_prop: bcm.foundation.value_prop,
                brand_voice: bcm.messaging.brand_voice.tone.join(', '),
                one_liner: bcm.messaging.one_liner,
                icps: bcm.icps.map(icp => icp.name),
                competitors: bcm.competitive.competitors
            } : null;

            // Call REAL Muse API with BCM context
            const response = await fetch('http://localhost:8000/api/v1/muse/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: messageText,
                    conversation_history: messages.map(msg => ({
                        role: msg.role,
                        content: msg.content,
                        timestamp: new Date(msg.timestamp).toISOString()
                    })),
                    context: { 
                        platform: "Raptorflow",
                        bcm: bcmContext
                    },
                    user_id: "test-user",
                    workspace_id: "test-workspace",
                    max_tokens: 800,
                    temperature: 0.7
                })
            });

            const data = await response.json();

            if (data.success) {
                const responseText = data.content || data.message || '';
                const assistantMessage: Message = {
                    id: Date.now().toString(),
                    role: 'assistant',
                    content: responseText || 'No response returned.',
                    timestamp: Date.now(),
                    tokens_used: data.tokens_used,
                    cost_usd: data.cost_usd,
                    suggestions: data.suggestions || []
                };

                setMessages(prev => [...prev, assistantMessage]);
            } else {
                setMessages(prev => [...prev, {
                    id: Date.now().toString(),
                    role: 'assistant',
                    content: `Error: ${data.error || 'Unknown error'}`,
                    timestamp: Date.now()
                }]);
            }
        } catch (error) {
            console.error('Error:', error);
            setMessages(prev => [...prev, {
                id: Date.now().toString(),
                role: 'assistant',
                content: 'Network error. Please try again.',
                timestamp: Date.now()
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    const generateContent = async (task: string, contentType: string) => {
        setIsLoading(true);

        try {
            // Build BCM context for enhanced content generation
            const bcmContext = bcm ? {
                company: bcm.foundation.company,
                mission: bcm.foundation.mission,
                value_prop: bcm.foundation.value_prop,
                brand_voice: bcm.messaging.brand_voice.tone.join(', '),
                one_liner: bcm.messaging.one_liner,
                icps: bcm.icps.map(icp => icp.name),
                value_props: bcm.messaging.value_props,
                do_list: bcm.messaging.brand_voice.do_list,
                dont_list: bcm.messaging.brand_voice.dont_list
            } : null;

            const response = await fetch('http://localhost:8000/api/v1/muse/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    task: task,
                    context: { 
                        platform: "Raptorflow",
                        bcm: bcmContext
                    },
                    user_id: "test-user",
                    workspace_id: "test-workspace",
                    content_type: contentType,
                    tone: bcm?.messaging.brand_voice.tone.join(', ') || 'professional',
                    target_audience: bcm?.icps[0]?.name || 'marketing professionals',
                    max_tokens: 1000,
                    temperature: 0.7
                })
            });

            const data = await response.json();

            if (data.success) {
                const responseText = data.content || data.message || '';
                setMessages(prev => [...prev, {
                    id: Date.now().toString(),
                    role: 'assistant',
                    content: `**Generated ${contentType}:**\n\n${responseText || 'No response returned.'}`,
                    timestamp: Date.now(),
                    tokens_used: data.tokens_used,
                    cost_usd: data.cost_usd,
                    suggestions: data.suggestions || []
                }]);
            } else {
                setMessages(prev => [...prev, {
                    id: Date.now().toString(),
                    role: 'assistant',
                    content: `Error: ${data.error || 'Unknown error'}`,
                    timestamp: Date.now()
                }]);
            }
        } catch (error) {
            console.error('Error:', error);
            setMessages(prev => [...prev, {
                id: Date.now().toString(),
                role: 'assistant',
                content: 'Network error. Please try again.',
                timestamp: Date.now()
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleSubmit = (e?: React.FormEvent) => {
        e?.preventDefault();
        if (!input.trim()) return;
        sendMessage(input);
    };

    const handleSuggestionClick = (suggestion: string) => {
        setInput(suggestion);
        inputRef.current?.focus();
    };

    return (
        <div className="h-full flex flex-col bg-[var(--background)]">
            {/* Header */}
            <div className="p-6 border-b border-[var(--border)] bg-[var(--surface)]">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <div className="relative">
                            <div className="w-12 h-12 bg-[var(--blueprint)] rounded-full flex items-center justify-center">
                                <Bot className="w-6 h-6 text-[var(--paper)]" />
                            </div>
                            <div className="absolute -bottom-1 -right-1 w-3 h-3 bg-[var(--success)] rounded-full border-2 border-[var(--surface)]"></div>
                        </div>
                        <div>
                            <h1 className="text-2xl font-bold text-[var(--ink)]">Muse</h1>
                            <p className="text-sm text-[var(--muted)] font-technical uppercase tracking-wider">
                                AI Content Assistant
                            </p>
                            <div className="flex items-center gap-2 mt-1">
                                <div className={cn(
                                    "w-2 h-2 rounded-full",
                                    apiStatus === 'connected' ? "bg-[var(--success)]" :
                                        apiStatus === 'error' ? "bg-[var(--error)]" : "bg-[var(--warning)]"
                                )}></div>
                                <span className={cn(
                                    "text-xs font-technical",
                                    apiStatus === 'connected' ? "text-[var(--success)]" :
                                        apiStatus === 'error' ? "text-[var(--error)]" : "text-[var(--warning)]"
                                )}>
                                    {apiStatus === 'connected' ? 'Connected to Gemini 2.0 Flash' :
                                        apiStatus === 'error' ? 'API Connection Error' : 'Connecting...'}
                                </span>
                            </div>
                        </div>
                    </div>

                    {/* Quick Actions */}
                    <div className="flex gap-3">
                        <BlueprintButton
                            size="sm"
                            onClick={() => generateContent("Create a blog post about marketing automation", "blog")}
                            disabled={isLoading || apiStatus !== 'connected'}
                            className="flex items-center gap-2"
                        >
                            <Sparkles className="w-4 h-4" />
                            Blog
                        </BlueprintButton>
                        <BlueprintButton
                            size="sm"
                            onClick={() => generateContent("Write a professional email campaign", "email")}
                            disabled={isLoading || apiStatus !== 'connected'}
                            className="flex items-center gap-2"
                        >
                            <Sparkles className="w-4 h-4" />
                            Email
                        </BlueprintButton>
                    </div>
                </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6">
                <div className="max-w-4xl mx-auto space-y-6">
                    {messages.length === 0 && (
                        <div className="text-center py-16">
                            <div className="relative inline-block">
                                <div className="w-16 h-16 bg-[var(--blueprint)] rounded-full flex items-center justify-center mb-6">
                                    <Bot className="w-8 h-8 text-[var(--paper)]" />
                                </div>
                                <div className="absolute -top-2 -right-2 w-4 h-4 bg-[var(--blueprint)] rounded-full flex items-center justify-center">
                                    <Sparkles className="w-2 h-2 text-[var(--paper)]" />
                                </div>
                            </div>
                            <h2 className="text-2xl font-bold text-[var(--ink)] mb-4">
                                Welcome to Muse
                            </h2>
                            <p className="text-[var(--muted)] mb-8 max-w-md">
                                I'm your AI content creation assistant powered by Gemini 2.0 Flash.
                                I can help you create marketing content, provide strategic insights, and offer creative solutions.
                            </p>

                            <div className="space-y-3">
                                <p className="text-sm font-technical text-[var(--muted)]">Try asking me:</p>
                                <div className="flex flex-wrap gap-2 justify-center">
                                    <button
                                        onClick={() => handleSuggestionClick("How can I improve my email marketing campaigns?")}
                                        className="px-4 py-2 bg-[var(--paper)] border border-[var(--ink)] rounded-[var(--radius)] text-sm text-[var(--ink)] hover:bg-[var(--muted)] transition-colors"
                                    >
                                        ≡ƒÆ¼ Email Marketing
                                    </button>
                                    <button
                                        onClick={() => handleSuggestionClick("Create a social media content calendar")}
                                        className="px-4 py-2 bg-[var(--paper)] border border-[var(--ink)] rounded-[var(--radius)] text-sm text-[var(--ink)] hover:bg-[var(--muted)] transition-colors"
                                    >
                                        ≡ƒôà Content Calendar
                                    </button>
                                    <button
                                        onClick={() => handleSuggestionClick("What are the best practices for landing page optimization?")}
                                        className="px-4 py-2 bg-[var(--paper)] border border-[var(--ink)] rounded-[var(--radius)] text-sm text-[var(--ink)] hover:bg-[var(--muted)] transition-colors"
                                    >
                                        ≡ƒÄ» Landing Pages
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}

                    {messages.map((message) => (
                        <div
                            key={message.id}
                            className={cn(
                                "flex gap-4",
                                message.role === 'user' ? 'justify-end' : 'justify-start'
                            )}
                        >
                            {message.role === 'assistant' && (
                                <div className="flex-shrink-0">
                                    <div className="w-8 h-8 bg-[var(--blueprint)] rounded-full flex items-center justify-center">
                                        <Bot className="w-4 h-4 text-[var(--paper)]" />
                                    </div>
                                </div>
                            )}

                            <div
                                className={cn(
                                    "max-w-[85%] p-4 rounded-[var(--radius-lg)] border border-[var(--border)]",
                                    message.role === 'user'
                                        ? 'bg-[var(--ink)] text-[var(--paper)]'
                                        : 'bg-[var(--surface)] text-[var(--ink)]'
                                )}
                            >
                                {message.role === 'assistant' && (
                                    <div className="flex items-center gap-2 mb-3">
                                        <div className="w-6 h-6 bg-[var(--blueprint)] rounded-full flex items-center justify-center">
                                            <Bot className="w-3 h-3 text-[var(--paper)]" />
                                        </div>
                                        <span className="text-xs font-technical text-[var(--muted)] uppercase tracking-wider">
                                            Muse AI
                                        </span>
                                    </div>
                                )}
                                <div className="whitespace-pre-wrap text-sm leading-relaxed">
                                    {message.content}
                                </div>

                                {/* Metadata */}
                                {(message.tokens_used || message.cost_usd) && (
                                    <div className="mt-3 pt-3 border-t border-[var(--border)]">
                                        <div className="flex items-center gap-4 text-xs text-[var(--muted)]">
                                            {message.tokens_used && (
                                                <>
                                                    <span>Tokens: {message.tokens_used}</span>
                                                    <span className="text-[var(--ink)]">ΓÇó</span>
                                                </>
                                            )}
                                            {message.cost_usd && (
                                                <span>Cost: ${message.cost_usd.toFixed(6)}</span>
                                            )}
                                        </div>
                                    </div>
                                )}

                                {/* Suggestions */}
                                {message.suggestions && message.suggestions.length > 0 && (
                                    <div className="mt-3 space-y-2">
                                        <p className="text-xs font-technical text-[var(--muted)]">Suggestions:</p>
                                        {message.suggestions.map((suggestion, index) => (
                                            <button
                                                key={index}
                                                onClick={() => handleSuggestionClick(suggestion)}
                                                className="block w-full text-left px-3 py-2 bg-[var(--muted)] border border-[var(--border)] rounded-[var(--radius)] text-xs text-[var(--ink)] hover:bg-[var(--surface)] hover:border-[var(--ink)] transition-colors"
                                            >
                                                ≡ƒÆí {suggestion}
                                            </button>
                                        ))}
                                    </div>
                                )}

                                {/* Timestamp */}
                                <div className={cn(
                                    "mt-3 text-xs text-[var(--muted)]",
                                    message.role === 'user' ? "text-right" : "text-left"
                                )}>
                                    {new Date(message.timestamp).toLocaleTimeString([], {
                                        hour: '2-digit',
                                        minute: '2-digit'
                                    })}
                                </div>
                            </div>

                            {message.role === 'user' && (
                                <div className="flex-shrink-0">
                                    <div className="w-8 h-8 bg-[var(--ink)] rounded-full flex items-center justify-center">
                                        <User className="w-4 h-4 text-[var(--paper)]" />
                                    </div>
                                </div>
                            )}
                        </div>
                    ))}

                    {/* Loading Indicator */}
                    {isLoading && (
                        <div className="flex justify-start">
                            <div className="flex-shrink-0">
                                <div className="w-8 h-8 bg-[var(--blueprint)] rounded-full flex items-center justify-center">
                                    <Bot className="w-4 h-4 text-[var(--paper)]" />
                                </div>
                            </div>
                            <div className="p-4 rounded-[var(--radius-lg)] border border-[var(--border)] bg-[var(--surface)]">
                                <div className="flex items-center gap-2 mb-3">
                                    <div className="w-6 h-6 bg-[var(--blueprint)] rounded-full flex items-center justify-center">
                                        <Bot className="w-3 h-3 text-[var(--paper)]" />
                                    </div>
                                    <span className="text-xs font-technical text-[var(--muted)] uppercase tracking-wider">
                                        Muse AI
                                    </span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <div className="w-2 h-2 bg-[var(--muted)] rounded-full animate-pulse"></div>
                                    <div className="w-2 h-2 bg-[var(--muted)] rounded-full animate-pulse delay-75"></div>
                                    <div className="w-2 h-2 bg-[var(--muted)] rounded-full animate-pulse delay-150"></div>
                                </div>
                            </div>
                        </div>
                    )}

                    <div ref={messagesEndRef} />
                </div>
            </div>

            {/* Input */}
            <div className="p-6 border-t border-[var(--border)] bg-[var(--surface)]">
                <div className="max-w-4xl mx-auto">
                    {/* Prompt Suggestions */}
                    <div className="flex flex-wrap gap-2 mb-4 justify-center">
                        <button
                            onClick={() => handleSuggestionClick("Write an email about")}
                            className="px-3 py-1.5 bg-[var(--paper)] border border-[var(--ink)] rounded-[var(--radius)] text-xs text-[var(--muted)] hover:border-[var(--blueprint)] hover:text-[var(--blueprint)] transition-colors"
                        >
                            ≡ƒôº Email
                        </button>
                        <button
                            onClick={() => handleSuggestionClick("Create a LinkedIn post")}
                            className="px-3 py-1.5 bg-[var(--paper)] border border-[var(--ink)] rounded-[var(--radius)] text-xs text-[var(--muted)] hover:border-[var(--blueprint)] hover:text-[var(--blueprint)] transition-colors"
                        >
                            ≡ƒÆ╝ LinkedIn
                        </button>
                        <button
                            onClick={() => handleSuggestionClick("Generate a blog outline")}
                            className="px-3 py-1.5 bg-[var(--paper)] border border-[var(--ink)] rounded-[var(--radius)] text-xs text-[var(--muted)] hover:border-[var(--blueprint)] hover:text-[var(--blueprint)] transition-colors"
                        >
                            ≡ƒô¥ Blog
                        </button>
                        <button
                            onClick={() => handleSuggestionClick("Create marketing campaign")}
                            className="px-3 py-1.5 bg-[var(--paper)] border border-[var(--ink)] rounded-[var(--radius)] text-xs text-[var(--muted)] hover:border-[var(--blueprint)] hover:text-[var(--blueprint)] transition-colors"
                        >
                            ≡ƒôó Campaign
                        </button>
                    </div>

                    {/* Input Form */}
                    <form onSubmit={handleSubmit} className="relative">
                        <div className="relative">
                            <input
                                ref={inputRef}
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                placeholder="Ask Muse anything about marketing..."
                                className={cn(
                                    "w-full px-4 py-3 pr-12 bg-[var(--paper)] border border-[var(--ink)] rounded-[var(--radius)] text-[var(--ink)] placeholder:text-[var(--muted)] focus:outline-none focus:border-[var(--blueprint)] focus:ring-2 focus:ring-[var(--blueprint)]/20 transition-all text-sm",
                                    isLoading || apiStatus !== 'connected' ? "opacity-50 cursor-not-allowed" : ""
                                )}
                                disabled={isLoading || apiStatus !== 'connected'}
                            />
                            <button
                                type="submit"
                                className={cn(
                                    "absolute right-2 top-1/2 -translate-y-1/2 w-8 h-8 rounded-[var(--radius)] flex items-center justify-center transition-all",
                                    input.trim() && !isLoading && apiStatus === 'connected'
                                        ? "bg-[var(--blueprint)] text-[var(--paper)] hover:bg-[var(--blueprint)]/90"
                                        : "bg-[var(--muted)] text-[var(--ink)]"
                                )}
                                disabled={!input.trim() || isLoading || apiStatus !== 'connected'}
                            >
                                {isLoading ? (
                                    <StopCircle className="w-4 h-4" />
                                ) : (
                                    <Send className="w-4 h-4" />
                                )}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
}
