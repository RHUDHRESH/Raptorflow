'use client';

import Link from 'next/link';
import { MarketingLayout } from '@/components/marketing/MarketingLayout';
import { Button } from '@/components/ui/button';

export default function AboutPage() {
    return (
        <MarketingLayout>
            {/* Hero */}
            <section className="py-24 lg:py-32">
                <div className="mx-auto max-w-7xl px-6 lg:px-8">
                    <div className="mx-auto max-w-3xl text-center">
                        <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-4">
                            About RaptorFlow
                        </p>
                        <h1 className="font-display text-5xl lg:text-6xl font-medium tracking-tight mb-6">
                            We exist to kill confusion.
                        </h1>
                        <p className="text-lg lg:text-xl text-muted-foreground leading-relaxed">
                            Because the confused mind defaults to &quot;no.&quot;
                        </p>
                    </div>
                </div>
            </section>

            {/* Manifesto */}
            <section className="border-y border-border bg-muted/30 py-16 lg:py-24">
                <div className="mx-auto max-w-7xl px-6 lg:px-8">
                    <div className="mx-auto max-w-3xl">
                        <h2 className="font-display text-3xl lg:text-4xl font-medium mb-8">The Manifesto</h2>
                        <div className="prose prose-lg text-muted-foreground space-y-6">
                            <p className="text-foreground text-xl font-medium">
                                Good businesses should not lose to louder, uglier, better-funded competitors just because their marketing is chaotic and unclear.
                            </p>
                            <p>
                                But that is exactly what happens. Every day.
                            </p>
                            <p>
                                Founders with great products stare at blank screens wondering what to post. They try ChatGPT, then Notion, then Hootsuite, then give up. They hire an agency, burn three months of runway, and end up with &quot;content&quot; that sounds like everyone else.
                            </p>
                            <p>
                                Marketing by vibes. Strategy by accident. Execution by hope.
                            </p>
                            <p>
                                We have been there. We built products, raised money, hired teams—and still could not crack marketing. It felt like a swamp: fragmented tools, random tactics, inconsistent execution, no feedback loop.
                            </p>
                            <p className="text-foreground font-medium">
                                So we built RaptorFlow.
                            </p>
                            <p>
                                Not another tool. A system. A complete marketing operating system that turns messy context into clear positioning, clear positioning into 90-day war plans, and war plans into weekly execution that actually ships.
                            </p>
                            <p>
                                <strong>Clarify.</strong> We pull the strategy out of your head—ICP, positioning, proof, voice.
                            </p>
                            <p>
                                <strong>Build.</strong> AI generates campaigns and assets that connect to your Foundation.
                            </p>
                            <p>
                                <strong>Run.</strong> Weekly Moves ship. Experiments prove what works. Results compound.
                            </p>
                            <p className="text-foreground text-xl font-medium">
                                You stop &quot;trying marketing&quot; and start running a marketing machine.
                            </p>
                        </div>
                    </div>
                </div>
            </section>

            {/* Why */}
            <section className="py-24 lg:py-32">
                <div className="mx-auto max-w-7xl px-6 lg:px-8">
                    <div className="mx-auto max-w-3xl">
                        <h2 className="font-display text-3xl lg:text-4xl font-medium mb-12">Why We Built This</h2>

                        <div className="grid gap-8">
                            {[
                                {
                                    title: 'Marketing without a system is just gambling.',
                                    description: 'Random posts. Random channels. Random timing. And somehow expecting consistent results.',
                                },
                                {
                                    title: 'The confused mind defaults to "no."',
                                    description: 'If your prospects cannot immediately understand what you do and why it matters, they leave. And they never come back.',
                                },
                                {
                                    title: 'Tools do not solve the strategy problem.',
                                    description: 'Scheduling 100 posts does not help if you do not know what to say. AI generation does not help if it is not connected to your positioning.',
                                },
                                {
                                    title: 'Founders need operations, not inspiration.',
                                    description: 'You do not need more "content ideas." You need a system that tells you exactly what to do, every week, forever.',
                                },
                            ].map((item) => (
                                <div key={item.title} className="border-l-2 border-foreground pl-6">
                                    <h3 className="text-xl font-semibold mb-2">{item.title}</h3>
                                    <p className="text-muted-foreground">{item.description}</p>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </section>

            {/* Core Beliefs */}
            <section className="border-y border-border bg-muted/30 py-16 lg:py-24">
                <div className="mx-auto max-w-7xl px-6 lg:px-8">
                    <div className="mx-auto max-w-3xl">
                        <h2 className="font-display text-3xl lg:text-4xl font-medium mb-12">What We Believe</h2>

                        <div className="grid gap-6">
                            {[
                                'Clarity beats cleverness. Every time.',
                                'Strategy without execution is hallucination.',
                                'Marketing should compound, not reset every Monday.',
                                'One system beats five tools.',
                                'If you cannot prove it works, it does not work.',
                                'The customer is the hero. You are the guide.',
                            ].map((belief, index) => (
                                <div key={index} className="flex items-center gap-4">
                                    <div className="h-8 w-8 rounded-full bg-foreground flex items-center justify-center flex-shrink-0">
                                        <span className="text-background font-mono text-sm">{index + 1}</span>
                                    </div>
                                    <span className="text-lg">{belief}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </section>

            {/* CTA */}
            <section className="py-24 lg:py-32">
                <div className="mx-auto max-w-7xl px-6 lg:px-8">
                    <div className="mx-auto max-w-2xl text-center">
                        <h2 className="font-display text-4xl lg:text-5xl font-medium mb-6">
                            Ready to run your marketing machine?
                        </h2>
                        <p className="text-lg text-muted-foreground mb-10">
                            Give us your messy context. We will turn it into a plan you can actually execute.
                        </p>
                        <Button asChild size="lg" className="h-14 px-8 text-base rounded-xl">
                            <Link href="/foundation">Get Started Free</Link>
                        </Button>
                    </div>
                </div>
            </section>
        </MarketingLayout>
    );
}
