import React, { useState } from 'react';

const OnboardingIntakeStep = () => {
    const [formData, setFormData] = useState({
        description: '',
        websiteUrl: '',
        geography: '',
        industry: '',
    });
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({ ...prev, [name]: value }));
        if (name === 'description' && value.trim() !== '') {
            setError('');
        }
    };

    const handleSubmit = async () => {
        if (!formData.description.trim()) {
            setError('Please tell us a little about your business to continue.');
            return;
        }

        setIsLoading(true);

        // Mock API call
        try {
            console.log('Submitting analysis request:', formData);

            // Simulate network delay
            await new Promise((resolve) => setTimeout(resolve, 3000));

            // Mock response
            const response = { status: 'success', message: 'Analysis complete' };
            console.log('API Response:', response);

            // TODO: pass analysis up to parent or navigate to insights step

        } catch (err) {
            console.error('Analysis failed:', err);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen w-full bg-canvas text-charcoal font-sans flex flex-col lg:flex-row overflow-hidden">
            {/* Left Side - Narrative */}
            <div className="w-full lg:w-1/2 p-8 lg:p-16 flex flex-col justify-center relative border-b lg:border-b-0 lg:border-r border-line">
                <div className="max-w-xl mx-auto lg:mx-0">
                    <div className="text-xs font-bold tracking-widest text-aubergine mb-6 uppercase">
                        Step 1 • Know Your Battlefield
                    </div>

                    <h1 className="font-serif text-4xl lg:text-5xl leading-tight mb-6 text-charcoal">
                        Let’s understand the world you’re fighting in.
                    </h1>

                    <p className="text-lg text-charcoal/80 leading-relaxed mb-8 font-light">
                        Describe your business and where you’re at today. We’ll use this to map your positioning, ICP, and opportunities – before we ever talk campaigns.
                    </p>

                    <div className="flex items-center space-x-3 text-sm text-aubergine/60 font-medium">
                        <div className="h-px w-8 bg-gold"></div>
                        <span>You’re 1 of 5 steps away from your first bespoke plan.</span>
                    </div>
                </div>
            </div>

            {/* Right Side - Intake Card */}
            <div className="w-full lg:w-1/2 bg-white/50 lg:bg-transparent p-8 lg:p-16 flex flex-col justify-center items-center">
                <div className="w-full max-w-lg bg-white border border-line p-8 lg:p-10 shadow-sm relative">

                    {isLoading ? (
                        <div className="flex flex-col items-center justify-center py-12 space-y-6 animate-pulse">
                            <div className="text-gold text-xl font-serif italic">Analyzing your battlefield…</div>
                            <div className="space-y-3 text-center">
                                <div className="flex items-center space-x-2 text-sm text-charcoal/70">
                                    <span className="w-1.5 h-1.5 bg-aubergine rounded-full animate-bounce"></span>
                                    <span>Scanning your market and category…</span>
                                </div>
                                <div className="flex items-center space-x-2 text-sm text-charcoal/70 delay-150">
                                    <span className="w-1.5 h-1.5 bg-aubergine rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></span>
                                    <span>Extracting your ICP and status quo competitor…</span>
                                </div>
                                <div className="flex items-center space-x-2 text-sm text-charcoal/70 delay-300">
                                    <span className="w-1.5 h-1.5 bg-aubergine rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></span>
                                    <span>Preparing your first positioning snapshot…</span>
                                </div>
                            </div>
                        </div>
                    ) : (
                        <>
                            <div className="mb-8">
                                <label htmlFor="description" className="block text-lg font-serif text-charcoal mb-3">
                                    Tell us about your business in your own words
                                </label>
                                <textarea
                                    id="description"
                                    name="description"
                                    value={formData.description}
                                    onChange={handleInputChange}
                                    placeholder="What do you sell? Who is it for? What’s working in your marketing, what isn’t?"
                                    className={`w-full h-40 p-4 bg-canvas/30 border ${error ? 'border-red-400' : 'border-line'} focus:border-gold focus:ring-1 focus:ring-gold outline-none resize-none transition-all text-charcoal placeholder:text-charcoal/40 font-sans text-base leading-relaxed`}
                                />
                                {error && <p className="text-red-500 text-xs mt-2">{error}</p>}
                            </div>

                            <div className="w-full h-px bg-line mb-8"></div>

                            <div className="space-y-6">
                                <div>
                                    <label htmlFor="websiteUrl" className="block text-xs font-bold uppercase tracking-wider text-charcoal/60 mb-2">
                                        Website URL <span className="font-normal normal-case text-charcoal/40">(Optional)</span>
                                    </label>
                                    <input
                                        type="text"
                                        id="websiteUrl"
                                        name="websiteUrl"
                                        value={formData.websiteUrl}
                                        onChange={handleInputChange}
                                        className="w-full p-3 bg-transparent border-b border-line focus:border-gold outline-none transition-colors text-charcoal"
                                        placeholder="raptorflow.com"
                                    />
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    <div>
                                        <label htmlFor="geography" className="block text-xs font-bold uppercase tracking-wider text-charcoal/60 mb-2">
                                            Primary Market
                                        </label>
                                        <input
                                            type="text"
                                            id="geography"
                                            name="geography"
                                            value={formData.geography}
                                            onChange={handleInputChange}
                                            className="w-full p-3 bg-transparent border-b border-line focus:border-gold outline-none transition-colors text-charcoal"
                                            placeholder="e.g. North America"
                                        />
                                    </div>
                                    <div>
                                        <label htmlFor="industry" className="block text-xs font-bold uppercase tracking-wider text-charcoal/60 mb-2">
                                            Industry
                                        </label>
                                        <input
                                            type="text"
                                            id="industry"
                                            name="industry"
                                            value={formData.industry}
                                            onChange={handleInputChange}
                                            className="w-full p-3 bg-transparent border-b border-line focus:border-gold outline-none transition-colors text-charcoal"
                                            placeholder="e.g. SaaS"
                                        />
                                    </div>
                                </div>
                            </div>

                            <div className="mt-8 flex items-center justify-between pt-6">
                                <button
                                    type="button"
                                    className="text-sm text-charcoal/50 hover:text-charcoal transition-colors"
                                    onClick={() => console.log('Skipped for now')}
                                >
                                    Skip for now
                                </button>

                                <div className="flex flex-col items-end">
                                    <p className="text-[10px] text-charcoal/40 mb-2 italic">
                                        You can keep it messy. RaptorFlow will clean it up.
                                    </p>
                                    <button
                                        onClick={handleSubmit}
                                        className="bg-charcoal text-white px-8 py-3 font-medium hover:bg-aubergine transition-colors duration-300 shadow-lg hover:shadow-xl"
                                    >
                                        Continue
                                    </button>
                                </div>
                            </div>
                        </>
                    )}
                </div>
            </div>
        </div>
    );
};

export default OnboardingIntakeStep;
