import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowLeft, Home, Search } from 'lucide-react'
import { LuxeButton, LuxeCard } from '../components/ui/PremiumUI'

export default function Error404() {
    const navigate = useNavigate()

    return (
        <div className="min-h-screen bg-neutral-50 flex items-center justify-center p-6">
            <div className="max-w-md w-full text-center space-y-8">
                <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.5 }}
                >
                    <h1 className="font-serif text-9xl font-black text-neutral-200">404</h1>
                    <div className="relative -mt-12">
                        <h2 className="font-serif text-3xl font-bold text-neutral-900 mb-2">Page Not Found</h2>
                        <p className="text-neutral-500">
                            The page you are looking for doesn't exist or has been moved.
                        </p>
                    </div>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="flex flex-col gap-3"
                >
                    <LuxeButton onClick={() => navigate(-1)} variant="secondary" icon={ArrowLeft} className="w-full justify-center">
                        Go Back
                    </LuxeButton>
                    <Link to="/dashboard" className="w-full">
                        <LuxeButton icon={Home} className="w-full justify-center">
                            Return Home
                        </LuxeButton>
                    </Link>
                </motion.div>
            </div>
        </div>
    )
}
