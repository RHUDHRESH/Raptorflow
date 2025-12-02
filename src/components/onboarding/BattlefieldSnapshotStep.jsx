import React, { useState } from 'react';

const BattlefieldSnapshotStep = ({ analysis, onBack, onBlueprintReady }) => {
    const [userConfidence, setUserConfidence] = useState('spot_on');
    const [primaryFocus, setPrimaryFocus] = useState('revenue');
    const [isLoading, setIsLoading] = useState(false);

    // Helper to format timestamp
    const getTimeAgo = (timestamp) => {
        const seconds = Math.floor((new Date() - new Date(timestamp)) / 1000);
        if (seconds < 60) return 'a few seconds ago';
        if (seconds < 3600) return `${Math.floor(seconds / 60)} minutes ago`;
        return `${Math.floor(seconds / 3600)} hours ago`;
    };

    // Helper to get score label
    const getScoreLabel = (score) => {
        if (score < 0.4) return 'Early';
        if (score < 0.7) return 'Emerging';
        return 'Strong';
    };

    // Helper to get score color
    const getScoreColor = (score) => {
        if (score < 0.4) return 'bg-aubergine/20';
        if (score < 0.7) return 'bg-gold/30';
        return 'bg-gold/50';
    };

    const handleContinue = async () => {
        setIsLoading(true);

        try {
            console.log('Submitting positioning request:', {
                analysisId: analysis.analysisId,
                userConfidence,
                primaryFocus,
            });

            // Mock API call
            const response = await fetch('/api/onboarding/positioning', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    analysisId: analysis.analysisId,
                    userConfidence,
                    primaryFocus,
                }),
            });

            // Simulate network delay for demo
            await new Promise((resolve) => setTimeout(resolve, 3000));

            const data = { blueprintId: 'mock-blueprint-123' };
            console.log('Positioning blueprint ready:', data);

            // TODO: navigate to next step or call onBlueprintReady
            if (onBlueprintReady) {
                onBlueprintReady(data.blueprintId);
            }
        } catch (err) {
            console.error('Failed to generate positioning blueprint:', err);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen w-full bg-canvas text-charcoal font-sans flex flex-col lg:flex-row overflow-hidden">
            {/* Left Panel - Narrative */}
            <div className="w-full lg:w-1/2 p-8 lg:p-16 flex flex-col justify-center relative border-b lg:border-b-0 lg:border-r border-line">
                <div className="max-w-xl mx-auto lg:mx-0">
                    <div className="text-xs font-bold tracking-widest text-aubergine mb-6 uppercase">
                        Step 2 • Battlefield Snapshot
                    </div>

                    <h1 className="font-serif text-4xl lg:text-5xl leading-tight mb-6 text-charcoal">
                        Here's how your world looks from our vantage point.
                    </h1>

                    <div className="space-y-4 text-lg text-charcoal/80 leading-relaxed mb-8 font-light">
                        <p>
                            We've read your description and inferred where you sit in the market, who you serve, and where the critical gaps are.
                        </p>
                        <p>
                            This analysis will drive your positioning blueprint and your first 90-day plan. If something feels off, you can refine it in the next step.
                        </p>
                    </div>

                    <div className="flex items-center space-x-3 text-xs text-charcoal/50 font-medium">
                        <div className="h-px w-6 bg-line"></div>
                        <span>
                            Analysis generated {getTimeAgo(analysis.createdAt)} • Draft 1
                        </span>
                    </div>
                </div>
            </div>

            {/* Right Panel - Cards & Interaction */}
            <div className="w-full lg:w-1/2 bg-white/30 lg:bg-transparent p-8 lg:p-16 flex flex-col justify-start overflow-y-auto">
                <div className="w-full max-w-lg mx-auto space-y-6">
                    {/* Who You Are Card */}
                    <div className="bg-white border border-line p-6 shadow-sm">
                        <h3 className="text-sm font-bold uppercase tracking-wider text-charcoal/60 mb-4">
                            Who you are (according to us)
                        </h3>

                        <div className="space-y-3">
                            <div className="inline-block px-3 py-1 bg-aubergine/10 text-aubergine text-xs font-medium rounded-sm">
                                {analysis.summary.companyType}
                            </div>

                            <p className="text-base text-charcoal leading-relaxed">
                                {analysis.summary.productOrService}
                            </p>

                            <div className="pt-2">
                                <div className="text-xs font-bold uppercase tracking-wider text-charcoal/50 mb-1">
                                    Primary Audience
                                </div>
                                <p className="text-sm text-charcoal/80">
                                    {analysis.summary.primaryAudience}
                                </p>
                            </div>

                            <p className="text-xs text-charcoal/40 italic pt-2 border-t border-line/50 mt-4">
                                You can refine this in the next step.
                            </p>
                        </div>
                    </div>

                    {/* Diagnostics Card */}
                    <div className="bg-white border border-line p-6 shadow-sm">
                        <h3 className="text-sm font-bold uppercase tracking-wider text-charcoal/60 mb-4">
                            Clarity at a glance
                        </h3>

                        <div className="space-y-4">
                            {/* Positioning Uniqueness */}
                            <div>
                                <div className="flex items-center justify-between mb-2">
                                    <span className="text-sm text-charcoal">Positioning uniqueness</span>
                                    <span className="text-xs font-medium text-charcoal/60 px-2 py-0.5 bg-canvas rounded">
                                        {getScoreLabel(analysis.diagnostics.positioningUniqueness)}
                                    </span>
                                </div>
                                <div className="w-full h-2 bg-canvas rounded-full overflow-hidden">
                                    <div
                                        className={`h-full ${getScoreColor(analysis.diagnostics.positioningUniqueness)} transition-all duration-500`}
                                        style={{ width: `${analysis.diagnostics.positioningUniqueness * 100}%` }}
                                    ></div>
                                </div>
                            </div>

                            {/* ICP Clarity */}
                            <div>
                                <div className="flex items-center justify-between mb-2">
                                    <span className="text-sm text-charcoal">ICP clarity</span>
                                    <span className="text-xs font-medium text-charcoal/60 px-2 py-0.5 bg-canvas rounded">
                                        {getScoreLabel(analysis.diagnostics.icpClarity)}
                                    </span>
                                </div>
                                <div className="w-full h-2 bg-canvas rounded-full overflow-hidden">
                                    <div
                                        className={`h-full ${getScoreColor(analysis.diagnostics.icpClarity)} transition-all duration-500`}
                                        style={{ width: `${analysis.diagnostics.icpClarity * 100}%` }}
                                    ></div>
                                </div>
                            </div>

                            {/* Marketing Maturity */}
                            <div>
                                <div className="flex items-center justify-between mb-2">
                                    <span className="text-sm text-charcoal">Marketing maturity</span>
                                    <span className="text-xs font-medium text-charcoal/60 px-2 py-0.5 bg-canvas rounded">
                                        {getScoreLabel(analysis.diagnostics.marketingMaturity)}
                                    </span>
                                </div>
                                <div className="w-full h-2 bg-canvas rounded-full overflow-hidden">
                                    <div
                                        className={`h-full ${getScoreColor(analysis.diagnostics.marketingMaturity)} transition-all duration-500`}
                                        style={{ width: `${analysis.diagnostics.marketingMaturity * 100}%` }}
                                    ></div>
                                </div>
                            </div>
                        </div>

                        <p className="text-xs text-charcoal/40 italic pt-4 mt-4 border-t border-line/50">
                            These scores help us decide how aggressive your first 90 days can be.
                        </p>
                    </div>

                    {/* Risks & Openings Card */}
                    <div className="bg-white border border-line p-6 shadow-sm">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                            {/* Risks */}
                            <div>
                                <h4 className="text-xs font-bold uppercase tracking-wider text-charcoal/60 mb-3">
                                    Risks we see
                                </h4>
                                <ul className="space-y-2">
                                    {analysis.notes.positioningRisks.map((risk, idx) => (
                                        <li key={idx} className="text-sm text-charcoal/70 flex items-start">
                                            <span className="text-aubergine mr-2">•</span>
                                            <span>{risk}</span>
                                        </li>
                                    ))}
                                </ul>
                            </div>

                            {/* Openings */}
                            <div>
                                <h4 className="text-xs font-bold uppercase tracking-wider text-charcoal/60 mb-3">
                                    Openings you can exploit
                                </h4>
                                <ul className="space-y-2">
                                    {analysis.notes.obviousOpportunities.map((opp, idx) => (
                                        <li key={idx} className="text-sm text-charcoal/70 flex items-start">
                                            <span className="text-gold mr-2">•</span>
                                            <span>{opp}</span>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        </div>

                        <div className="pt-4 border-t border-line/50">
                            <p className="text-xs text-charcoal/50 mb-1">Biggest hidden competitor:</p>
                            <p className="text-sm font-medium text-aubergine">
                                {analysis.notes.statusQuoCompetitor}
                            </p>
                        </div>
                    </div>

                    {/* Interaction Section */}
                    {isLoading ? (
                        <div className="bg-white border border-line p-8 shadow-sm">
                            <div className="flex flex-col items-center justify-center space-y-6 animate-pulse">
                                <div className="text-gold text-xl font-serif italic">
                                    Drafting your positioning blueprint…
                                </div>
                                <div className="space-y-3 text-center">
                                    <div className="flex items-center space-x-2 text-sm text-charcoal/70">
                                        <span className="w-1.5 h-1.5 bg-aubergine rounded-full animate-bounce"></span>
                                        <span>Tightening your category and claim…</span>
                                    </div>
                                    <div className="flex items-center space-x-2 text-sm text-charcoal/70">
                                        <span className="w-1.5 h-1.5 bg-aubergine rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></span>
                                        <span>Aligning your ICP with your offer…</span>
                                    </div>
                                    <div className="flex items-center space-x-2 text-sm text-charcoal/70">
                                        <span className="w-1.5 h-1.5 bg-aubergine rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></span>
                                        <span>Planning how to flank competitors…</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="bg-white border border-line p-6 shadow-sm">
                            <h3 className="text-sm font-bold uppercase tracking-wider text-charcoal/60 mb-6">
                                Your call
                            </h3>

                            {/* Confidence Selector */}
                            <div className="mb-6">
                                <label className="block text-xs font-medium text-charcoal/70 mb-3">
                                    Does this feel roughly right?
                                </label>
                                <div className="flex flex-wrap gap-2">
                                    {[
                                        { value: 'spot_on', label: 'Spot on' },
                                        { value: 'mostly', label: 'Mostly' },
                                        { value: 'not_really', label: 'Not really' },
                                    ].map((option) => (
                                        <button
                                            key={option.value}
                                            onClick={() => setUserConfidence(option.value)}
                                            className={`px-4 py-2 text-sm font-medium transition-all ${userConfidence === option.value
                                                    ? 'bg-charcoal text-white'
                                                    : 'bg-canvas text-charcoal hover:bg-line'
                                                }`}
                                        >
                                            {option.label}
                                        </button>
                                    ))}
                                </div>
                            </div>

                            {/* Primary Focus Selector */}
                            <div className="mb-6">
                                <label className="block text-xs font-medium text-charcoal/70 mb-3">
                                    What matters most in the next 90 days?
                                </label>
                                <div className="flex flex-wrap gap-2">
                                    {[
                                        { value: 'revenue', label: 'Revenue' },
                                        { value: 'pipeline', label: 'Pipeline' },
                                        { value: 'retention', label: 'Retention' },
                                        { value: 'brand', label: 'Brand' },
                                    ].map((option) => (
                                        <button
                                            key={option.value}
                                            onClick={() => setPrimaryFocus(option.value)}
                                            className={`px-4 py-2 text-sm font-medium transition-all ${primaryFocus === option.value
                                                    ? 'bg-aubergine text-white'
                                                    : 'bg-canvas text-charcoal hover:bg-line'
                                                }`}
                                        >
                                            {option.label}
                                        </button>
                                    ))}
                                </div>
                            </div>

                            {/* Actions */}
                            <div className="flex items-center justify-between pt-4 border-t border-line/50">
                                {onBack ? (
                                    <button
                                        onClick={onBack}
                                        className="text-sm text-charcoal/50 hover:text-charcoal transition-colors"
                                    >
                                        Back
                                    </button>
                                ) : (
                                    <div></div>
                                )}

                                <button
                                    onClick={handleContinue}
                                    className="bg-charcoal text-white px-8 py-3 font-medium hover:bg-aubergine transition-colors duration-300 shadow-lg hover:shadow-xl"
                                >
                                    Continue to Positioning
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default BattlefieldSnapshotStep;
