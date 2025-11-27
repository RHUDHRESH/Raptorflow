import React, { useState } from 'react'
import { motion } from 'framer-motion'
// import { Slider } from '../ui/slider' // Assuming we have this or I'll mock it
import { LuxeCard, LuxeHeading, LuxeButton } from '../ui/PremiumUI'
import { DollarSign, TrendingUp, Users, ArrowRight } from 'lucide-react'

// Mock Slider if not exists
const SimpleSlider = ({ value, onValueChange, min, max, step }) => (
    <div className="relative w-full h-6 flex items-center">
        <input
            type="range"
            min={min}
            max={max}
            step={step}
            value={value[0]}
            onChange={(e) => onValueChange([parseFloat(e.target.value)])}
            className="w-full h-2 bg-neutral-200 rounded-lg appearance-none cursor-pointer accent-neutral-900"
        />
    </div>
)

export const RoiCalculator = () => {
    const [visitors, setVisitors] = useState([10000])
    const [conversion, setConversion] = useState([2])
    const [ltv, setLtv] = useState([500])

    const currentRevenue = visitors[0] * (conversion[0] / 100) * ltv[0]
    const raptorImpact = currentRevenue * 1.45 // 45% uplift
    const uplift = raptorImpact - currentRevenue

    return (
        <section className="py-32 bg-neutral-900 text-white overflow-hidden relative">
            <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20"></div>

            <div className="mx-auto max-w-7xl px-6 relative z-10">
                <div className="grid lg:grid-cols-2 gap-20 items-center">
                    <div>
                        <LuxeHeading level={2} className="text-white mb-6">
                            Calculate your <br />
                            <span className="text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-emerald-600">
                                Potential Growth
                            </span>
                        </LuxeHeading>
                        <p className="text-neutral-400 text-xl mb-12 leading-relaxed">
                            See how much revenue you're leaving on the table. RaptorFlow typically increases strategic execution efficiency by 3x and revenue by 45%.
                        </p>

                        <div className="space-y-10">
                            <div>
                                <div className="flex justify-between mb-4">
                                    <label className="font-medium text-neutral-300">Monthly Visitors</label>
                                    <span className="font-mono text-white">{visitors[0].toLocaleString()}</span>
                                </div>
                                <SimpleSlider value={visitors} onValueChange={setVisitors} min={1000} max={100000} step={1000} />
                            </div>

                            <div>
                                <div className="flex justify-between mb-4">
                                    <label className="font-medium text-neutral-300">Conversion Rate (%)</label>
                                    <span className="font-mono text-white">{conversion[0]}%</span>
                                </div>
                                <SimpleSlider value={conversion} onValueChange={setConversion} min={0.1} max={10} step={0.1} />
                            </div>

                            <div>
                                <div className="flex justify-between mb-4">
                                    <label className="font-medium text-neutral-300">Customer LTV ($)</label>
                                    <span className="font-mono text-white">${ltv[0]}</span>
                                </div>
                                <SimpleSlider value={ltv} onValueChange={setLtv} min={50} max={5000} step={50} />
                            </div>
                        </div>
                    </div>

                    <div className="relative">
                        <div className="absolute inset-0 bg-gradient-to-r from-green-500/20 to-emerald-500/20 blur-3xl rounded-full" />
                        <LuxeCard className="bg-neutral-800/50 border-neutral-700 backdrop-blur-xl relative">
                            <div className="text-center py-8 border-b border-neutral-700">
                                <p className="text-neutral-400 text-sm uppercase tracking-wider font-bold mb-2">Projected Annual Revenue</p>
                                <div className="font-serif text-6xl font-black text-white">
                                    ${raptorImpact.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                                </div>
                                <div className="mt-4 inline-flex items-center gap-2 text-green-400 bg-green-400/10 px-3 py-1 rounded-full text-sm font-bold">
                                    <TrendingUp className="w-4 h-4" />
                                    +${uplift.toLocaleString(undefined, { maximumFractionDigits: 0 })} uplift
                                </div>
                            </div>

                            <div className="p-8 space-y-6">
                                <div className="flex items-center gap-4">
                                    <div className="w-10 h-10 rounded-full bg-neutral-700 flex items-center justify-center">
                                        <Users className="w-5 h-5 text-white" />
                                    </div>
                                    <div>
                                        <div className="text-sm text-neutral-400">Additional Customers</div>
                                        <div className="text-xl font-bold text-white">
                                            +{Math.floor((visitors[0] * (conversion[0] / 100) * 0.45)).toLocaleString()}
                                        </div>
                                    </div>
                                </div>

                                <div className="flex items-center gap-4">
                                    <div className="w-10 h-10 rounded-full bg-neutral-700 flex items-center justify-center">
                                        <DollarSign className="w-5 h-5 text-white" />
                                    </div>
                                    <div>
                                        <div className="text-sm text-neutral-400">Efficiency Gain</div>
                                        <div className="text-xl font-bold text-white">312%</div>
                                    </div>
                                </div>

                                <LuxeButton className="w-full mt-4 bg-white text-neutral-900 hover:bg-neutral-200">
                                    Unlock This Growth <ArrowRight className="ml-2 w-4 h-4" />
                                </LuxeButton>
                            </div>
                        </LuxeCard>
                    </div>
                </div>
            </div>
        </section>
    )
}
