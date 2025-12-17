import React from 'react'
import { Helmet, HelmetProvider } from 'react-helmet-async'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowLeft, BarChart3, Beaker, TrendingUp, Lightbulb } from 'lucide-react'
import { MarketingLayout } from '@/components/MarketingLayout'

const BlackBox = () => {
    return (
        <HelmetProvider>
            <Helmet>
                <title>Black Box Testing - RaptorFlow</title>
                <meta name="description" content="A/B test your marketing hooks, CTAs, and creatives automatically with Black Box." />
            </Helmet>
            <MarketingLayout>
                <section className="pt-16 pb-24 md:pt-24 md:pb-32">
                    <div className="container mx-auto px-6 max-w-4xl">
                        <Link
                            to="/"
                            className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground mb-8 transition-colors"
                        >
                            <ArrowLeft className="w-4 h-4" />
                            Back to home
                        </Link>

                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.5 }}
                        >
                            <div className="flex items-center gap-4 mb-6">
                                <div className="w-14 h-14 rounded-2xl bg-primary/10 flex items-center justify-center">
                                    <BarChart3 className="w-7 h-7 text-primary" />
                                </div>
                                <div>
                                    <span className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Feature</span>
                                    <h1 className="font-serif text-3xl md:text-4xl font-medium text-foreground">
                                        Black Box Testing
                                    </h1>
                                </div>
                            </div>

                            <p className="text-xl text-muted-foreground mb-12 leading-relaxed">
                                Black Box is our A/B testing engine. Test different hooks, CTAs, or creatives—measure
                                what works and get recommendations automatically. Data-driven marketing, simplified.
                            </p>

                            <div className="grid md:grid-cols-2 gap-8 mb-12">
                                <div className="p-6 rounded-xl border border-border bg-card">
                                    <Beaker className="w-6 h-6 text-primary mb-4" />
                                    <h3 className="font-medium text-foreground mb-2">Easy experiments</h3>
                                    <p className="text-sm text-muted-foreground">
                                        Set up A/B tests in seconds. Test headlines, images, CTAs, or entire campaigns.
                                    </p>
                                </div>
                                <div className="p-6 rounded-xl border border-border bg-card">
                                    <BarChart3 className="w-6 h-6 text-primary mb-4" />
                                    <h3 className="font-medium text-foreground mb-2">Clear results</h3>
                                    <p className="text-sm text-muted-foreground">
                                        See which variant wins. Statistical significance calculated automatically.
                                    </p>
                                </div>
                                <div className="p-6 rounded-xl border border-border bg-card">
                                    <TrendingUp className="w-6 h-6 text-primary mb-4" />
                                    <h3 className="font-medium text-foreground mb-2">Continuous improvement</h3>
                                    <p className="text-sm text-muted-foreground">
                                        Learn from every test. Build a library of what works for your audience.
                                    </p>
                                </div>
                                <div className="p-6 rounded-xl border border-border bg-card">
                                    <Lightbulb className="w-6 h-6 text-primary mb-4" />
                                    <h3 className="font-medium text-foreground mb-2">AI recommendations</h3>
                                    <p className="text-sm text-muted-foreground">
                                        Get suggestions for what to test next based on your past results.
                                    </p>
                                </div>
                            </div>

                            <div className="flex gap-4">
                                <Link
                                    to="/signup"
                                    className="inline-flex items-center gap-2 px-6 py-3 bg-primary text-primary-foreground rounded-lg font-medium hover:opacity-90 transition-opacity"
                                >
                                    Start testing
                                </Link>
                                <Link
                                    to="/#pricing"
                                    className="inline-flex items-center gap-2 px-6 py-3 border border-border bg-background rounded-lg font-medium hover:bg-muted transition-colors"
                                >
                                    View pricing
                                </Link>
                            </div>
                        </motion.div>
                    </div>
                </section>
            </MarketingLayout>
        </HelmetProvider>
    )
}

export default BlackBox
