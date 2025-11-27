import React from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'

export const FooterHuge = () => {
    return (
        <footer className="bg-black text-white pt-32 pb-12">
            <div className="mx-auto max-w-[1400px] px-6 md:px-12">
                <div className="grid grid-cols-1 md:grid-cols-12 gap-12 mb-32">
                    <div className="md:col-span-4">
                        <Link to="/" className="font-serif text-3xl font-bold tracking-tighter mb-8 block">
                            RaptorFlow.
                        </Link>
                        <p className="text-neutral-500 max-w-sm font-light">
                            Strategy execution for the modern age. <br />
                            Simple. Elegant. Powerful.
                        </p>
                    </div>

                    <div className="md:col-span-2 md:col-start-7">
                        <h4 className="font-mono text-xs uppercase tracking-widest text-neutral-500 mb-8">Platform</h4>
                        <ul className="space-y-4 font-light text-neutral-300">
                            <li><Link to="#" className="hover:text-white transition-colors">Intelligence</Link></li>
                            <li><Link to="#" className="hover:text-white transition-colors">Cohorts</Link></li>
                            <li><Link to="#" className="hover:text-white transition-colors">Campaigns</Link></li>
                            <li><Link to="#" className="hover:text-white transition-colors">Analytics</Link></li>
                        </ul>
                    </div>

                    <div className="md:col-span-2">
                        <h4 className="font-mono text-xs uppercase tracking-widest text-neutral-500 mb-8">Company</h4>
                        <ul className="space-y-4 font-light text-neutral-300">
                            <li><Link to="#" className="hover:text-white transition-colors">Manifesto</Link></li>
                            <li><Link to="#" className="hover:text-white transition-colors">Careers</Link></li>
                            <li><Link to="#" className="hover:text-white transition-colors">Contact</Link></li>
                        </ul>
                    </div>

                    <div className="md:col-span-2">
                        <h4 className="font-mono text-xs uppercase tracking-widest text-neutral-500 mb-8">Legal</h4>
                        <ul className="space-y-4 font-light text-neutral-300">
                            <li><Link to="/privacy" className="hover:text-white transition-colors">Privacy</Link></li>
                            <li><Link to="/terms" className="hover:text-white transition-colors">Terms</Link></li>
                        </ul>
                    </div>
                </div>

                <div className="border-t border-white/10 pt-12 flex flex-col md:flex-row justify-between items-center gap-6">
                    <p className="text-neutral-600 text-sm font-mono">© 2024 RAPTORFLOW INC.</p>
                    <div className="font-serif italic text-2xl text-neutral-800">
                        Execute Beautifully.
                    </div>
                </div>
            </div>
        </footer>
    )
}
