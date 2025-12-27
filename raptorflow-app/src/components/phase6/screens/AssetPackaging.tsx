'use client';

import React, { useState } from 'react';
import { ChannelAsset, WebsiteHeroPack, AdAngle, Signal7Soundbite, ChannelType } from '@/lib/foundation';
import { Copy, Globe, Linkedin, Megaphone, Mail, Presentation, Check } from 'lucide-react';
import { toast } from 'sonner';

interface Props {
    websiteHero: WebsiteHeroPack | undefined;
    adAngles: AdAngle[];
    channelAssets: ChannelAsset[];
    soundbites: Signal7Soundbite[];
    onUpdateHero: (hero: WebsiteHeroPack) => void;
    onUpdateAssets: (assets: ChannelAsset[]) => void;
}

const TABS: { channel: ChannelType | 'website'; icon: React.ReactNode; label: string }[] = [
    { channel: 'website', icon: <Globe className="w-4 h-4" />, label: 'Website Hero' },
    { channel: 'linkedin', icon: <Linkedin className="w-4 h-4" />, label: 'LinkedIn' },
    { channel: 'ads', icon: <Megaphone className="w-4 h-4" />, label: 'Ads' },
    { channel: 'email', icon: <Mail className="w-4 h-4" />, label: 'Cold Email' },
    { channel: 'deck', icon: <Presentation className="w-4 h-4" />, label: 'Deck' }
];

export function AssetPackaging({
    websiteHero,
    adAngles,
    channelAssets,
    soundbites,
    onUpdateHero,
    onUpdateAssets
}: Props) {
    const [activeTab, setActiveTab] = useState<ChannelType | 'website'>('website');
    const [copiedId, setCopiedId] = useState<string | null>(null);

    const copyToClipboard = (text: string, id: string) => {
        navigator.clipboard.writeText(text);
        setCopiedId(id);
        toast.success('Copied to clipboard');
        setTimeout(() => setCopiedId(null), 2000);
    };

    const getChannelAsset = (channel: ChannelType) => channelAssets.find(a => a.channel === channel);

    return (
        <div className="space-y-6">
            {/* Tabs */}
            <div className="flex gap-2 p-1 bg-[#F3F4EE] rounded-xl">
                {TABS.map(tab => (
                    <button
                        key={tab.channel}
                        onClick={() => setActiveTab(tab.channel)}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm transition-all ${activeTab === tab.channel
                                ? 'bg-white text-[#2D3538] shadow-sm'
                                : 'text-[#5B5F61] hover:text-[#2D3538]'
                            }`}
                    >
                        {tab.icon}
                        {tab.label}
                    </button>
                ))}
            </div>

            {/* Website Hero Tab */}
            {activeTab === 'website' && websiteHero && (
                <div className="space-y-4">
                    {/* Preview Card */}
                    <div className="bg-[#2D3538] rounded-3xl p-10 text-center">
                        <h1 className="font-serif text-[40px] text-white mb-4">
                            {websiteHero.headline}
                        </h1>
                        <p className="text-white/70 text-lg mb-6 max-w-lg mx-auto">
                            {websiteHero.subhead}
                        </p>
                        <div className="flex flex-wrap justify-center gap-4 mb-8">
                            {websiteHero.bullets.map((bullet, i) => (
                                <span key={i} className="flex items-center gap-2 text-white/80 text-sm">
                                    <Check className="w-4 h-4 text-white/60" />
                                    {bullet}
                                </span>
                            ))}
                        </div>
                        <button className="px-8 py-4 bg-white text-[#2D3538] rounded-xl font-medium">
                            {websiteHero.cta}
                        </button>
                        <p className="text-white/50 text-xs mt-4">{websiteHero.trustLine}</p>
                    </div>

                    {/* Editable Fields */}
                    <div className="grid grid-cols-2 gap-4">
                        <EditableField
                            label="Headline"
                            value={websiteHero.headline}
                            onChange={v => onUpdateHero({ ...websiteHero, headline: v })}
                            onCopy={() => copyToClipboard(websiteHero.headline, 'headline')}
                            copied={copiedId === 'headline'}
                        />
                        <EditableField
                            label="Subhead"
                            value={websiteHero.subhead}
                            onChange={v => onUpdateHero({ ...websiteHero, subhead: v })}
                            onCopy={() => copyToClipboard(websiteHero.subhead, 'subhead')}
                            copied={copiedId === 'subhead'}
                        />
                        <EditableField
                            label="CTA"
                            value={websiteHero.cta}
                            onChange={v => onUpdateHero({ ...websiteHero, cta: v })}
                            onCopy={() => copyToClipboard(websiteHero.cta, 'cta')}
                            copied={copiedId === 'cta'}
                        />
                        <EditableField
                            label="Trust Line"
                            value={websiteHero.trustLine}
                            onChange={v => onUpdateHero({ ...websiteHero, trustLine: v })}
                            onCopy={() => copyToClipboard(websiteHero.trustLine, 'trust')}
                            copied={copiedId === 'trust'}
                        />
                    </div>
                </div>
            )}

            {/* Ads Tab */}
            {activeTab === 'ads' && (
                <div className="space-y-4">
                    <span className="text-[11px] font-mono uppercase tracking-[0.15em] text-[#9D9F9F]">
                        6 Ad Angles
                    </span>
                    <div className="grid grid-cols-2 gap-4">
                        {adAngles.map((ad, i) => (
                            <div
                                key={ad.angle}
                                className="bg-white border border-[#E5E6E3] rounded-2xl p-6 group"
                            >
                                <span className="text-[10px] font-mono uppercase text-[#9D9F9F] block mb-2">
                                    {ad.angle.replace(/-/g, ' ')}
                                </span>
                                <p className="font-medium text-[#2D3538] mb-2">{ad.headline}</p>
                                <p className="text-sm text-[#5B5F61] line-clamp-2">{ad.body}</p>
                                <button
                                    onClick={() => copyToClipboard(`${ad.headline}\n\n${ad.body}`, `ad-${i}`)}
                                    className="mt-4 flex items-center gap-2 text-xs text-[#9D9F9F] opacity-0 group-hover:opacity-100 transition-opacity"
                                >
                                    {copiedId === `ad-${i}` ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                                    {copiedId === `ad-${i}` ? 'Copied!' : 'Copy'}
                                </button>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Email Tab */}
            {activeTab === 'email' && (
                <div className="space-y-4">
                    {getChannelAsset('email')?.variants.map((variant, i) => (
                        <div
                            key={variant.id}
                            className="bg-white border border-[#E5E6E3] rounded-2xl p-6 group"
                        >
                            <div className="flex items-center justify-between mb-4">
                                <span className="text-[10px] font-mono uppercase text-[#9D9F9F]">
                                    {variant.label}
                                </span>
                                <button
                                    onClick={() => copyToClipboard(
                                        `Subject: ${variant.content.subject}\n\n${variant.content.body}`,
                                        `email-${i}`
                                    )}
                                    className="flex items-center gap-2 text-xs text-[#9D9F9F] opacity-0 group-hover:opacity-100 transition-opacity"
                                >
                                    {copiedId === `email-${i}` ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                                </button>
                            </div>
                            <div className="space-y-3">
                                <div className="bg-[#FAFAF8] rounded-lg p-3">
                                    <span className="text-[10px] text-[#9D9F9F]">Subject:</span>
                                    <p className="text-sm text-[#2D3538] font-medium">{variant.content.subject}</p>
                                </div>
                                <div className="bg-[#FAFAF8] rounded-lg p-3">
                                    <span className="text-[10px] text-[#9D9F9F]">Body:</span>
                                    <p className="text-sm text-[#2D3538] whitespace-pre-wrap">{variant.content.body}</p>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* LinkedIn Tab */}
            {activeTab === 'linkedin' && (
                <div className="space-y-4">
                    {getChannelAsset('linkedin')?.variants.map((variant, i) => (
                        <div
                            key={variant.id}
                            className="bg-white border border-[#E5E6E3] rounded-2xl p-6 group"
                        >
                            <div className="flex items-center justify-between mb-4">
                                <span className="text-[10px] font-mono uppercase text-[#9D9F9F]">
                                    {variant.label}
                                </span>
                                <button
                                    onClick={() => copyToClipboard(
                                        `${variant.content.openingHook}\n\n${variant.content.body}\n\n${variant.content.cta}`,
                                        `linkedin-${i}`
                                    )}
                                    className="flex items-center gap-2 text-xs text-[#9D9F9F] opacity-0 group-hover:opacity-100 transition-opacity"
                                >
                                    {copiedId === `linkedin-${i}` ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                                </button>
                            </div>
                            <div className="bg-[#FAFAF8] rounded-lg p-4">
                                <p className="text-sm text-[#2D3538] whitespace-pre-wrap">
                                    <strong>{variant.content.openingHook}</strong>
                                    {'\n\n'}
                                    {variant.content.body}
                                    {'\n\n'}
                                    {variant.content.cta}
                                </p>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Deck Tab */}
            {activeTab === 'deck' && (
                <div className="space-y-4">
                    {getChannelAsset('deck')?.variants.map((variant, i) => (
                        <div
                            key={variant.id}
                            className="bg-[#2D3538] rounded-2xl p-10 text-center group"
                        >
                            <span className="text-[10px] font-mono uppercase text-white/50 block mb-4">
                                {variant.label}
                            </span>
                            <h2 className="font-serif text-[36px] text-white mb-2">
                                {variant.content.headline}
                            </h2>
                            <p className="text-white/70">
                                {variant.content.subhead}
                            </p>
                            <button
                                onClick={() => copyToClipboard(
                                    `${variant.content.headline}\n${variant.content.subhead}`,
                                    `deck-${i}`
                                )}
                                className="mt-6 flex items-center gap-2 text-xs text-white/50 mx-auto opacity-0 group-hover:opacity-100 transition-opacity"
                            >
                                {copiedId === `deck-${i}` ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                                {copiedId === `deck-${i}` ? 'Copied!' : 'Copy'}
                            </button>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

function EditableField({
    label,
    value,
    onChange,
    onCopy,
    copied
}: {
    label: string;
    value: string;
    onChange: (v: string) => void;
    onCopy: () => void;
    copied: boolean;
}) {
    return (
        <div className="bg-white border border-[#E5E6E3] rounded-xl p-4 group">
            <div className="flex items-center justify-between mb-2">
                <span className="text-[10px] font-mono uppercase text-[#9D9F9F]">{label}</span>
                <button
                    onClick={onCopy}
                    className="opacity-0 group-hover:opacity-100 transition-opacity"
                >
                    {copied ? <Check className="w-3 h-3 text-green-500" /> : <Copy className="w-3 h-3 text-[#9D9F9F]" />}
                </button>
            </div>
            <input
                type="text"
                value={value}
                onChange={e => onChange(e.target.value)}
                className="w-full bg-transparent text-[#2D3538] text-sm focus:outline-none"
            />
        </div>
    );
}
