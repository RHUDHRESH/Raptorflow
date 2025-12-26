'use client';

import React, { useState, useRef, useEffect, useCallback, useMemo } from 'react';
import { cn } from '@/lib/utils';
import { Send, User, Sparkles, ChevronRight, AtSign, Hash, X } from 'lucide-react';
import { AssetType, ASSET_TYPES, getAssetConfig } from './types';
import { VariantSelector, generateMockVariants } from './VariantSelector';
import { useIcpStore } from '@/lib/icp-store';
import { selectSkill } from '@/lib/muse/skill-selector';
import { SYSTEM_SKILLS } from '@/lib/muse/skills-inventory';
import { spine } from '@/lib/muse/spine-client';
import { motion, AnimatePresence } from 'motion/react';
import { gsap } from 'gsap';
import { TypingText } from '@/components/ui/typing-text';
import { useTypingExperience } from '@/components/ui/typing/TypingExperienceProvider';

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
type CommandType = 'asset' | 'cohort' | 'campaign' | 'competitor' | '/' | '@';

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

    const candidates = [...ASSET_TYPES].sort((a, b) => b.type.length - a.type.length);

    // Direct asset type matches
    for (const asset of candidates) {
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

const GREETING_WORDS = new Set(['hey', 'hi', 'hello', 'yo', 'sup']);

function isGreeting(message: string): boolean {
    const normalized = message.trim().toLowerCase().replace(/[.!?,]/g, '');
    return GREETING_WORDS.has(normalized);
}

function buildAssetOptions(types: AssetType[]): ConversationOption[] {
    return types.map((type) => {
        const config = getAssetConfig(type);
        return {
            id: `asset-${type}`,
            label: config?.label || type,
            description: config?.description,
            value: type,
        };
    });
}

function isAssetOption(value: ConversationOption['value']): value is AssetType {
    return !!getAssetConfig(value as AssetType);
}

export function MuseChat({
    initialPrompt,
    onAssetCreate,
    cohorts = [],
    campaigns = [],
    competitors = [],
    className
}: MuseChatProps) {
    const { playKeySound, playClickSound, playCompletionSound } = useTypingExperience();
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [isTyping, setIsTyping] = useState(false);
    const [showCommands, setShowCommands] = useState(false);
    const [commandType, setCommandType] = useState<CommandType | null>(null);
    const [commandFilter, setCommandFilter] = useState('');
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
    const inputWrapperRef = useRef<HTMLDivElement>(null);
    const chatContainerRef = useRef<HTMLDivElement>(null);

    // GSAP animations for new messages
    useEffect(() => {
        if (messages.length > 0) {
            gsap.from('.message-bubble-new', {
                opacity: 0,
                y: 20,
                duration: 0.4,
                stagger: 0.1,
                ease: 'power2.out'
            });
        }
    }, [messages.length]);

    const assetOptions = useMemo(
        () => buildAssetOptions(ASSET_TYPES.map(asset => asset.type)),
        []
    );

    const extractContext = useCallback((message: string): Record<string, string> => {
        const lower = message.toLowerCase();
        const matchByName = <T extends { name: string }>(items: T[]) =>
            items.find(item => lower.includes(item.name.toLowerCase()));

        const matchedCohort = matchByName(cohorts);
        const matchedCampaign = matchByName(campaigns);
        const matchedCompetitor = matchByName(competitors);

        const context: Record<string, string> = {};
        if (matchedCohort) context.cohort = matchedCohort.name;
        if (matchedCampaign) context.campaign = matchedCampaign.name;
        if (matchedCompetitor) context.competitor = matchedCompetitor.name;

        return context;
    }, [cohorts, campaigns, competitors]);

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

    // Scroll input into view when command dropdown opens
    useEffect(() => {
        if (showCommands && inputWrapperRef.current) {
            // Scroll the input wrapper into view with some extra space for the dropdown
            inputWrapperRef.current.scrollIntoView({ behavior: 'smooth', block: 'end' });
        }
    }, [showCommands]);

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

        if (isAssetOption(option.value)) {
            const assetType = option.value;
            const context: Record<string, string> = {};
            if (currentContext.cohort) context.cohort = currentContext.cohort;
            if (currentContext.campaign) context.campaign = currentContext.campaign;
            if (currentContext.prompt) {
                setCurrentContext(prev => ({ ...prev, assetType }));
                addMessage('muse', 'Hey, coming right up,');
                onAssetCreate(currentContext.prompt, assetType, Object.keys(context).length ? context : undefined);
                return;
            }

            setCurrentContext(prev => ({ ...prev, assetType }));
            const assetLabel = getAssetConfig(assetType)?.label || assetType;
            addMessage('muse', `Nice. What should the ${assetLabel.toLowerCase()} be about?`);
            return;
        }

        // Pass threadId back to resume the graph
        handleMuseResponse(option.label, currentContext.threadId);
    }, [addMessage, handleMuseResponse, currentContext, onAssetCreate]);

    // Handle input change with command detection
    const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        const value = e.target.value;
        setInput(value);

        // Play typing sound for each character
        playKeySound({ velocity: 0.3 });

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

        // Play click sound when sending
        playClickSound({ velocity: 0.5 });

        const userMessage = input.trim();
        setInput('');
        setShowCommands(false);
        addMessage('user', userMessage);

        const messageContext = extractContext(userMessage);
        if (Object.keys(messageContext).length > 0) {
            setCurrentContext(prev => ({ ...prev, ...messageContext }));
        }

        const contextForAsset: Record<string, string> = { ...messageContext };
        if (currentContext.cohort && !contextForAsset.cohort) {
            contextForAsset.cohort = currentContext.cohort;
        }
        if (currentContext.campaign && !contextForAsset.campaign) {
            contextForAsset.campaign = currentContext.campaign;
        }

        if (isGreeting(userMessage)) {
            setCurrentContext(prev => ({ ...prev, prompt: undefined, assetType: undefined }));
            addMessage('muse', 'Hey,\nWhat would you like to create?', assetOptions);
            return;
        }

        if (currentContext.assetType && !currentContext.prompt) {
            addMessage('muse', 'Hey, coming right up,');
            setCurrentContext(prev => ({ ...prev, prompt: userMessage }));
            onAssetCreate(userMessage, currentContext.assetType, Object.keys(contextForAsset).length ? contextForAsset : undefined);
            return;
        }

        const intent = parseIntent(userMessage);
        if (intent.understood && intent.assetType) {
            addMessage('muse', 'Hey, coming right up,');
            setCurrentContext(prev => ({ ...prev, prompt: userMessage, assetType: intent.assetType }));
            onAssetCreate(userMessage, intent.assetType, Object.keys(contextForAsset).length ? contextForAsset : undefined);
            return;
        }

        if (intent.needsClarification === 'asset_type') {
            setCurrentContext(prev => ({ ...prev, prompt: userMessage, assetType: undefined }));
            addMessage('muse', 'Got it. What kind of asset should I create?', assetOptions);
            return;
        }

        handleMuseResponse(userMessage);
    }, [input, addMessage, assetOptions, extractContext, handleMuseResponse, onAssetCreate, currentContext]);

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
        <div ref={chatContainerRef} className={cn('flex flex-col h-full', className)}>
            {/* Messages area with enhanced animations */}
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.6 }}
                className="flex-1 overflow-auto"
            >
                {messages.length === 0 ? (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8 }}
                    >
                        <WelcomeState onPromptClick={(prompt) => {
                            setInput(prompt);
                            inputRef.current?.focus();
                        }} />
                    </motion.div>
                ) : (
                    <div className="max-w-2xl mx-auto space-y-6">
                        <AnimatePresence>
                            {messages.map((message, index) => (
                                <motion.div
                                    key={message.id}
                                    layout
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, y: -20 }}
                                    transition={{
                                        duration: 0.4,
                                        delay: index * 0.05,
                                        ease: 'easeOut'
                                    }}
                                    className="message-bubble-new"
                                >
                                    <MessageBubble
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
                                </motion.div>
                            ))}
                        </AnimatePresence>

                        <AnimatePresence>
                            {isTyping && (
                                <motion.div
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, y: -10 }}
                                    className="flex items-start gap-4"
                                >
                                    <div className="h-8 w-8 rounded-full bg-foreground flex items-center justify-center shrink-0">
                                        <motion.div
                                            animate={{ rotate: 360 }}
                                            transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                                        >
                                            <Sparkles className="h-4 w-4 text-background" />
                                        </motion.div>
                                    </div>
                                    <div className="flex items-center gap-1 pt-2">
                                        <TypingText
                                            messages={[
                                                "Thinking...",
                                                "Crafting your response...",
                                                "Almost there...",
                                                "Putting it all together..."
                                            ]}
                                            className="text-xs text-gray-600/40"
                                            speed={80}
                                            deleteSpeed={40}
                                            pauseDuration={1500}
                                        />
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>

                        <div ref={messagesEndRef} />
                    </div>
                )}
            </motion.div>

            {/* Enhanced Input area with magnetic animations */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.3 }}
                className="p-6"
            >
                <div ref={inputWrapperRef} className="max-w-2xl mx-auto relative">
                    {/* Command suggestions dropdown - Monochrome, scrollable */}
                    <AnimatePresence mode="wait">
                        {showCommands && commandSuggestions.length > 0 && (
                            <motion.div
                                initial={{ opacity: 0, y: 8 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: 8 }}
                                transition={{ duration: 0.15 }}
                                className="absolute bottom-full mb-2 left-0 right-0 bg-white border border-[#E5E6E3] rounded-xl shadow-lg overflow-hidden z-50"
                            >
                                <div className="px-3 py-2 border-b border-[#E5E6E3] flex items-center justify-between">
                                    <span className="text-[11px] font-mono uppercase tracking-wider text-[#9D9F9F]">
                                        {commandType === '/' ? 'Asset Types' : 'References'}
                                    </span>
                                    <button
                                        onClick={() => setShowCommands(false)}
                                        className="p-1 hover:bg-[#F8F9F7] rounded"
                                    >
                                        <X className="h-3 w-3 text-[#9D9F9F]" />
                                    </button>
                                </div>
                                <div className="max-h-48 overflow-y-auto overscroll-contain">
                                    {commandSuggestions.map((suggestion, index) => (
                                        <button
                                            key={suggestion.id}
                                            onClick={() => selectCommand(suggestion)}
                                            className={cn(
                                                'w-full flex items-center gap-3 px-3 py-2.5 text-left transition-colors',
                                                'hover:bg-[#F8F9F7]',
                                                index === selectedCommandIndex && 'bg-[#F8F9F7]'
                                            )}
                                        >
                                            <div className="h-7 w-7 rounded-lg bg-[#F8F9F7] border border-[#E5E6E3] flex items-center justify-center shrink-0">
                                                {commandType === '/' ? (
                                                    <Hash className="h-3.5 w-3.5 text-[#5B5F61]" />
                                                ) : (
                                                    <AtSign className="h-3.5 w-3.5 text-[#5B5F61]" />
                                                )}
                                            </div>
                                            <div className="flex-1 min-w-0">
                                                <p className="text-[13px] font-medium text-[#2D3538] truncate">{suggestion.label}</p>
                                                {suggestion.description && (
                                                    <p className="text-[11px] text-[#9D9F9F] truncate">{suggestion.description}</p>
                                                )}
                                            </div>
                                        </button>
                                    ))}
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>

                    <motion.div
                        whileHover={{ scale: 1.02 }}
                        whileFocus={{
                            scale: 1.03,
                            boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)'
                        }}
                        transition={{
                            type: "spring",
                            stiffness: 300,
                            damping: 30,
                            mass: 0.8
                        }}
                        className={cn(
                            'relative group rounded-2xl border bg-card transition-all duration-300',
                            'border-border/60 shadow-sm',
                            'focus-within:border-foreground/20 focus-within:shadow-lg focus-within:shadow-foreground/5'
                        )}
                    >
                        <textarea
                            ref={inputRef}
                            value={input}
                            onChange={handleInputChange}
                            onKeyDown={handleKeyDown}
                            placeholder="Describe what you want to create... (use / or @)"
                            rows={1}
                            className={cn(
                                'w-full resize-none bg-transparent border-none outline-none',
                                'text-[15px] leading-relaxed placeholder:text-[#9D9F9F]',
                                'p-4 pr-14',
                                'min-h-[52px] max-h-[200px]'
                            )}
                            style={{ letterSpacing: '-0.01em' }}
                        />

                        <motion.button
                            whileHover={{
                                scale: 1.15,
                                boxShadow: '0 10px 20px -5px rgba(0, 0, 0, 0.3)',
                                rotate: [0, -5, 5, 0]
                            }}
                            whileTap={{
                                scale: 0.85,
                                boxShadow: '0 2px 4px -1px rgba(0, 0, 0, 0.2)',
                                rotate: [0, 2, -2, 0]
                            }}
                            transition={{
                                type: "spring",
                                stiffness: 400,
                                damping: 17,
                                rotate: { duration: 0.3, repeat: 0 }
                            }}
                            onClick={handleSubmit}
                            disabled={!input.trim()}
                            className={cn(
                                'absolute right-3 top-1/2 -translate-y-1/2',
                                'flex items-center justify-center h-10 w-10 rounded-xl',
                                'bg-foreground text-background',
                                'transition-all duration-200',
                                'disabled:opacity-20 disabled:cursor-not-allowed disabled:hover:scale-100'
                            )}
                        >
                            <Send className="h-4 w-4" />
                        </motion.button>
                    </motion.div>

                    <p className="text-center text-[11px] text-[#9D9F9F] mt-3">
                        <kbd className="px-1.5 py-0.5 rounded-md bg-[#F8F9F7] border border-[#E5E6E3] font-mono text-[10px] text-[#5B5F61]">/</kbd> asset types • <kbd className="px-1.5 py-0.5 rounded-md bg-[#F8F9F7] border border-[#E5E6E3] font-mono text-[10px] text-[#5B5F61]">@</kbd> cohorts & campaigns
                    </p>
                </div>
            </motion.div>
        </div>
    );
}

function WelcomeState({ onPromptClick }: { onPromptClick?: (prompt: string) => void }) {
    // Smart prompts with monochrome Lucide icons
    const smartPrompts = [
        { id: 'cold-email', label: 'Cold Sales Email', prompt: 'Write a cold sales email that gets replies. Focus on value, not features.', icon: 'mail' },
        { id: 'linkedin', label: 'LinkedIn Announcement', prompt: 'Create a LinkedIn post announcing our latest update. Make it authentic, not corporate.', icon: 'briefcase' },
        { id: 'tagline', label: 'New Tagline Ideas', prompt: 'Generate 5 tagline options for our brand. Short, memorable, aligned with positioning.', icon: 'message-circle' },
        { id: 'product-name', label: 'Product Name Ideas', prompt: 'Brainstorm product name ideas that are memorable and brandable.', icon: 'lightbulb' },
        { id: 'hook', label: 'Attention-Grabbing Hook', prompt: 'Write an opening hook for a landing page that stops the scroll.', icon: 'anchor' },
        { id: 'meme', label: 'Industry Meme', prompt: 'Create a meme that pokes fun at a common pain point our audience faces.', icon: 'smile' },
    ];

    // Monochrome icon renderer
    const getIcon = (iconName: string) => {
        const iconClass = "h-5 w-5 text-[#5B5F61]";
        switch (iconName) {
            case 'mail': return <Send className={iconClass} />;
            case 'briefcase': return <User className={iconClass} />;
            case 'message-circle': return <Hash className={iconClass} />;
            case 'lightbulb': return <Sparkles className={iconClass} />;
            case 'anchor': return <ChevronRight className={iconClass} />;
            case 'smile': return <AtSign className={iconClass} />;
            default: return <Sparkles className={iconClass} />;
        }
    };

    return (
        <div className="flex flex-col items-center justify-center h-full text-center px-8 py-16">
            {/* Editorial Headline */}
            <h2 className="font-serif text-[36px] text-[#2D3538] tracking-tight leading-tight mb-4">
                How can I help you today?
            </h2>
            <p className="font-sans text-[15px] text-[#5B5F61] leading-relaxed max-w-md mb-16">
                Start a conversation or pick a suggestion below.
            </p>

            {/* Monochrome Prompts Grid */}
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 w-full max-w-3xl">
                {smartPrompts.map((sp, index) => (
                    <motion.button
                        key={sp.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{
                            duration: 0.4,
                            delay: index * 0.08,
                            ease: 'easeOut'
                        }}
                        whileHover={{ y: -2 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => onPromptClick?.(sp.prompt)}
                        className={cn(
                            'group flex flex-col items-start gap-3 p-5 rounded-2xl text-left',
                            'bg-[#F8F9F7] border border-[#E5E6E3]',
                            'hover:border-[#C0C1BE] hover:shadow-[0_8px_24px_rgba(0,0,0,0.04)]',
                            'transition-all duration-300'
                        )}
                    >
                        <div className="h-10 w-10 rounded-xl bg-white border border-[#E5E6E3] flex items-center justify-center">
                            {getIcon(sp.icon)}
                        </div>
                        <span className="text-[14px] font-medium text-[#2D3538] tracking-tight">{sp.label}</span>
                    </motion.button>
                ))}
            </div>

            <p className="text-[11px] text-[#9D9F9F] mt-10">
                <kbd className="px-1.5 py-0.5 rounded-md bg-white border border-[#E5E6E3] font-mono text-[10px] text-[#5B5F61]">/</kbd> asset types • <kbd className="px-1.5 py-0.5 rounded-md bg-white border border-[#E5E6E3] font-mono text-[10px] text-[#5B5F61]">@</kbd> cohorts & campaigns
            </p>
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
                isUser ? 'bg-[#F8F9F7] border border-[#E5E6E3]' : 'bg-[#2D3538]'
            )}>
                {isUser ? (
                    <User className="h-4 w-4 text-[#5B5F61]" />
                ) : (
                    <Sparkles className="h-4 w-4 text-white" />
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
                                        <p className="text-xs text-gray-600 mt-0.5">{option.description}</p>
                                    )}
                                </div>
                                <ChevronRight className="h-4 w-4 text-gray-600 group-hover:text-foreground transition-colors" />
                            </button>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
