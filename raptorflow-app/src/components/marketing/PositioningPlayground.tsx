'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';

interface DemoResult {
    positioning: string;
    tagline: string;
    icp: {
        title: string;
        painPoints: string[];
    };
    firstMoves: string[];
}

// Simulated AI generation based on input keywords
function generatePositioning(input: string): DemoResult {
    const lowerInput = input.toLowerCase();

    // Detect business type
    const isSaas = lowerInput.includes('saas') || lowerInput.includes('software') || lowerInput.includes('app') || lowerInput.includes('platform');
    const isAgency = lowerInput.includes('agency') || lowerInput.includes('consulting') || lowerInput.includes('service');
    const isEcommerce = lowerInput.includes('ecommerce') || lowerInput.includes('shop') || lowerInput.includes('store') || lowerInput.includes('product');
    const isB2B = lowerInput.includes('b2b') || lowerInput.includes('business') || lowerInput.includes('enterprise');

    // Detect pain points
    const hasGrowth = lowerInput.includes('grow') || lowerInput.includes('scale') || lowerInput.includes('revenue');
    const hasTime = lowerInput.includes('time') || lowerInput.includes('busy') || lowerInput.includes('overwhelm');
    const hasClarity = lowerInput.includes('confus') || lowerInput.includes('unclear') || lowerInput.includes('messy');

    // Generate positioning based on detected patterns
    let positioning = '';
    let tagline = '';
    let icpTitle = '';
    let painPoints: string[] = [];
    let moves: string[] = [];

    if (isSaas) {
        positioning = 'The command center for SaaS founders who ship products but struggle to ship marketing. Turn technical excellence into market dominance.';
        tagline = 'Build products. Ship marketing. Scale faster.';
        icpTitle = 'Technical Founder / Product-First CEO';
        painPoints = ['Great product, weak positioning', 'Know how to code but not how to communicate value', 'Random content that does not convert'];
        moves = [
            'Define your "Only We Can" positioning statement',
            'Create ICP based on best existing customers',
            'Write a LinkedIn thought leadership thread on your unique insight',
        ];
    } else if (isAgency) {
        positioning = 'The growth engine for boutique agencies drowning in client work but starving for their own leads. Practice what you preach.';
        tagline = 'Serve clients. Market yourself. Grow predictably.';
        icpTitle = 'Agency Owner / Consulting Partner';
        painPoints = ['Too busy with deliverables to market yourself', 'Feast-or-famine pipeline', 'No time for your own content'];
        moves = [
            'Package your methodology into a repeatable framework',
            'Create a "Why Agencies Fail" contrarian content piece',
            'Build an ICP for your dream client profile',
        ];
    } else if (isEcommerce) {
        positioning = 'The marketing hub for DTC brands competing on story, not just price. Turn products into movements.';
        tagline = 'Great products deserve great stories.';
        icpTitle = 'DTC Brand Founder / E-commerce Operator';
        painPoints = ['Competing on price instead of brand', 'Paid ads eating margins', 'No organic content engine'];
        moves = [
            'Define your brand story and origin myth',
            'Create customer persona beyond demographics',
            'Launch a weekly content series on product behind-the-scenes',
        ];
    } else if (isB2B) {
        positioning = 'The marketing system for B2B founders selling to buyers who need to be educated, not entertained. Complex sales made simple.';
        tagline = 'Educate buyers. Close deals. Build pipeline.';
        icpTitle = 'B2B Founder / Enterprise Sales Leader';
        painPoints = ['Long sales cycles with no content support', 'Complex product hard to explain', 'Sales team has no marketing air cover'];
        moves = [
            'Create a buyer education sequence for your sales cycle',
            'Define your competitive positioning map',
            'Build a case study from your best customer win',
        ];
    } else {
        // Generic
        positioning = 'The marketing operating system for founders who know their product is great but struggle to communicate why anyone should care.';
        tagline = 'Stop explaining. Start connecting.';
        icpTitle = 'Growth-Stage Founder';
        painPoints = ['Unclear positioning', 'Inconsistent content', 'No marketing system'];
        moves = [
            'Extract your positioning from customer conversations',
            'Define your ideal customer profile with behavioral data',
            'Create your first 90-day content campaign',
        ];
    }

    // Add context based on specific pain points mentioned
    if (hasTime) {
        painPoints.push('No time for marketing');
        moves[0] = 'Set up your Foundation in 10 minutes (not 10 meetings)';
    }
    if (hasClarity) {
        painPoints.push('Messaging confusion');
        moves.push('Get your positioning statement crystal clear');
    }
    if (hasGrowth) {
        painPoints.push('Stalled growth');
        moves.push('Identify your highest-leverage marketing channel');
    }

    return {
        positioning,
        tagline,
        icp: {
            title: icpTitle,
            painPoints: painPoints.slice(0, 4),
        },
        firstMoves: moves.slice(0, 3),
    };
}

export function PositioningPlayground() {
    const [input, setInput] = useState('');
    const [isGenerating, setIsGenerating] = useState(false);
    const [result, setResult] = useState<DemoResult | null>(null);

    const handleGenerate = async () => {
        if (!input.trim()) return;

        setIsGenerating(true);

        // Simulate AI processing time
        await new Promise((resolve) => setTimeout(resolve, 1500));

        const generated = generatePositioning(input);
        setResult(generated);
        setIsGenerating(false);
    };

    const handleReset = () => {
        setInput('');
        setResult(null);
    };

    return (
        <div className="w-full max-w-3xl mx-auto">
            {!result ? (
                <div className="space-y-6">
                    {/* Input */}
                    <div>
                        <label className="block text-sm font-medium mb-3 text-center">
                            Describe your business in 2-3 sentences
                        </label>
                        <textarea
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Example: I run a B2B SaaS that helps sales teams automate outreach. We have a great product but struggle to explain why we are different from competitors. Growing slowly despite good retention."
                            rows={4}
                            className="w-full rounded-xl border border-border bg-card px-4 py-3 text-base placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-foreground/20 resize-none"
                        />
                    </div>

                    {/* Generate Button */}
                    <div className="text-center">
                        <Button
                            size="lg"
                            className="h-14 px-8 text-base rounded-xl min-w-[200px]"
                            onClick={handleGenerate}
                            disabled={!input.trim() || isGenerating}
                        >
                            {isGenerating ? (
                                <span className="flex items-center gap-2">
                                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24" fill="none">
                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                                    </svg>
                                    Analyzing...
                                </span>
                            ) : (
                                'Generate My Positioning →'
                            )}
                        </Button>
                    </div>

                    <p className="text-center text-sm text-muted-foreground">
                        Free instant analysis. No signup required.
                    </p>
                </div>
            ) : (
                <div className="space-y-6">
                    {/* Positioning Statement */}
                    <div className="rounded-2xl border-2 border-foreground bg-card p-6">
                        <div className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-3">
                            Your Positioning Statement
                        </div>
                        <p className="font-display text-xl lg:text-2xl font-medium leading-relaxed">
                            {result.positioning}
                        </p>
                        <div className="mt-4 pt-4 border-t border-border">
                            <div className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-2">
                                Tagline
                            </div>
                            <p className="text-lg font-medium text-foreground/80">{result.tagline}</p>
                        </div>
                    </div>

                    {/* ICP Preview */}
                    <div className="rounded-xl border border-border bg-card p-6">
                        <div className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-3">
                            Ideal Customer Profile
                        </div>
                        <h4 className="font-semibold text-lg mb-3">{result.icp.title}</h4>
                        <div className="flex flex-wrap gap-2">
                            {result.icp.painPoints.map((pain) => (
                                <span
                                    key={pain}
                                    className="px-3 py-1 rounded-full bg-muted text-sm"
                                >
                                    {pain}
                                </span>
                            ))}
                        </div>
                    </div>

                    {/* First Moves */}
                    <div className="rounded-xl border border-border bg-card p-6">
                        <div className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-3">
                            Your First 3 Moves
                        </div>
                        <ul className="space-y-3">
                            {result.firstMoves.map((move, index) => (
                                <li key={index} className="flex items-start gap-3">
                                    <div className="h-6 w-6 rounded-full bg-foreground text-background flex items-center justify-center flex-shrink-0 font-mono text-sm font-bold">
                                        {index + 1}
                                    </div>
                                    <span className="text-foreground/90">{move}</span>
                                </li>
                            ))}
                        </ul>
                    </div>

                    {/* CTAs */}
                    <div className="flex flex-col sm:flex-row gap-4 pt-4">
                        <Button size="lg" className="h-14 px-8 text-base rounded-xl flex-1">
                            Execute This Plan — Start Free
                        </Button>
                        <Button variant="outline" size="lg" className="h-14 px-8 text-base rounded-xl" onClick={handleReset}>
                            Try Another
                        </Button>
                    </div>
                </div>
            )}
        </div>
    );
}
