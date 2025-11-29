import React from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { RefreshCw, Home, AlertTriangle, ArrowRight } from 'lucide-react'
import { LuxeButton } from '../components/ui/PremiumUI'

export default function Error500({ error, resetErrorBoundary }) {
    const navigate = useNavigate()

    return (
        <div className="min-h-screen bg-black text-white flex items-center justify-center p-6 relative overflow-hidden">
            {/* Background Texture */}
            <div className="absolute inset-0 opacity-20"
                style={{
                    backgroundImage: 'radial-gradient(circle at 2px 2px, rgba(255,255,255,0.15) 1px, transparent 0)',
                    backgroundSize: '40px 40px'
                }}
            />

            {/* Ambient Glow */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-white/5 rounded-full blur-[100px] pointer-events-none" />

            <div className="max-w-2xl w-full relative z-10">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
                    className="text-center"
                >
                    <motion.div
                        initial={{ scale: 0.8, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        transition={{ delay: 0.2, duration: 0.5 }}
                        className="inline-flex items-center justify-center w-20 h-20 mb-8 rounded-full border border-white/10 bg-white/5 backdrop-blur-sm"
                    >
                        <AlertTriangle className="w-8 h-8 text-white/80" strokeWidth={1.5} />
                    </motion.div>

                    <h1 className="font-serif text-5xl md:text-7xl font-black tracking-tight mb-6 text-transparent bg-clip-text bg-gradient-to-b from-white to-white/60">
                        System Paused
                    </h1>

                    <p className="text-lg md:text-xl text-white/60 mb-12 max-w-lg mx-auto leading-relaxed font-light">
                        We encountered an unexpected state. <br className="hidden md:block" />
                        Our architects have been notified.
                    </p>

                    {error && (
                        <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                            className="mb-12 mx-auto max-w-md overflow-hidden rounded-lg border border-white/10 bg-white/5 backdrop-blur-md"
                        >
                            <div className="p-4 text-left">
                                <p className="text-xs font-mono text-white/40 mb-2 uppercase tracking-widest">Error Trace</p>
                                <p className="text-sm font-mono text-red-300 break-all">
                                    {error.message || error.toString()}
                                </p>
                            </div>
                        </motion.div>
                    )}

                    <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                        <motion.button
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            onClick={resetErrorBoundary || (() => window.location.reload())}
                            className="group relative px-8 py-4 bg-white text-black font-bold text-sm uppercase tracking-widest overflow-hidden rounded-full"
                        >
                            <span className="relative z-10 flex items-center gap-2">
                                <RefreshCw className="w-4 h-4" />
                                Reboot System
                            </span>
                            <div className="absolute inset-0 bg-gray-200 transform scale-x-0 group-hover:scale-x-100 transition-transform origin-left duration-300" />
                        </motion.button>

                        <motion.button
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            onClick={() => navigate('/dashboard')}
                            className="group px-8 py-4 bg-transparent border border-white/20 text-white font-bold text-sm uppercase tracking-widest rounded-full hover:bg-white/5 transition-colors"
                        >
                            <span className="flex items-center gap-2">
                                <Home className="w-4 h-4" />
                                Return to Base
                            </span>
                        </motion.button>
                    </div>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 1, duration: 1 }}
                    className="mt-24 text-center"
                >
                    <p className="text-xs font-mono text-white/20 uppercase tracking-[0.2em]">
                        RaptorFlow // Error 500
                    </p>
                </motion.div>
            </div>
        </div>
    )
}
