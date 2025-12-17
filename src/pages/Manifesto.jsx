import { motion } from 'framer-motion'
import { ArrowRight } from 'lucide-react'
import { Link } from 'react-router-dom'

import { MarketingLayout } from '@/components/MarketingLayout'

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
        <h3 className="font-serif text-headline-sm text-primary mb-4">{title}</h3>
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
    <MarketingLayout>
        <div>
            {/* Hero */}
            <section className="masthead">
                <div className="container-editorial">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
                        className="text-center max-w-3xl mx-auto"
                    >
                        <p className="text-editorial-caption mb-6">The Philosophy</p>
                        <h1 className="font-serif text-headline-xl md:text-[4.25rem] leading-[1.06] text-foreground mb-6">
                            Less,<br />
                            <span className="italic text-primary">but better.</span>
                        </h1>

                        <p className="text-body-lg text-muted-foreground">
                            The strategic discipline that separates legendary brands from noise.
                        </p>
                    </motion.div>
                </div>
            </section>

            {/* Content */}
            <section className="container-editorial py-16 md:py-24">
                <motion.p
                    initial={{ opacity: 0, y: 16 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    className="text-body-lg text-foreground leading-relaxed mb-16 max-w-[75ch]"
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
                    className="text-center mt-24 pt-16 border-t border-border"
                >
                    <h3 className="font-serif text-headline-sm text-foreground mb-4">
                        Ready to build with intention?
                    </h3>
                    <p className="text-muted-foreground mb-8">
                        Join founders who've traded chaos for clarity.
                    </p>
                    <Link
                        to="/start"
                        className="inline-flex items-center justify-center rounded-md bg-foreground px-5 py-3 text-sm font-medium text-background transition-editorial hover:opacity-95"
                    >
                        Get started
                        <ArrowRight className="ml-2 h-4 w-4" />
                    </Link>
                </motion.div>
            </section>
        </div>
    </MarketingLayout>
)

export default Manifesto
