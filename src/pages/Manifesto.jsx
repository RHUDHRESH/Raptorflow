import React from 'react'
import { motion } from 'framer-motion'
import { ArrowRight } from 'lucide-react'
import { Link } from 'react-router-dom'

/* ═══════════════════════════════════════════════════════════════════════════
   MANIFESTO - HIGH FASHION EDITORIAL DESIGN
   Philosophy page with minimal, sophisticated aesthetic
   ═══════════════════════════════════════════════════════════════════════════ */

const Section = ({ title, children }) => (
    <motion.section
        initial={{ opacity: 0, y: 16 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        className="mb-16"
    >
        <h3 className="text-headline text-primary mb-4">{title}</h3>
        <div className="text-lg text-muted-foreground leading-relaxed space-y-4">
            {children}
        </div>
    </motion.section>
)

const Blockquote = ({ children }) => (
    <motion.blockquote
        initial={{ opacity: 0, y: 16 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        className="my-16 p-8 bg-card border border-border/50"
    >
        <p className="text-2xl md:text-3xl text-foreground italic font-light leading-relaxed">
            "{children}"
        </p>
    </motion.blockquote>
)

const Manifesto = () => (
    <div className="min-h-screen bg-background">
        {/* Hero */}
        <section className="min-h-[70vh] flex items-center justify-center px-6">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
                className="text-center max-w-3xl"
            >
                <p className="text-caption text-muted-foreground mb-6">The Philosophy</p>
                <h1 className="text-display text-5xl md:text-7xl lg:text-8xl text-foreground mb-6">
                    Less,<br />
                    <span className="italic text-primary">but better.</span>
                </h1>
                <p className="text-xl text-muted-foreground">
                    The strategic discipline that separates legendary brands from noise.
                </p>
            </motion.div>
        </section>

        {/* Content */}
        <section className="max-w-3xl mx-auto px-6 py-24">
            <motion.p
                initial={{ opacity: 0, y: 16 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                className="text-xl text-foreground leading-relaxed mb-16"
            >
                Founders are drowning in advice. "Be everywhere." "Post daily." "Launch a podcast."
                "Run ads." The modern playbook is a recipe for burnout, not growth. It confuses
                motion with progress.
            </motion.p>

            <Blockquote>
                Strategy is not about what you do. It's about what you choose not to do.
            </Blockquote>

            <Section title="The Biological Limit">
                <p>
                    Your brain is not designed to hold 50 priorities. It can handle about three.
                    Yet, most project management tools let you add infinite tasks, infinite noise.
                </p>
                <p>
                    Raptorflow is built around biological constraints. We force you to pick 3-5 moves
                    for a 90-day cycle. Not because the software can't handle more, but because
                    <span className="text-primary"> you</span> can't.
                </p>
            </Section>

            <Section title="Deep Work vs. Shallow Work">
                <p>
                    Shallow work is answering emails, tweaking colors, or checking analytics for the
                    10th time. Deep work is writing the sales letter that changes your trajectory.
                </p>
                <p>
                    Our interface is minimal by design. No notifications. No "team activity" feeds.
                    Just you, your strategy, and the execution. A quiet room in a noisy world.
                </p>
            </Section>

            <Section title="The Myth of More">
                <p>
                    More channels. More content. More campaigns. The industry profits from your
                    exhaustion. We don't.
                </p>
                <p>
                    We believe in constraint. The brands that last aren't the ones that did everything—
                    they're the ones that did the right things with
                    <span className="text-primary"> relentless consistency</span>.
                </p>
            </Section>

            <Blockquote>
                The goal isn't to be busy. The goal is to be unmistakable.
            </Blockquote>

            {/* CTA */}
            <motion.div
                initial={{ opacity: 0, y: 16 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                className="text-center mt-24 pt-16 border-t border-border/30"
            >
                <h3 className="text-display text-3xl text-foreground mb-4">
                    Ready to build with intention?
                </h3>
                <p className="text-muted-foreground mb-8">
                    Join founders who've traded chaos for clarity.
                </p>
                <Link
                    to="/start"
                    className="inline-flex items-center gap-2 px-6 py-3 bg-foreground hover:bg-primary text-background text-caption transition-all"
                >
                    Get started
                    <ArrowRight className="w-4 h-4" />
                </Link>
            </motion.div>
        </section>
    </div>
)

export default Manifesto
