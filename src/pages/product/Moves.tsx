import React from 'react'
import { Helmet, HelmetProvider } from 'react-helmet-async'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowLeft, CheckCircle2, TrendingUp, Calendar, Target } from 'lucide-react'
import { BrandIcon } from '@/components/brand/BrandSystem'
import { MarketingLayout } from '@/components/MarketingLayout'

const Moves = () => {
    return (
        <HelmetProvider>
            <Helmet>
                <title>Moves - RaptorFlow</title>
                <meta name="description" content="Learn about Moves - tactical marketing actions tied to your campaigns." />
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
                                    <BrandIcon name="speed" className="w-7 h-7 text-primary" />
                                </div>
                                <div>
                                    <span className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Feature</span>
                                    <h1 className="font-serif text-3xl md:text-4xl font-medium text-foreground">
                                        Campaign & Moves
                                    </h1>
                                </div>
                            </div>

                            <p className="text-xl text-muted-foreground mb-12 leading-relaxed">
                                A Move is a single marketing action—a post, an email, an A/B test.
                                RaptorFlow helps you plan, generate, and track Moves tied to your campaigns.
                            </p>

                            <div className="grid md:grid-cols-2 gap-8 mb-12">
                                <div className="p-6 rounded-xl border border-border bg-card">
                                    <Calendar className="w-6 h-6 text-primary mb-4" />
                                    <h3 className="font-medium text-foreground mb-2">Daily execution</h3>
                                    <p className="text-sm text-muted-foreground">
                                        Each Move is scheduled and tracked. See what's due today, what's shipped, and what's next.
                                    </p>
                                </div>
                                <div className="p-6 rounded-xl border border-border bg-card">
                                    <Target className="w-6 h-6 text-primary mb-4" />
                                    <h3 className="font-medium text-foreground mb-2">Tied to KPIs</h3>
                                    <p className="text-sm text-muted-foreground">
                                        Every Move connects to a campaign goal. Track performance, not just output.
                                    </p>
                                </div>
                                <div className="p-6 rounded-xl border border-border bg-card">
                                    <TrendingUp className="w-6 h-6 text-primary mb-4" />
                                    <h3 className="font-medium text-foreground mb-2">Compound progress</h3>
                                    <p className="text-sm text-muted-foreground">
                                        Small daily actions stack. See your marketing velocity grow over time.
                                    </p>
                                </div>
                                <div className="p-6 rounded-xl border border-border bg-card">
                                    <CheckCircle2 className="w-6 h-6 text-primary mb-4" />
                                    <h3 className="font-medium text-foreground mb-2">Accountability</h3>
                                    <p className="text-sm text-muted-foreground">
                                        Weekly reviews show what worked and what didn't. Adjust and improve.
                                    </p>
                                </div>
                            </div>

                            <div className="flex gap-4">
                                <Link
                                    to="/signup"
                                    className="inline-flex items-center gap-2 px-6 py-3 bg-primary text-primary-foreground rounded-lg font-medium hover:opacity-90 transition-opacity"
                                >
                                    Start using Moves
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

export default Moves
