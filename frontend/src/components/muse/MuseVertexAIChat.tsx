"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Bot, User, StopCircle } from "lucide-react";

interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: number;
    tokens_used?: number;
    cost_usd?: number;
}

export default function MuseVertexAIChat() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [apiStatus, setApiStatus] = useState<'loading' | 'connected' | 'error'>('loading');
    const messagesEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    useEffect(() => {
        checkApiStatus();
    }, []);

    const checkApiStatus = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/v1/muse/status');
            const data = await response.json();

            if (data.status === 'available') {
                setApiStatus('connected');
                console.log('✅ REAL API connected:', data.model);
            } else {
                setApiStatus('error');
            }
        } catch (error) {
            setApiStatus('error');
            console.error('❌ API connection failed:', error);
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

        try {
            // Call REAL Muse Vertex AI API
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
                    context: { platform: "Raptorflow" },
                    user_id: "test-user",
                    workspace_id: "test-workspace",
                    max_tokens: 800,
                    temperature: 0.7
                })
            });

            const data = await response.json();

            if (data.success) {
                const assistantMessage: Message = {
                    id: Date.now().toString(),
                    role: 'assistant',
                    content: data.message,
                    timestamp: Date.now(),
                    tokens_used: data.tokens_used,
                    cost_usd: data.cost_usd
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
            const response = await fetch('http://localhost:8000/api/v1/muse/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    task: task,
                    context: { platform: "Raptorflow" },
                    user_id: "test-user",
                    workspace_id: "test-workspace",
                    content_type: contentType,
                    tone: 'professional',
                    target_audience: 'marketing professionals',
                    max_tokens: 1000,
                    temperature: 0.7
                })
            });

            const data = await response.json();

            if (data.success) {
                setMessages(prev => [...prev, {
                    id: Date.now().toString(),
                    role: 'assistant',
                    content: `**Generated ${contentType}:**\n\n${data.content}`,
                    timestamp: Date.now(),
                    tokens_used: data.tokens_used,
                    cost_usd: data.cost_usd
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
        setInput("");
    };

    return (
        <div className="flex flex-col h-full bg-white border border-gray-200">
            {/* Header */}
            <div className="p-4 border-b border-gray-200 bg-white">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                            <Bot className="w-4 h-4 text-white" />
                        </div>
                        <div>
                            <h3 className="text-sm font-semibold text-gray-900">Muse Vertex AI</h3>
                            <p className={`text-xs ${apiStatus === 'connected' ? 'text-green-600' : apiStatus === 'error' ? 'text-red-600' : 'text-yellow-600'}`}>
                                {apiStatus === 'connected' ? 'Connected to Gemini 2.0 Flash' : apiStatus === 'error' ? 'API Connection Error' : 'Connecting...'}
                            </p>
                        </div>
                    </div>

                    {/* Quick Actions */}
                    <div className="flex gap-2">
                        <button
                            onClick={() => generateContent("Create a blog post about marketing automation", "blog")}
                            disabled={isLoading || apiStatus !== 'connected'}
                            className="px-3 py-1 bg-blue-500 text-white text-xs rounded hover:bg-blue-600 disabled:opacity-50"
                        >
                            Blog
                        </button>
                        <button
                            onClick={() => generateContent("Write a professional email campaign", "email")}
                            disabled={isLoading || apiStatus !== 'connected'}
                            className="px-3 py-1 bg-blue-500 text-white text-xs rounded hover:bg-blue-600 disabled:opacity-50"
                        >
                            Email
                        </button>
                    </div>
                </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
                {messages.length === 0 && (
                    <div className="text-center py-12">
                        <Bot className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">
                            Welcome to Muse Vertex AI
                        </h3>
                        <p className="text-sm text-gray-600 mb-6">
                            I'm your AI content creation assistant powered by Gemini 2.0 Flash.
                        </p>

                        <div className="space-y-2">
                            <p className="text-xs text-gray-500">Try asking me:</p>
                            <div className="space-y-1">
                                <button
                                    onClick={() => setInput("How can I improve my email marketing campaigns?")}
                                    className="block w-full text-left text-xs text-gray-700 bg-gray-100 border border-gray-300 p-2 rounded hover:bg-gray-200"
                                >
                                    How can I improve my email marketing campaigns?
                                </button>
                                <button
                                    onClick={() => setInput("Create a social media content calendar")}
                                    className="block w-full text-left text-xs text-gray-700 bg-gray-100 border border-gray-300 p-2 rounded hover:bg-gray-200"
                                >
                                    Create a social media content calendar
                                </button>
                            </div>
                        </div>
                    </div>
                )}

                {messages.map((message) => (
                    <div
                        key={message.id}
                        className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                        {message.role === 'assistant' && (
                            <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0">
                                <Bot className="w-3 h-3 text-white" />
                            </div>
                        )}

                        <div
                            className={`max-w-[80%] p-3 rounded-lg ${
                                message.role === 'user'
                                    ? 'bg-blue-500 text-white'
                                    : 'bg-gray-100 border border-gray-300 text-gray-900'
                            }`}
                        >
                            <div className="whitespace-pre-wrap text-sm">{message.content}</div>

                            {/* Metadata */}
                            {(message.tokens_used || message.cost_usd) && (
                                <div className="mt-2 pt-2 border-t border-gray-300 text-xs text-gray-500">
                                    {message.tokens_used && <span>Tokens: {message.tokens_used}</span>}
                                    {message.tokens_used && message.cost_usd && <span> • </span>}
                                    {message.cost_usd && <span>Cost: ${message.cost_usd.toFixed(6)}</span>}
                                </div>
                            )}
                        </div>

                        {message.role === 'user' && (
                            <div className="w-6 h-6 bg-gray-500 rounded-full flex items-center justify-center flex-shrink-0">
                                <User className="w-3 h-3 text-white" />
                            </div>
                        )}
                    </div>
                ))}

                {isLoading && (
                    <div className="flex gap-3 justify-start">
                        <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center">
                            <Bot className="w-3 h-3 text-white" />
                        </div>
                        <div className="bg-gray-100 border border-gray-300 p-3 rounded-lg">
                            <div className="flex items-center gap-2">
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse"></div>
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse delay-75"></div>
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse delay-150"></div>
                            </div>
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="p-4 border-t border-gray-200 bg-white">
                <form onSubmit={handleSubmit} className="flex gap-2">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Ask Muse anything about marketing..."
                        className="flex-1 px-3 py-2 bg-white border border-gray-300 rounded text-sm text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        disabled={isLoading || apiStatus !== 'connected'}
                    />
                    <button
                        type="submit"
                        disabled={!input.trim() || isLoading || apiStatus !== 'connected'}
                        className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
                    >
                        {isLoading ? (
                            <StopCircle className="w-4 h-4" />
                        ) : (
                            <Send className="w-4 h-4" />
                        )}
                    </button>
                </form>
            </div>
        </div>
    );
}
