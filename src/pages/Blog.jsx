import React, { useState } from 'react'
import { ReactLenis } from 'lenis/react'
import Header from './landing/Header'
import Footer from './landing/Footer'
import CustomCursor from '../components/CustomCursor'
import { motion, AnimatePresence } from 'framer-motion'
import { Sparkles, Bell, ArrowRight, Check, Twitter, Linkedin } from 'lucide-react'

const Blog = () => {
    const [email, setEmail] = useState('')
    const [status, setStatus] = useState('idle')

    const handleSubmit = async (e) => {
        e.preventDefault()
        if (!email) return

        setStatus('loading')
        await new Promise(resolve => setTimeout(resolve, 1500))
        setStatus('success')
        setEmail('')
        setTimeout(() => setStatus('idle'), 3000)
    }

    return (
        <ReactLenis root>
            <div className="min-h-screen bg-[#0a0a0a] antialiased font-sans selection:bg-amber-500/30 relative">
                <CustomCursor />
                <Header />

                {/* Texture Overlay */}
                <div className="fixed inset-0 z-0 pointer-events-none opacity-[0.02]"
                    style={{ backgroundImage: 'url(/noise.png)', backgroundSize: '200px' }} />

                <main className="relative z-10 pt-32 pb-24 min-h-[80vh] flex items-center justify-center">
                    <div className="max-w-2xl mx-auto px-6 md:px-12 text-center">

                        <motion.div
                            initial={{ opacity: 0, y: 30 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.8 }}
                        >
                            {/* Icon */}
                            <motion.div
                                className="w-20 h-20 mx-auto mb-8 rounded-2xl bg-gradient-to-br from-amber-500/20 to-orange-500/10 flex items-center justify-center"
                                animate={{
                                    boxShadow: ['0 0 0 0 rgba(245,158,11,0)', '0 0 60px 10px rgba(245,158,11,0.1)', '0 0 0 0 rgba(245,158,11,0)']
                                }}
                                transition={{ duration: 3, repeat: Infinity }}
                            >
                                <Sparkles className="w-10 h-10 text-amber-400" />
                            </motion.div>

                            <span className="text-xs uppercase tracking-[0.4em] text-amber-400 font-medium block mb-6">
                                Blog
                            </span>

                            <h1 className="text-4xl md:text-6xl font-light text-white leading-tight mb-6">
                                Coming <span className="italic text-amber-300">soon</span>
                            </h1>

                            <p className="text-xl text-white/50 max-w-md mx-auto mb-12 leading-relaxed">
                                We're crafting insights on positioning, founder marketing, and AI-powered strategy.
                                Be the first to know when we publish.
                            </p>

                            {/* Newsletter Signup */}
                            <form onSubmit={handleSubmit} className="max-w-md mx-auto mb-12">
                                <div className={`
                  flex items-center gap-2 p-1.5 rounded-xl border transition-all duration-300
                  ${status === 'success' ? 'border-emerald-500/40 bg-emerald-500/5' : 'border-white/10 bg-white/5 focus-within:border-amber-500/40 focus-within:bg-amber-500/5'}
                `}>
                                    <input
                                        type="email"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        placeholder="Enter your email"
                                        className="flex-1 px-4 py-3 bg-transparent text-white placeholder:text-white/30 focus:outline-none text-sm"
                                        disabled={status !== 'idle'}
                                    />

                                    <motion.button
                                        type="submit"
                                        disabled={status !== 'idle' || !email}
                                        className="px-5 py-3 bg-white text-black font-medium rounded-lg text-sm flex items-center gap-2 disabled:opacity-50 transition-all hover:bg-white/90"
                                        whileHover={{ scale: 1.02 }}
                                        whileTap={{ scale: 0.98 }}
                                    >
                                        <AnimatePresence mode="wait">
                                            {status === 'loading' ? (
                                                <motion.div
                                                    key="loading"
                                                    initial={{ opacity: 0 }}
                                                    animate={{ opacity: 1, rotate: 360 }}
                                                    exit={{ opacity: 0 }}
                                                    transition={{ duration: 0.5, repeat: Infinity }}
                                                    className="w-4 h-4 border-2 border-black/20 border-t-black rounded-full"
                                                />
                                            ) : status === 'success' ? (
                                                <motion.div
                                                    key="success"
                                                    initial={{ scale: 0 }}
                                                    animate={{ scale: 1 }}
                                                    exit={{ scale: 0 }}
                                                >
                                                    <Check className="w-4 h-4" />
                                                </motion.div>
                                            ) : (
                                                <motion.div
                                                    key="default"
                                                    initial={{ opacity: 0 }}
                                                    animate={{ opacity: 1 }}
                                                    exit={{ opacity: 0 }}
                                                    className="flex items-center gap-2"
                                                >
                                                    <Bell className="w-4 h-4" />
                                                    <span>Notify me</span>
                                                </motion.div>
                                            )}
                                        </AnimatePresence>
                                    </motion.button>
                                </div>

                                {status === 'success' && (
                                    <motion.p
                                        initial={{ opacity: 0, y: -10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        className="text-emerald-400 text-sm mt-3"
                                    >
                                        You're on the list! We'll notify you when we launch.
                                    </motion.p>
                                )}
                            </form>

                            {/* Social Links */}
                            <div className="flex items-center justify-center gap-4">
                                <span className="text-white/30 text-sm">Follow us:</span>
                                <a
                                    href="https://twitter.com/raptorflow"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="w-10 h-10 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center hover:border-amber-500/30 hover:bg-amber-500/10 transition-all"
                                >
                                    <Twitter className="w-4 h-4 text-white/50 hover:text-amber-400" />
                                </a>
                                <a
                                    href="https://linkedin.com/company/raptorflow"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="w-10 h-10 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center hover:border-amber-500/30 hover:bg-amber-500/10 transition-all"
                                >
                                    <Linkedin className="w-4 h-4 text-white/50 hover:text-amber-400" />
                                </a>
                            </div>
                        </motion.div>
                    </div>
                </main>

                <Footer />
            </div>
        </ReactLenis>
    )
}

export default Blog
