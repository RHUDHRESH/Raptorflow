"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Bot, User, StopCircle, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";
import { BlueprintButton } from "@/components/ui/BlueprintButton";
import { useAuth } from "@/components/auth/AuthProvider";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

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
    const { user, profile, session } = useAuth();
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [apiStatus, setApiStatus] = useState<'loading' | 'connected' | 'error'>('connected'); // Default to connected
    const [hasAutoSent, setHasAutoSent] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLInputElement>(null);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    // Skip status check as endpoint doesn't exist
    // useEffect(() => {
    //     checkApiStatus();
    // }, []);

    // Auto-send initial message when context is provided
    useEffect(() => {
        if (initialContext?.prompt && !hasAutoSent && messages.length === 0) {
            setHasAutoSent(true);
            sendMessage(initialContext.prompt);
        }
    }, [initialContext, hasAutoSent, messages.length]);

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
            // Call REAL Muse API with auth context
            // Redirecting chat to generate endpoint as /chat doesn't exist
            const authHeader = session?.access_token
                ? { Authorization: `Bearer ${session.access_token}` }
                : {};
            const workspaceHeader = profile?.workspace_id
                ? { "x-workspace-id": profile.workspace_id }
                : {};
            const response = await fetch(`${API_BASE_URL}/api/v1/muse/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', ...authHeader, ...workspaceHeader },
                body: JSON.stringify({
                    topic: messageText, // Treat message as topic/task
                    task: messageText,
                    content_type: "general", // generic type
                    context: { platform: "Raptorflow" },
                    user_id: user?.id || "anonymous",
                    workspace_id: profile?.workspace_id || "default",
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
            const authHeader = session?.access_token
                ? { Authorization: `Bearer ${session.access_token}` }
                : {};
            const workspaceHeader = profile?.workspace_id
                ? { "x-workspace-id": profile.workspace_id }
                : {};
            const response = await fetch(`${API_BASE_URL}/api/v1/muse/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', ...authHeader, ...workspaceHeader },
                body: JSON.stringify({
                    topic: task,
                    task: task, // Some backends might use task
                    context: { platform: "Raptorflow" },
                    user_id: user?.id || "anonymous",
                    workspace_id: profile?.workspace_id || "default",
                    content_type: contentType,
                    tone: 'professional',
                    target_audience: 'marketing professionals',
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
                                        💬 Email Marketing
                                    </button>
                                    <button
                                        onClick={() => handleSuggestionClick("Create a social media content calendar")}
                                        className="px-4 py-2 bg-[var(--paper)] border border-[var(--ink)] rounded-[var(--radius)] text-sm text-[var(--ink)] hover:bg-[var(--muted)] transition-colors"
                                    >
                                        📅 Content Calendar
                                    </button>
                                    <button
                                        onClick={() => handleSuggestionClick("What are the best practices for landing page optimization?")}
                                        className="px-4 py-2 bg-[var(--paper)] border border-[var(--ink)] rounded-[var(--radius)] text-sm text-[var(--ink)] hover:bg-[var(--muted)] transition-colors"
                                    >
                                        🎯 Landing Pages
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
                                                    <span className="text-[var(--ink)]">•</span>
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
                                                💡 {suggestion}
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
                            📧 Email
                        </button>
                        <button
                            onClick={() => handleSuggestionClick("Create a LinkedIn post")}
                            className="px-3 py-1.5 bg-[var(--paper)] border border-[var(--ink)] rounded-[var(--radius)] text-xs text-[var(--muted)] hover:border-[var(--blueprint)] hover:text-[var(--blueprint)] transition-colors"
                        >
                            💼 LinkedIn
                        </button>
                        <button
                            onClick={() => handleSuggestionClick("Generate a blog outline")}
                            className="px-3 py-1.5 bg-[var(--paper)] border border-[var(--ink)] rounded-[var(--radius)] text-xs text-[var(--muted)] hover:border-[var(--blueprint)] hover:text-[var(--blueprint)] transition-colors"
                        >
                            📝 Blog
                        </button>
                        <button
                            onClick={() => handleSuggestionClick("Create marketing campaign")}
                            className="px-3 py-1.5 bg-[var(--paper)] border border-[var(--ink)] rounded-[var(--radius)] text-xs text-[var(--muted)] hover:border-[var(--blueprint)] hover:text-[var(--blueprint)] transition-colors"
                        >
                            📢 Campaign
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
