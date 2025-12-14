import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Mail, Copy, Check, Twitter, Linkedin, Send } from 'lucide-react'

/* ═══════════════════════════════════════════════════════════════════════════
   CONTACT - HIGH FASHION EDITORIAL DESIGN
   Contact page with minimal, sophisticated aesthetic
   ═══════════════════════════════════════════════════════════════════════════ */

const SocialLink = ({ href, icon: Icon, label }) => (
    <a
        href={href}
        target="_blank"
        rel="noopener noreferrer"
        className="group flex items-center gap-3 p-4 bg-card border border-border/50 hover:border-primary/50 transition-all"
    >
        <Icon className="w-5 h-5 text-muted-foreground group-hover:text-primary transition-colors" strokeWidth={1.5} />
        <span className="text-foreground">{label}</span>
    </a>
)

const Contact = () => {
    const [copied, setCopied] = useState(false)
    const email = 'hello@raptorflow.com'

    const handleCopy = async () => {
        try {
            await navigator.clipboard.writeText(email)
            setCopied(true)
            setTimeout(() => setCopied(false), 2000)
        } catch (err) {
            console.error('Failed to copy:', err)
        }
    }

    return (
        <div className="min-h-screen bg-background">
            <div className="max-w-3xl mx-auto px-6 py-24 md:py-32">
                {/* Hero */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
                    className="text-center mb-16"
                >
                    <p className="text-caption text-muted-foreground mb-4">Contact</p>
                    <h1 className="text-display text-4xl md:text-6xl text-foreground mb-4">
                        Let's <span className="italic text-primary">talk</span>
                        </h1>

                    <p className="text-lg text-muted-foreground max-w-xl mx-auto">
                        Questions about Raptorflow? Want to partner? We'd love to hear from you.
                    </p>
                </motion.div>

                {/* Email Card */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="mb-12"
                >
                    <div className="p-8 bg-card border border-border/50">
                        <div className="flex items-center gap-4 mb-6">
                            <div className="w-12 h-12 border border-border/50 flex items-center justify-center">
                                <Mail className="w-5 h-5 text-primary" strokeWidth={1.5} />
                            </div>
                            <div>
                                <h3 className="text-headline text-foreground">Email us</h3>
                                <p className="text-caption text-muted-foreground">Best way to reach us</p>
                            </div>
                        </div>

                        <button
                            onClick={handleCopy}
                            className="w-full group flex items-center justify-between p-6 bg-secondary hover:bg-secondary/80 border border-border/50 hover:border-primary/50 transition-all"
                        >
                            <span className="text-2xl md:text-3xl font-light text-foreground">
                                {email}
                            </span>
                            <div className="w-10 h-10 border border-border/50 flex items-center justify-center group-hover:border-primary/50 transition-colors">
                                {copied ? (
                                    <Check className="w-5 h-5 text-green-500" strokeWidth={1.5} />
                                ) : (
                                    <Copy className="w-5 h-5 text-muted-foreground group-hover:text-primary transition-colors" strokeWidth={1.5} />
                                )}
                            </div>
                        </button>

                        <p className="text-caption text-muted-foreground mt-4">
                            We typically respond within 24 hours
                        </p>
                    </div>
                </motion.div>

                {/* Social Links */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="mb-12"
                >
                    <p className="text-caption text-muted-foreground mb-4">Find us on social</p>
                    <div className="grid grid-cols-2 gap-4">
                        <SocialLink href="https://twitter.com/raptorflow" icon={Twitter} label="Twitter" />
                        <SocialLink href="https://linkedin.com/company/raptorflow" icon={Linkedin} label="LinkedIn" />
                    </div>
                </motion.div>

                {/* Support Email */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.3 }}
                    className="text-center pt-8 border-t border-border/30"
                >
                    <p className="text-caption text-muted-foreground">
                        For support inquiries:{' '}
                        <a href="mailto:support@raptorflow.com" className="text-primary hover:underline">
                            support@raptorflow.com
                        </a>
                    </p>
                </motion.div>
            </div>
        </div>
    )
}

export default Contact
