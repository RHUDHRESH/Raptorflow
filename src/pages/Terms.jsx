import React from 'react'
import { motion } from 'framer-motion'
import { FileText } from 'lucide-react'

/* ═══════════════════════════════════════════════════════════════════════════
   TERMS - HIGH FASHION EDITORIAL DESIGN
   Legal page with minimal, sophisticated aesthetic
   ═══════════════════════════════════════════════════════════════════════════ */

const sections = [
    { title: '1. Acceptance of Terms', content: ['By accessing Raptorflow, you agree to these Terms of Service.', 'If you disagree, please do not use our service.'] },
    { title: '2. Description of Service', content: ['Raptorflow is an AI-powered marketing operating system.', 'Features may change as we improve the platform.'] },
    { title: '3. Account Registration', content: ['Provide accurate information when creating an account.', 'Maintain security of your credentials.', 'Must be 18+ years old.'] },
    { title: '4. Payment', content: ['Some features require paid subscription.', 'Payments processed via Razorpay.', 'Prices in INR, inclusive of taxes.'] },
    { title: '5. User Content', content: ['You retain ownership of your content.', 'We may store and process content to provide service.'] },
    { title: '6. AI Content', content: ['AI content is a starting point and should be reviewed.', 'We do not guarantee accuracy.'] },
    { title: '7. Prohibited Uses', content: ['Illegal purposes prohibited.', 'Unauthorized access prohibited.'] },
    { title: '8. Liability', content: ['Service provided "as is".', 'Liability limited to amounts paid in past 12 months.'] },
    { title: '9. Governing Law', content: ['Governed by laws of India.', 'Disputes resolved in Chennai courts.'] },
    { title: '10. Contact', content: ['legal@raptorflow.com'] },
]

const Terms = () => (
    <div className="min-h-screen bg-background">
        <div className="max-w-3xl mx-auto px-6 py-24 md:py-32">
            {/* Header */}
            <motion.header
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
                className="mb-16"
            >
                <p className="text-caption text-muted-foreground mb-4">Legal</p>
                <h1 className="text-display text-4xl md:text-5xl text-foreground mb-4">Terms of Service</h1>
                <p className="text-muted-foreground">Last updated: December 1, 2024</p>
            </motion.header>

            {/* Intro */}
            <motion.div
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="bg-card border border-border/50 p-6 mb-12"
            >
                <p className="text-foreground leading-relaxed">
                    These Terms of Service govern your use of Raptorflow. Please read them carefully.
                </p>
            </motion.div>

            {/* Sections */}
            <div className="space-y-8">
                {sections.map((section, index) => (
                    <motion.div
                        key={section.title}
                        initial={{ opacity: 0, y: 16 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: index * 0.02 }}
                        className="border-b border-border/30 pb-8"
                    >
                        <h2 className="text-headline text-foreground mb-4">{section.title}</h2>
                        <ul className="space-y-2">
                            {section.content.map((item, i) => (
                                <li key={i} className="text-muted-foreground leading-relaxed flex items-start gap-3">
                                    <span className="w-1 h-1 bg-primary mt-2.5 flex-shrink-0" />
                                    {item}
                                </li>
                            ))}
                        </ul>
                    </motion.div>
                ))}
            </div>
        </div>
    </div>
)

export default Terms
