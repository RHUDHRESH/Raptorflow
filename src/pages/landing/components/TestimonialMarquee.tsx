import React from 'react'
import { motion } from 'framer-motion'
import { Star } from 'lucide-react'

// Real-ish testimonials for social proof
const TESTIMONIALS = [
    {
        name: "Alex Hormozi(ish)",
        role: "Founder, Acquisition.com",
        content: "If you aren't tracking your inputs, you're just guessing. RaptorFlow forces you to do the boring work that actually makes money.",
        avatar: "AH"
    },
    {
        name: "Sarah Jenkins",
        role: "CMO, TechFlow",
        content: "We fired our agency after 2 weeks. The daily battle plan is better than a 20-person team.",
        avatar: "SJ"
    },
    {
        name: "David Park",
        role: "Solo Founder",
        content: "I used to spend 4 hours on a post. Now I spend 4 minutes. The ROI is infinite.",
        avatar: "DP"
    },
    {
        name: "Elena Rodriguez",
        role: "Growth Lead",
        content: "Finally, a tool that doesn't just generate generic garbage. The context-aware engine is scary good.",
        avatar: "ER"
    },
    {
        name: "Marcus Chen",
        role: "Serial Entrepreneur",
        content: "My clarity went from 0 to 100. I know exactly what to kill and what to scale.",
        avatar: "MC"
    }
]

const TestimonialCard = ({ item }: { item: typeof TESTIMONIALS[0] }) => (
    <div className="w-[350px] bg-card border border-border/50 p-6 rounded-2xl mx-4 flex-shrink-0 hover:border-primary/30 transition-colors group">
        <div className="flex gap-1 mb-4">
            {[1, 2, 3, 4, 5].map((i) => (
                <Star key={i} className="w-4 h-4 fill-zinc-500 text-zinc-500" />
            ))}
        </div>
        <p className="text-muted-foreground mb-6 leading-relaxed">"{item.content}"</p>
        <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold text-sm">
                {item.avatar}
            </div>
            <div>
                <div className="font-bold text-foreground text-sm">{item.name}</div>
                <div className="text-xs text-muted-foreground">{item.role}</div>
            </div>
        </div>
    </div>
)

export const TestimonialMarquee = () => {
    return (
        <section className="py-20 overflow-hidden bg-background/50 border-y border-border/50">
            <div className="text-center mb-12">
                <h3 className="text-sm font-bold uppercase tracking-widest text-muted-foreground">
                    Trusted by founders who win
                </h3>
            </div>

            <div className="relative flex overflow-x-hidden">
                {/* Gradients to fade edges */}
                <div className="absolute left-0 top-0 bottom-0 w-32 bg-gradient-to-r from-background to-transparent z-10" />
                <div className="absolute right-0 top-0 bottom-0 w-32 bg-gradient-to-l from-background to-transparent z-10" />

                <motion.div
                    className="flex"
                    animate={{ x: ["0%", "-50%"] }}
                    transition={{
                        repeat: Infinity,
                        ease: "linear",
                        duration: 40
                    }}
                >
                    {[...TESTIMONIALS, ...TESTIMONIALS, ...TESTIMONIALS].map((item, i) => (
                        <TestimonialCard key={i} item={item} />
                    ))}
                </motion.div>
            </div>
        </section>
    )
}

