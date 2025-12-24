'use client';

import React, { useState, useRef, useEffect, useCallback, useMemo } from 'react';
import { cn } from '@/lib/utils';
import { Send, User, Sparkles, ChevronRight, AtSign, Hash, X } from 'lucide-react';
import { AssetType, ASSET_TYPES, getAssetConfig } from './types';
import { VariantSelector, generateMockVariants } from './VariantSelector';
import { useIcpStore } from '@/lib/icp-store';
import { selectSkill } from '@/lib/muse/skill-selector';
import { SYSTEM_SKILLS } from '@/lib/muse/skills-inventory';

interface Message {
    id: string;
    role: 'user' | 'muse';
    content: string;
    timestamp: Date;
    options?: ConversationOption[];
    variants?: any[]; // Using any to avoid circular deps for now
    selectedOption?: string;
    selectedVariant?: string;
}

interface ConversationOption {
    id: string;
    label: string;
    description?: string;
    value: AssetType | string;
}

interface MuseChatProps {
    initialPrompt?: string;
    onAssetCreate: (prompt: string, assetType: AssetType, context?: Record<string, string>) => void;
    cohorts?: { id: string; name: string }[];
    campaigns?: { id: string; name: string }[];
    competitors?: { name: string }[];
    className?: string;
}

// Command types
type CommandType = 'asset' | 'cohort' | 'campaign' | 'competitor';

interface CommandSuggestion {
    id: string;
    type: CommandType;
    label: string;
    description?: string;
    trigger: string; // The text that triggers this (for replacement)
}

// Conversation flow logic
function parseIntent(message: string): { understood: boolean; assetType?: AssetType; needsClarification?: string } {
    const lower = message.toLowerCase();

    // Direct asset type matches
    for (const asset of ASSET_TYPES) {
        if (lower.includes(asset.type.replace('-', ' ')) ||
            lower.includes(asset.label.toLowerCase())) {
            return { understood: true, assetType: asset.type };
        }
    }

    // Vague requests that need clarification
    if (lower.match(/make|create|build|generate|write|design/i) &&
        !ASSET_TYPES.some(a => lower.includes(a.label.toLowerCase()))) {
        return { understood: false, needsClarification: 'asset_type' };
    }

    return { understood: false, needsClarification: 'unclear' };
}

export function MuseChat({ initialPrompt, onAssetCreate, cohorts = [], campaigns = [], competitors = [], className }: MuseChatProps) {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState(initialPrompt || '');
    const [isTyping, setIsTyping] = useState(false);
    const [showCommands, setShowCommands] = useState(false);
    const [commandFilter, setCommandFilter] = useState('');
    const [commandType, setCommandType] = useState<'/' | '@' | null>(null);
    const [selectedCommandIndex, setSelectedCommandIndex] = useState(0);
    const [currentContext, setCurrentContext] = useState<{
        prompt?: string;
        assetType?: AssetType;
        cohort?: string;
        campaign?: string;
        variantCount?: number;
        threadId?: string;
    }>({});
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLTextAreaElement>(null);

    // Build command suggestions
    const commandSuggestions: CommandSuggestion[] = useMemo(() => {
        const suggestions: CommandSuggestion[] = [];

        if (commandType === '/') {
            // Slash commands for asset types
            ASSET_TYPES.forEach(asset => {
                suggestions.push({
                    id: `asset-${asset.type}`,
                    type: 'asset',
                    label: asset.label,
                    description: asset.description,
                    trigger: `/${asset.type}`,
                });
            });
        } else if (commandType === '@') {
            // @ commands for cohorts and campaigns
            cohorts.forEach(cohort => {
                suggestions.push({
                    id: `cohort-${cohort.id}`,
                    type: 'cohort',
                    label: cohort.name,
                    description: 'Target audience',
                    trigger: `@${cohort.name}`,
                });
            });
            campaigns.forEach(campaign => {
                suggestions.push({
                    id: `campaign-${campaign.id}`,
                    type: 'campaign',
                    label: campaign.name,
                    description: 'Campaign',
                    trigger: `@${campaign.name}`,
                });
            });
            competitors.forEach((comp, i) => {
                suggestions.push({
                    id: `competitor-${i}`,
                    type: 'competitor' as CommandType,
                    label: comp.name,
                    description: 'Competitor',
                    trigger: `@${comp.name}`,
                });
            });
        }

        // Filter by search
        if (commandFilter) {
            return suggestions.filter(s =>
                s.label.toLowerCase().includes(commandFilter.toLowerCase())
            );
        }

        return suggestions;
    }, [commandType, commandFilter, cohorts, campaigns, competitors]);

    // Scroll to bottom when messages change
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    // Auto-focus input
    useEffect(() => {
        inputRef.current?.focus();
    }, []);

    // Reset command selection when suggestions change
    useEffect(() => {
        setSelectedCommandIndex(0);
    }, [commandSuggestions.length]);

    const addMessage = useCallback((role: 'user' | 'muse', content: string, options?: ConversationOption[], variants?: any[]) => {
        const message: Message = {
            id: `msg-${Date.now()}-${Math.random()}`,
            role,
            content,
            timestamp: new Date(),
            options,
            variants,
        };
        setMessages(prev => [...prev, message]);
        return message;
    }, []);

import { spine } from '@/lib/muse/spine-client';

// ...

    const handleMuseResponse = useCallback(async (userMessage: string, threadId?: string) => {
        setIsTyping(true);

        try {
            const response = await spine.chat(userMessage, threadId);

            // Handle text response
            if (response.asset_content) {
                addMessage('muse', response.asset_content);
            }

            // Save threadId for future context
            if (response.thread_id) {
                setCurrentContext(prev => ({ ...prev, threadId: response.thread_id }));
            }

        } catch (error: any) {
            console.error("Muse Chat Error:", error);
            addMessage('muse', "Muse couldn't generate that. Add one detail and retry.");
        } finally {
            setIsTyping(false);
        }
    }, [addMessage]);

    // Resume logic for clarification
    const handleOptionSelect = useCallback((messageId: string, option: ConversationOption) => {
        setMessages(prev => prev.map(m =>
            m.id === messageId ? { ...m, selectedOption: option.id } : m
        ));
        addMessage('user', option.label);

        // Pass threadId back to resume the graph
        handleMuseResponse(option.label, currentContext.threadId);
    }, [addMessage, handleMuseResponse, currentContext.threadId]);

    // Handle input change with command detection
    const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        const value = e.target.value;
        setInput(value);

        // Detect / or @ commands
        const lastWord = value.split(' ').pop() || '';

        if (lastWord.startsWith('/') && lastWord.length >= 1) {
            setCommandType('/');
            setCommandFilter(lastWord.slice(1));
            setShowCommands(true);
        } else if (lastWord.startsWith('@') && lastWord.length >= 1) {
            setCommandType('@');
            setCommandFilter(lastWord.slice(1));
            setShowCommands(true);
        } else {
            setShowCommands(false);
            setCommandType(null);
            setCommandFilter('');
        }
    };

    // Select a command suggestion
    const selectCommand = (suggestion: CommandSuggestion) => {
        // Replace the command trigger with the selected item
        const words = input.split(' ');
        words[words.length - 1] = suggestion.trigger + ' ';
        setInput(words.join(' '));
        setShowCommands(false);
        setCommandType(null);
        setCommandFilter('');
        inputRef.current?.focus();
    };

    const handleSubmit = useCallback(() => {
        if (!input.trim()) return;

        const userMessage = input.trim();
        setInput('');
        setShowCommands(false);
        addMessage('user', userMessage);

        handleMuseResponse(userMessage);
    }, [input, addMessage, handleMuseResponse]);

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (showCommands && commandSuggestions.length > 0) {
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                setSelectedCommandIndex(prev =>
                    prev < commandSuggestions.length - 1 ? prev + 1 : 0
                );
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                setSelectedCommandIndex(prev =>
                    prev > 0 ? prev - 1 : commandSuggestions.length - 1
                );
            } else if (e.key === 'Enter' || e.key === 'Tab') {
                e.preventDefault();
                selectCommand(commandSuggestions[selectedCommandIndex]);
            } else if (e.key === 'Escape') {
                setShowCommands(false);
            }
        } else if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit();
        }
    };

    return (
        <div className={cn('flex flex-col h-full', className)}>
            {/* Messages area */}
            <div className="flex-1 overflow-auto px-6 py-8">
                {messages.length === 0 ? (
                    <WelcomeState onPromptClick={(prompt) => {
                        setInput(prompt);
                        inputRef.current?.focus();
                    }} />
                ) : (
                    <div className="max-w-2xl mx-auto space-y-6">
                        {messages.map(message => (
                            <MessageBubble
                                key={message.id}
                                message={message}
                                onOptionSelect={(option) => handleOptionSelect(message.id, option)}
                                onVariantSelect={(variant) => {
                                    // Handle variant selection - create asset from this variant
                                    onAssetCreate(
                                        variant.content,
                                        currentContext.assetType || 'email',
                                        {
                                            cohort: currentContext.cohort || '',
                                            originalPrompt: currentContext.prompt!
                                        }
                                    );
                                }}
                            />
                        ))}

                        {isTyping && (
                            <div className="flex items-start gap-4">
                                <div className="h-8 w-8 rounded-full bg-foreground flex items-center justify-center shrink-0">
                                    <Sparkles className="h-4 w-4 text-background" />
                                </div>
                                <div className="flex items-center gap-1 pt-2">
                                    <span className="h-2 w-2 rounded-full bg-muted-foreground/40 animate-pulse" />
                                    <span className="h-2 w-2 rounded-full bg-muted-foreground/40 animate-pulse" style={{ animationDelay: '150ms' }} />
                                    <span className="h-2 w-2 rounded-full bg-muted-foreground/40 animate-pulse" style={{ animationDelay: '300ms' }} />
                                </div>
                            </div>
                        )}

                        <div ref={messagesEndRef} />
                    </div>
                )}
            </div>

            {/* Input area */}
            <div className="border-t border-border/40 p-6">
                <div className="max-w-2xl mx-auto relative">
                    {/* Command suggestions dropdown */}
                    {showCommands && commandSuggestions.length > 0 && (
                        <div className="absolute bottom-full mb-2 left-0 right-0 bg-card border border-border/60 rounded-xl shadow-xl overflow-hidden z-10">
                            <div className="p-2 border-b border-border/40 flex items-center justify-between">
                                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                                    {commandType === '/' && <Hash className="h-3 w-3" />}
                                    {commandType === '@' && <AtSign className="h-3 w-3" />}
                                    <span>{commandType === '/' ? 'Asset Types' : 'References'}</span>
                                </div>
                                <button
                                    onClick={() => setShowCommands(false)}
                                    className="p-1 hover:bg-muted rounded"
                                >
                                    <X className="h-3 w-3" />
                                </button>
                            </div>
                            <div className="max-h-64 overflow-auto">
                                {commandSuggestions.map((suggestion, index) => (
                                    <button
                                        key={suggestion.id}
                                        onClick={() => selectCommand(suggestion)}
                                        className={cn(
                                            'w-full flex items-center gap-3 px-4 py-3 text-left transition-colors',
                                            index === selectedCommandIndex ? 'bg-muted' : 'hover:bg-muted/50'
                                        )}
                                    >
                                        <div className={cn(
                                            'h-8 w-8 rounded-lg flex items-center justify-center shrink-0',
                                            suggestion.type === 'asset' && 'bg-foreground/10',
                                            suggestion.type === 'cohort' && 'bg-blue-500/10',
                                            suggestion.type === 'campaign' && 'bg-purple-500/10',
                                            suggestion.type === 'competitor' && 'bg-red-500/10'
                                        )}>
                                            {suggestion.type === 'asset' && <Hash className="h-4 w-4" />}
                                            {suggestion.type === 'cohort' && <AtSign className="h-4 w-4 text-blue-500" />}
                                            {suggestion.type === 'campaign' && <AtSign className="h-4 w-4 text-purple-500" />}
                                            {suggestion.type === 'competitor' && <AtSign className="h-4 w-4 text-red-500" />}
                                        </div>
                                        <div className="flex-1 min-w-0">
                                            <p className="font-medium text-sm truncate">{suggestion.label}</p>
                                            {suggestion.description && (
                                                <p className="text-xs text-muted-foreground truncate">{suggestion.description}</p>
                                            )}
                                        </div>
                                    </button>
                                ))}
                            </div>
                        </div>
                    )}

                    <div className={cn(
                        'relative group rounded-2xl border bg-card transition-all duration-300',
                        'border-border/60 shadow-sm',
                        'focus-within:border-foreground/20 focus-within:shadow-lg focus-within:shadow-foreground/5'
                    )}>
                        <textarea
                            ref={inputRef}
                            value={input}
                            onChange={handleInputChange}
                            onKeyDown={handleKeyDown}
                            placeholder="Describe what you want to create... (use / or @)"
                            rows={1}
                            className={cn(
                                'w-full resize-none bg-transparent border-none outline-none',
                                'text-base leading-relaxed placeholder:text-muted-foreground/40',
                                'p-4 pr-14',
                                'min-h-[56px] max-h-[200px]'
                            )}
                            style={{ letterSpacing: '-0.01em' }}
                        />

                        <button
                            onClick={handleSubmit}
                            disabled={!input.trim()}
                            className={cn(
                                'absolute right-3 top-1/2 -translate-y-1/2',
                                'flex items-center justify-center h-10 w-10 rounded-xl',
                                'bg-foreground text-background',
                                'transition-all duration-200',
                                'hover:scale-105 active:scale-95',
                                'disabled:opacity-20 disabled:cursor-not-allowed disabled:hover:scale-100'
                            )}
                        >
                            <Send className="h-4 w-4" />
                        </button>
                    </div>

                    <p className="text-center text-xs text-muted-foreground/40 mt-3">
                        Type <kbd className="px-1 py-0.5 rounded bg-muted font-mono text-[10px]">/</kbd> for asset types • <kbd className="px-1 py-0.5 rounded bg-muted font-mono text-[10px]">@</kbd> for cohorts, competitors, or campaigns
                    </p>
                </div>
            </div>
        </div>
    );
}

function WelcomeState({ onPromptClick }: { onPromptClick?: (prompt: string) => void }) {
    // Smart prompts based on common use cases
    const smartPrompts = [
        { id: 'cold-email', label: 'Cold Sales Email', prompt: 'Write a cold sales email that gets replies. Focus on value, not features.', icon: '📧' },
        { id: 'linkedin', label: 'LinkedIn Announcement', prompt: 'Create a LinkedIn post announcing our latest update. Make it authentic, not corporate.', icon: '💼' },
        { id: 'tagline', label: 'New Tagline Ideas', prompt: 'Generate 5 tagline options for our brand. Short, memorable, aligned with positioning.', icon: '💬' },
        { id: 'product-name', label: 'Product Name Ideas', prompt: 'Brainstorm product name ideas that are memorable and domain-available.', icon: '💡' },
        { id: 'hook', label: 'Attention-Grabbing Hook', prompt: 'Write an opening hook for a landing page that stops the scroll.', icon: '🎣' },
        { id: 'meme', label: 'Industry Meme', prompt: 'Create a meme that pokes fun at a common pain point our audience faces.', icon: '😂' },
    ];

    return (
        <div className="flex flex-col items-center justify-center h-full text-center max-w-2xl mx-auto px-6">
            {/* Icon */}
            <div className="h-16 w-16 rounded-2xl bg-foreground/5 flex items-center justify-center mb-8">
                <Sparkles className="h-8 w-8 text-foreground/60" />
            </div>

            <h2 className="font-display text-4xl font-medium tracking-tight mb-4">
                What shall we create?
            </h2>
            <p className="text-lg text-muted-foreground leading-relaxed max-w-md mb-10">
                Describe an asset or pick a suggestion below.
            </p>

            {/* Smart Prompts Grid */}
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3 w-full">
                {smartPrompts.map((sp) => (
                    <button
                        key={sp.id}
                        onClick={() => onPromptClick?.(sp.prompt)}
                        className={cn(
                            'group flex flex-col items-start gap-2 p-4 rounded-xl text-left',
                            'border border-border/60 bg-card/50',
                            'hover:border-foreground/20 hover:bg-muted/30 hover:shadow-sm',
                            'transition-all duration-200'
                        )}
                    >
                        <span className="text-2xl">{sp.icon}</span>
                        <span className="text-sm font-medium group-hover:text-foreground transition-colors">{sp.label}</span>
                    </button>
                ))}
            </div>

            <p className="text-xs text-muted-foreground/50 mt-8">
                Use <kbd className="px-1 py-0.5 rounded bg-muted font-mono text-[10px]">@</kbd> to mention cohorts, competitors, or campaigns
            </p>

            {/* Pro Tips */}
            <div className="mt-6 p-4 rounded-xl border border-border/40 bg-muted/20 max-w-md">
                <p className="text-xs font-medium text-muted-foreground mb-2">💡 Pro Tips</p>
                <ul className="text-xs text-muted-foreground/70 space-y-1">
                    <li>• Add <code className="px-1 bg-muted rounded">--variants 3</code> to generate multiple options</li>
                    <li>• Use <code className="px-1 bg-muted rounded">/meme</code> or <code className="px-1 bg-muted rounded">/email</code> for quick asset types</li>
                    <li>• Press <kbd className="px-1 bg-muted rounded font-mono">⌘S</kbd> to save anytime in the editor</li>
                </ul>
            </div>
        </div>
    );
}


function MessageBubble({
    message,
    onOptionSelect,
    onVariantSelect
}: {
    message: Message;
    onOptionSelect: (option: ConversationOption) => void;
    onVariantSelect?: (variant: any) => void;
}) {
    const isUser = message.role === 'user';

    return (
        <div className={cn('flex items-start gap-4', isUser && 'flex-row-reverse')}>
            {/* Avatar */}
            <div className={cn(
                'h-8 w-8 rounded-full flex items-center justify-center shrink-0',
                isUser ? 'bg-muted' : 'bg-foreground'
            )}>
                {isUser ? (
                    <User className="h-4 w-4 text-muted-foreground" />
                ) : (
                    <Sparkles className="h-4 w-4 text-background" />
                )}
            </div>

            {/* Content */}
            <div className={cn('flex-1 space-y-3', isUser && 'text-right')}>
                <div className={cn(
                    'inline-block rounded-2xl px-4 py-3 max-w-[85%]',
                    isUser
                        ? 'bg-foreground text-background'
                        : 'bg-muted/50'
                )}>
                    <p className="text-sm leading-relaxed whitespace-pre-line">{message.content}</p>
                </div>

                {/* Variants */}
                {message.variants && (
                    <div className="w-full max-w-lg">
                        <VariantSelector
                            variants={message.variants}
                            selectedId={message.selectedVariant}
                            onSelect={onVariantSelect}
                        />
                    </div>
                )}

                {/* Options */}
                {message.options && !message.selectedOption && (
                    <div className="flex flex-wrap gap-2">
                        {message.options.map(option => (
                            <button
                                key={option.id}
                                onClick={() => onOptionSelect(option)}
                                className={cn(
                                    'group flex items-center gap-2 px-4 py-2.5 rounded-xl',
                                    'border border-border/60 bg-card',
                                    'text-sm text-left',
                                    'hover:border-foreground/30 hover:bg-muted/30',
                                    'transition-all duration-200'
                                )}
                            >
                                <div className="flex-1">
                                    <p className="font-medium">{option.label}</p>
                                    {option.description && (
                                        <p className="text-xs text-muted-foreground mt-0.5">{option.description}</p>
                                    )}
                                </div>
                                <ChevronRight className="h-4 w-4 text-muted-foreground group-hover:text-foreground transition-colors" />
                            </button>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
