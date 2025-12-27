'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
    Linkedin, Youtube, MessageCircle, Globe, Users, Mail,
    Calendar, FileText, Video, Image, Mic, Check, AlertCircle
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ChannelHabitatItem } from '@/lib/foundation';

interface ChannelHabitatMapProps {
    channels: ChannelHabitatItem[];
    onUpdateChannel: (id: string, updates: Partial<ChannelHabitatItem>) => void;
    onTogglePrimary: (id: string) => void;
    onToggleSecondary: (id: string) => void;
    primaryCount: number;
    secondaryCount: number;
}

const CHANNEL_CONFIG: Record<string, {
    icon: React.ElementType;
    color: string;
    bgColor: string;
    defaultContentTypes: string[];
    defaultTiming: string;
}> = {
    'LinkedIn': {
        icon: Linkedin,
        color: '#0A66C2',
        bgColor: '#E7F3FF',
        defaultContentTypes: ['Thought leadership', 'Case studies', 'Behind-the-scenes'],
        defaultTiming: 'Tue–Thu, 8–10am'
    },
    'YouTube': {
        icon: Youtube,
        color: '#FF0000',
        bgColor: '#FEE2E2',
        defaultContentTypes: ['Tutorial videos', 'Webinars', 'Customer stories'],
        defaultTiming: 'Wed & Sat'
    },
    'WhatsApp/Communities': {
        icon: MessageCircle,
        color: '#25D366',
        bgColor: '#DCFCE7',
        defaultContentTypes: ['Quick tips', 'Templates', 'Exclusive content'],
        defaultTiming: 'Daily, evening'
    },
    'Reddit/Forums': {
        icon: Globe,
        color: '#FF4500',
        bgColor: '#FFEDD5',
        defaultContentTypes: ['Discussions', 'AMAs', 'Resource shares'],
        defaultTiming: 'Varies by subreddit'
    },
    'Conferences/Events': {
        icon: Users,
        color: '#8B5CF6',
        bgColor: '#EDE9FE',
        defaultContentTypes: ['Speaking', 'Workshops', 'Networking'],
        defaultTiming: 'Quarterly'
    },
    'Email/Newsletter': {
        icon: Mail,
        color: '#2D3538',
        bgColor: '#F3F4EE',
        defaultContentTypes: ['Weekly digest', 'Product updates', 'Educational series'],
        defaultTiming: 'Weekly, Tue morning'
    },
    'Twitter/X': {
        icon: Globe,
        color: '#1DA1F2',
        bgColor: '#E0F2FE',
        defaultContentTypes: ['Threads', 'Insights', 'Engagement'],
        defaultTiming: 'Daily, multiple'
    },
    'Podcast': {
        icon: Mic,
        color: '#9333EA',
        bgColor: '#F3E8FF',
        defaultContentTypes: ['Guest appearances', 'Own show', 'Sponsor reads'],
        defaultTiming: 'Monthly'
    }
};

const CONTENT_TYPE_ICONS: Record<string, React.ElementType> = {
    'Case studies': FileText,
    'Tutorial videos': Video,
    'Thought leadership': FileText,
    'Templates': FileText,
    'Webinars': Video,
    'Behind-the-scenes': Image,
    'default': FileText
};

function ConfidenceMeter({ score }: { score: number }) {
    const segments = 5;
    const filled = Math.round(score / 20);

    return (
        <div className="flex items-center gap-1">
            {[...Array(segments)].map((_, i) => (
                <div
                    key={i}
                    className={`w-4 h-1.5 rounded-full transition-colors ${i < filled ? 'bg-[#2D3538]' : 'bg-[#E5E6E3]'
                        }`}
                />
            ))}
            <span className="text-[10px] font-mono text-[#9D9F9F] ml-1">{score}%</span>
        </div>
    );
}

function ChannelCard({
    channel,
    config,
    onTogglePrimary,
    onToggleSecondary,
    canAddPrimary,
    canAddSecondary,
    index
}: {
    channel: ChannelHabitatItem;
    config: typeof CHANNEL_CONFIG[string];
    onTogglePrimary: () => void;
    onToggleSecondary: () => void;
    canAddPrimary: boolean;
    canAddSecondary: boolean;
    index: number;
}) {
    const Icon = config.icon;

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
            className={`bg-white border-2 rounded-2xl overflow-hidden transition-all ${channel.isPrimary
                    ? 'border-[#2D3538] shadow-lg'
                    : channel.isSecondary
                        ? 'border-[#9D9F9F]'
                        : 'border-[#E5E6E3]'
                }`}
        >
            {/* Header */}
            <div
                className="p-5 flex items-center gap-4"
                style={{ backgroundColor: config.bgColor }}
            >
                <div
                    className="w-12 h-12 rounded-xl flex items-center justify-center"
                    style={{ backgroundColor: config.color }}
                >
                    <Icon className="w-6 h-6 text-white" />
                </div>
                <div className="flex-1">
                    <div className="flex items-center gap-2">
                        <h3 className="font-medium text-[#2D3538]">{channel.platform}</h3>
                        {channel.isPrimary && (
                            <span className="text-[9px] font-mono uppercase bg-[#2D3538] text-white px-2 py-0.5 rounded">
                                Primary
                            </span>
                        )}
                        {channel.isSecondary && (
                            <span className="text-[9px] font-mono uppercase bg-[#9D9F9F] text-white px-2 py-0.5 rounded">
                                Secondary
                            </span>
                        )}
                    </div>
                    <ConfidenceMeter score={channel.confidenceScore} />
                </div>
            </div>

            {/* Content Types */}
            <div className="p-5 border-b border-[#E5E6E3]">
                <span className="text-[10px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F] mb-3 block">
                    Content Types
                </span>
                <div className="flex flex-wrap gap-2">
                    {channel.contentTypes.map((type, i) => {
                        const ContentIcon = CONTENT_TYPE_ICONS[type] || CONTENT_TYPE_ICONS.default;
                        return (
                            <div
                                key={i}
                                className="flex items-center gap-1.5 bg-[#F3F4EE] rounded-lg px-3 py-1.5"
                            >
                                <ContentIcon className="w-3 h-3 text-[#9D9F9F]" />
                                <span className="text-xs text-[#2D3538]">{type}</span>
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* Timing */}
            <div className="p-5 border-b border-[#E5E6E3] bg-[#FAFAF8]">
                <span className="text-[10px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F] mb-2 block">
                    Best Timing
                </span>
                <div className="flex items-center gap-2">
                    <Calendar className="w-4 h-4 text-[#9D9F9F]" />
                    <span className="text-sm text-[#2D3538]">
                        {channel.timingPattern || config.defaultTiming}
                    </span>
                </div>
            </div>

            {/* Actions */}
            <div className="p-4 flex gap-2">
                <Button
                    onClick={onTogglePrimary}
                    disabled={!channel.isPrimary && !canAddPrimary}
                    variant={channel.isPrimary ? "default" : "outline"}
                    size="sm"
                    className={`flex-1 rounded-xl ${channel.isPrimary ? 'bg-[#2D3538] hover:bg-[#1A1D1E]' : ''
                        }`}
                >
                    {channel.isPrimary ? (
                        <>
                            <Check className="w-4 h-4 mr-1" />
                            Primary
                        </>
                    ) : (
                        'Set Primary'
                    )}
                </Button>
                <Button
                    onClick={onToggleSecondary}
                    disabled={channel.isPrimary || (!channel.isSecondary && !canAddSecondary)}
                    variant={channel.isSecondary ? "default" : "outline"}
                    size="sm"
                    className={`flex-1 rounded-xl ${channel.isSecondary ? 'bg-[#9D9F9F] hover:bg-[#7D7F7F]' : ''
                        }`}
                >
                    {channel.isSecondary ? (
                        <>
                            <Check className="w-4 h-4 mr-1" />
                            Secondary
                        </>
                    ) : (
                        'Add Secondary'
                    )}
                </Button>
            </div>
        </motion.div>
    );
}

export function ChannelHabitatMap({
    channels,
    onUpdateChannel,
    onTogglePrimary,
    onToggleSecondary,
    primaryCount,
    secondaryCount
}: ChannelHabitatMapProps) {
    // Generate default channels if empty
    const displayChannels: ChannelHabitatItem[] = channels.length > 0
        ? channels
        : Object.entries(CHANNEL_CONFIG).map(([platform, config], i) => ({
            id: `channel-${i}`,
            platform,
            contentTypes: config.defaultContentTypes,
            timingPattern: config.defaultTiming,
            confidenceScore: Math.floor(Math.random() * 40) + 50,
            isPrimary: false,
            isSecondary: false
        }));

    const canAddPrimary = primaryCount < 3;
    const canAddSecondary = secondaryCount < 2;

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-start gap-3 p-4 bg-[#F3F4EE] rounded-xl">
                <Globe className="w-5 h-5 text-[#2D3538] flex-shrink-0 mt-0.5" />
                <p className="text-sm text-[#5B5F61]">
                    <strong className="text-[#2D3538]">Channel Habitat Map</strong> — Where your ICP spends time
                    and what content works. Pick <strong>3 Primary</strong> and <strong>2 Secondary</strong> channels.
                </p>
            </div>

            {/* Selection Status */}
            <div className="flex gap-4">
                <div className={`flex-1 p-4 rounded-2xl ${primaryCount === 3 ? 'bg-[#2D3538]' : 'bg-[#F3F4EE]'
                    }`}>
                    <span className={`text-[10px] font-mono uppercase ${primaryCount === 3 ? 'text-white/60' : 'text-[#9D9F9F]'
                        }`}>
                        Primary Channels
                    </span>
                    <div className="flex items-center gap-2 mt-1">
                        <span className={`text-2xl font-mono ${primaryCount === 3 ? 'text-white' : 'text-[#2D3538]'
                            }`}>
                            {primaryCount}/3
                        </span>
                        {primaryCount === 3 && <Check className="w-5 h-5 text-white" />}
                    </div>
                </div>
                <div className={`flex-1 p-4 rounded-2xl ${secondaryCount === 2 ? 'bg-[#9D9F9F]' : 'bg-[#F3F4EE]'
                    }`}>
                    <span className={`text-[10px] font-mono uppercase ${secondaryCount === 2 ? 'text-white/60' : 'text-[#9D9F9F]'
                        }`}>
                        Secondary Channels
                    </span>
                    <div className="flex items-center gap-2 mt-1">
                        <span className={`text-2xl font-mono ${secondaryCount === 2 ? 'text-white' : 'text-[#2D3538]'
                            }`}>
                            {secondaryCount}/2
                        </span>
                        {secondaryCount === 2 && <Check className="w-5 h-5 text-white" />}
                    </div>
                </div>
            </div>

            {/* Channel Grid */}
            <div className="grid grid-cols-2 gap-4">
                {displayChannels.map((channel, index) => (
                    <ChannelCard
                        key={channel.id}
                        channel={channel}
                        config={CHANNEL_CONFIG[channel.platform] || CHANNEL_CONFIG['Email/Newsletter']}
                        onTogglePrimary={() => onTogglePrimary(channel.id)}
                        onToggleSecondary={() => onToggleSecondary(channel.id)}
                        canAddPrimary={canAddPrimary}
                        canAddSecondary={canAddSecondary}
                        index={index}
                    />
                ))}
            </div>
        </div>
    );
}
