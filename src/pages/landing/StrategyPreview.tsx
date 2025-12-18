import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Check, ChevronRight, Sliders, BarChart2, Users, Target, ArrowUpRight } from 'lucide-react'
import { clsx } from 'clsx'

const StrategyPreview = () => {
  const [activeTab, setActiveTab] = useState('overview')

  // Simulated Data for the Dashboard
  const dashboardData = {
    overview: [
      { label: 'Total Revenue', value: '$124,500', change: '+12%', icon: BarChart2 },
      { label: 'Active Users', value: '1,240', change: '+5%', icon: Users },
      { label: 'Conversion Rate', value: '3.2%', change: '+0.4%', icon: Target },
    ],
    acquisition: [
        { label: 'LinkedIn', value: '450', change: '+20%', icon: ArrowUpRight },
        { label: 'SEO', value: '320', change: '+8%', icon: ArrowUpRight },
        { label: 'Direct', value: '180', change: '+2%', icon: ArrowUpRight },
    ],
    retention: [
        { label: 'Churn Rate', value: '1.8%', change: '-0.2%', icon: ArrowUpRight, positive: true },
        { label: 'LTV', value: '$850', change: '+5%', icon: ArrowUpRight },
        { label: 'NPS', value: '72', change: '+4', icon: ArrowUpRight },
    ]
  }

  return (
    <section className="py-32 bg-charcoal relative overflow-hidden text-canvas">
        {/* Background Glow */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[500px] bg-aubergine/20 blur-[120px] rounded-full pointer-events-none"></div>

        <div className="max-w-7xl mx-auto px-6 md:px-12 relative z-10">
            <div className="text-center mb-20 space-y-4">
                <motion.span 
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    className="text-xs uppercase tracking-[0.3em] text-gold font-medium"
                >
                    The Control Room
                </motion.span>
                <motion.h2 
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.1 }}
                    className="font-serif text-4xl md:text-6xl"
                >
                    Your strategy, <span className="italic text-gray-400">visualized.</span>
                </motion.h2>
            </div>

            {/* Dashboard UI Container */}
            <div className="relative rounded-3xl border border-white/10 bg-white/5 backdrop-blur-2xl overflow-hidden shadow-2xl">
                {/* Window Controls */}
                <div className="h-12 border-b border-white/10 flex items-center px-6 gap-2 bg-white/5">
                    <div className="w-3 h-3 rounded-full bg-white/20"></div>
                    <div className="w-3 h-3 rounded-full bg-white/20"></div>
                    <div className="w-3 h-3 rounded-full bg-white/20"></div>
                </div>

                {/* Dashboard Content */}
                <div className="grid grid-cols-1 lg:grid-cols-4 h-[600px]">
                    
                    {/* Sidebar */}
                    <div className="border-r border-white/10 p-6 hidden lg:block bg-white/5">
                        <div className="space-y-6">
                            <div className="flex items-center gap-3 text-white/40 text-xs uppercase tracking-widest font-medium mb-6">
                                Menu
                            </div>
                            {['Overview', 'Acquisition', 'Retention', 'Settings'].map((item) => (
                                <button 
                                    key={item}
                                    onClick={() => setActiveTab(item.toLowerCase())}
                                    className={clsx(
                                        "w-full text-left px-4 py-3 rounded-lg text-sm transition-all",
                                        activeTab === item.toLowerCase() 
                                            ? "bg-white/10 text-white font-medium" 
                                            : "text-white/60 hover:text-white hover:bg-white/5"
                                    )}
                                >
                                    {item}
                                </button>
                            ))}
                        </div>
                        
                        <div className="mt-12 p-4 rounded-xl bg-gradient-to-br from-gold/20 to-transparent border border-gold/10">
                            <p className="text-xs text-gold mb-2">Live Insight</p>
                            <p className="text-sm text-white/80">Traffic spike detected from LinkedIn. Review campaign performance.</p>
                        </div>
                    </div>

                    {/* Main Area */}
                    <div className="lg:col-span-3 p-8 overflow-y-auto">
                        <div className="flex justify-between items-end mb-10">
                            <div>
                                <h3 className="text-2xl font-serif text-white">Q1 Performance</h3>
                                <p className="text-white/40 text-sm">Updated just now</p>
                            </div>
                            <button className="px-4 py-2 rounded-lg bg-white text-charcoal text-xs font-medium hover:bg-gray-200 transition-colors">
                                Export Report
                            </button>
                        </div>

                        {/* Metrics Grid */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
                            {dashboardData[activeTab === 'settings' ? 'overview' : activeTab].map((metric, i) => (
                                <motion.div
                                    key={metric.label}
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: i * 0.1 }}
                                    className="p-6 rounded-2xl bg-white/5 border border-white/10 hover:bg-white/10 transition-colors group"
                                >
                                    <div className="flex justify-between items-start mb-4">
                                        <div className="p-2 rounded-lg bg-white/5 text-white/60 group-hover:text-white transition-colors">
                                            <metric.icon className="w-5 h-5" />
                                        </div>
                                        <span className={clsx("text-xs font-medium px-2 py-1 rounded-full", metric.positive !== false ? "bg-white/20 text-white" : "bg-white/5 text-white/60")}>
                                            {metric.change}
                                        </span>
                                    </div>
                                    <p className="text-white/40 text-xs uppercase tracking-wider mb-1">{metric.label}</p>
                                    <p className="text-3xl font-mono text-white">{metric.value}</p>
                                </motion.div>
                            ))}
                        </div>

                        {/* Chart Area (Simulated) */}
                        <div className="h-64 w-full bg-white/5 rounded-2xl border border-white/10 p-6 relative overflow-hidden group">
                            <div className="absolute inset-0 bg-gradient-to-t from-aubergine/20 to-transparent opacity-50"></div>
                            <div className="flex items-end justify-between h-full gap-2 px-4 pb-4">
                                {[40, 65, 50, 80, 55, 90, 70, 85, 60, 75, 95, 100].map((height, i) => (
                                    <motion.div
                                        key={i}
                                        initial={{ height: 0 }}
                                        whileInView={{ height: `${height}%` }}
                                        transition={{ duration: 1, delay: i * 0.05, ease: "easeOut" }}
                                        className="w-full bg-gradient-to-t from-white/20 to-white/60 rounded-t-sm group-hover:from-gold/20 group-hover:to-gold/60 transition-colors duration-500"
                                    ></motion.div>
                                ))}
                            </div>
                        </div>

                    </div>
                </div>
            </div>
        </div>
    </section>
  )
}

export default StrategyPreview

