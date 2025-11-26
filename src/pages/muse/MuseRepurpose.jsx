import React, { useState } from "react";
import { Link } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import {
    Upload,
    Link as LinkIcon,
    FileText,
    Video,
    Mic,
    Sparkles,
    ArrowRight,
    X,
    Check,
    Copy,
    Download,
    RefreshCw
} from "lucide-react";
import { MuseHeader } from "./components/MuseHeader";
import { cn } from "../../utils/cn";

const CONTENT_TYPES = [
    { id: 'url', label: 'URL', icon: LinkIcon, placeholder: 'https://example.com/blog-post' },
    { id: 'text', label: 'Text', icon: FileText, placeholder: 'Paste your content here...' },
    { id: 'video', label: 'Video', icon: Video, placeholder: 'Upload or paste video URL' },
    { id: 'audio', label: 'Audio', icon: Mic, placeholder: 'Upload or paste audio URL' },
];

const OUTPUT_FORMATS = [
    { id: 'twitter', label: 'Twitter Thread', count: '5-10 tweets' },
    { id: 'linkedin', label: 'LinkedIn Post', count: '1 post' },
    { id: 'instagram', label: 'Instagram Carousel', count: '5-10 slides' },
    { id: 'email', label: 'Email Newsletter', count: '1 email' },
    { id: 'blog', label: 'Blog Post', count: '1 article' },
    { id: 'shorts', label: 'Video Script', count: '60s script' },
];

export default function MuseRepurpose() {
    const [week, setWeek] = useState("Week 42");
    const [brand, setBrand] = useState("RaptorFlow");
    const [activeType, setActiveType] = useState('url');
    const [inputContent, setInputContent] = useState('');
    const [selectedFormats, setSelectedFormats] = useState([]);
    const [isGenerating, setIsGenerating] = useState(false);
    const [generatedContent, setGeneratedContent] = useState(null);

    const handleGenerate = () => {
        if (!inputContent || selectedFormats.length === 0) return;

        setIsGenerating(true);
        // Simulate AI generation
        setTimeout(() => {
            setGeneratedContent({
                twitter: "🚀 Thread on Strategic Marketing...\n\n1/ Your marketing isn't broken. Your strategy is.\n\n2/ Most teams jump straight to tactics...",
                linkedin: "Strategic Marketing in 2024\n\nAfter working with 100+ companies, I've noticed a pattern...",
                instagram: "Slide 1: Strategic Marketing 101\nSlide 2: The Problem\nSlide 3: The Solution...",
            });
            setIsGenerating(false);
        }, 2000);
    };

    const toggleFormat = (formatId) => {
        setSelectedFormats(prev =>
            prev.includes(formatId)
                ? prev.filter(id => id !== formatId)
                : [...prev, formatId]
        );
    };

    return (
        <div className="min-h-screen bg-[#FAFAFA]">
            <MuseHeader
                week={week} setWeek={setWeek}
                brand={brand} setBrand={setBrand}
                modelRoute="GPT-4o"
                title="Repurpose Studio"
                subtitle="Transform long-form content into multi-platform assets"
            />

            <div className="max-w-7xl mx-auto px-6 py-8">
                {/* Navigation Tabs */}
                <div className="flex items-center gap-1 rounded-full bg-white p-1 shadow-sm border border-black/5 w-fit mb-8">
                    <Link to="/muse" className="rounded-full px-5 py-2 text-sm font-medium text-neutral-600 hover:bg-neutral-50 hover:text-neutral-900 transition-colors">Muse Home</Link>
                    <Link to="/muse/workspace" className="rounded-full px-5 py-2 text-sm font-medium text-neutral-600 hover:bg-neutral-50 hover:text-neutral-900 transition-colors">Draft Workspace</Link>
                    <Link to="/muse/repurpose" className="rounded-full bg-black px-5 py-2 text-sm font-medium text-white shadow-sm">Repurpose Studio</Link>
                    <Link to="/muse/hooks" className="rounded-full px-5 py-2 text-sm font-medium text-neutral-600 hover:bg-neutral-50 hover:text-neutral-900 transition-colors">Hooks Lab</Link>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* Left: Input */}
                    <div className="space-y-6">
                        <div className="bg-white rounded-2xl border border-neutral-200 p-6 shadow-sm">
                            <h2 className="font-serif text-2xl text-neutral-900 mb-6">Source Content</h2>

                            {/* Content Type Selector */}
                            <div className="flex gap-2 mb-6">
                                {CONTENT_TYPES.map(type => {
                                    const Icon = type.icon;
                                    return (
                                        <button
                                            key={type.id}
                                            onClick={() => setActiveType(type.id)}
                                            className={cn(
                                                "flex items-center gap-2 px-4 py-2 rounded-lg border-2 transition-all",
                                                activeType === type.id
                                                    ? "border-neutral-900 bg-neutral-900 text-white"
                                                    : "border-neutral-200 text-neutral-600 hover:border-neutral-400"
                                            )}
                                        >
                                            <Icon className="w-4 h-4" />
                                            <span className="text-sm font-medium">{type.label}</span>
                                        </button>
                                    );
                                })}
                            </div>

                            {/* Input Area */}
                            <div className="space-y-4">
                                {activeType === 'text' ? (
                                    <textarea
                                        value={inputContent}
                                        onChange={(e) => setInputContent(e.target.value)}
                                        placeholder={CONTENT_TYPES.find(t => t.id === activeType)?.placeholder}
                                        className="w-full h-64 p-4 border-2 border-neutral-200 rounded-lg focus:border-neutral-900 focus:outline-none resize-none font-sans text-sm"
                                    />
                                ) : (
                                    <input
                                        type="text"
                                        value={inputContent}
                                        onChange={(e) => setInputContent(e.target.value)}
                                        placeholder={CONTENT_TYPES.find(t => t.id === activeType)?.placeholder}
                                        className="w-full p-4 border-2 border-neutral-200 rounded-lg focus:border-neutral-900 focus:outline-none font-sans text-sm"
                                    />
                                )}
                            </div>
                        </div>

                        {/* Output Formats */}
                        <div className="bg-white rounded-2xl border border-neutral-200 p-6 shadow-sm">
                            <h2 className="font-serif text-2xl text-neutral-900 mb-6">Output Formats</h2>
                            <div className="grid grid-cols-2 gap-3">
                                {OUTPUT_FORMATS.map(format => (
                                    <button
                                        key={format.id}
                                        onClick={() => toggleFormat(format.id)}
                                        className={cn(
                                            "p-4 rounded-lg border-2 text-left transition-all",
                                            selectedFormats.includes(format.id)
                                                ? "border-neutral-900 bg-neutral-50"
                                                : "border-neutral-200 hover:border-neutral-400"
                                        )}
                                    >
                                        <div className="flex items-start justify-between mb-2">
                                            <span className="font-medium text-sm text-neutral-900">{format.label}</span>
                                            {selectedFormats.includes(format.id) && (
                                                <Check className="w-4 h-4 text-neutral-900" />
                                            )}
                                        </div>
                                        <span className="text-xs text-neutral-500">{format.count}</span>
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Generate Button */}
                        <button
                            onClick={handleGenerate}
                            disabled={!inputContent || selectedFormats.length === 0 || isGenerating}
                            className="w-full flex items-center justify-center gap-2 bg-neutral-900 text-white px-6 py-4 rounded-lg font-medium hover:bg-neutral-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                        >
                            {isGenerating ? (
                                <>
                                    <RefreshCw className="w-5 h-5 animate-spin" />
                                    Generating...
                                </>
                            ) : (
                                <>
                                    <Sparkles className="w-5 h-5" />
                                    Generate Assets
                                    <ArrowRight className="w-5 h-5" />
                                </>
                            )}
                        </button>
                    </div>

                    {/* Right: Output */}
                    <div className="bg-white rounded-2xl border border-neutral-200 p-6 shadow-sm">
                        <h2 className="font-serif text-2xl text-neutral-900 mb-6">Generated Assets</h2>

                        {!generatedContent ? (
                            <div className="flex flex-col items-center justify-center h-96 text-center">
                                <div className="w-16 h-16 rounded-full bg-neutral-100 flex items-center justify-center mb-4">
                                    <Sparkles className="w-8 h-8 text-neutral-400" />
                                </div>
                                <h3 className="font-serif text-xl text-neutral-900 mb-2">No Assets Yet</h3>
                                <p className="text-sm text-neutral-600 max-w-sm">
                                    Add your source content and select output formats to generate assets
                                </p>
                            </div>
                        ) : (
                            <div className="space-y-4">
                                {selectedFormats.map(formatId => {
                                    const format = OUTPUT_FORMATS.find(f => f.id === formatId);
                                    return (
                                        <motion.div
                                            key={formatId}
                                            initial={{ opacity: 0, y: 20 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            className="p-4 border border-neutral-200 rounded-lg"
                                        >
                                            <div className="flex items-center justify-between mb-3">
                                                <h3 className="font-medium text-neutral-900">{format.label}</h3>
                                                <div className="flex gap-2">
                                                    <button className="p-2 hover:bg-neutral-100 rounded-lg transition-colors">
                                                        <Copy className="w-4 h-4 text-neutral-600" />
                                                    </button>
                                                    <button className="p-2 hover:bg-neutral-100 rounded-lg transition-colors">
                                                        <Download className="w-4 h-4 text-neutral-600" />
                                                    </button>
                                                </div>
                                            </div>
                                            <div className="text-sm text-neutral-700 font-mono bg-neutral-50 p-3 rounded whitespace-pre-wrap">
                                                {generatedContent[formatId] || "Content generated..."}
                                            </div>
                                        </motion.div>
                                    );
                                })}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
