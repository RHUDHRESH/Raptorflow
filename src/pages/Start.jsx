import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { supabase } from '../lib/supabase'
import Button from '../components/Button'
import Input from '../components/Input'
import Card from '../components/Card'

export default function Start() {
    const navigate = useNavigate()
    const [loading, setLoading] = useState(false)
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        password: ''
    })

    const handleGoogleSignup = async () => {
        try {
            setLoading(true)
            const { error } = await supabase.auth.signInWithOAuth({
                provider: 'google',
                options: {
                    redirectTo: `${window.location.origin}/onboarding/intro`,
                },
            })
            if (error) throw error
        } catch (error) {
            console.error('Error signing up with Google:', error.message)
            alert('Error signing up with Google: ' + error.message)
        } finally {
            setLoading(false)
        }
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        const name = formData.name.trim()
        const email = formData.email.trim()
        const password = formData.password.trim()

        try {
            setLoading(true)
            const { data, error } = await supabase.auth.signUp({
                email,
                password,
                options: {
                    data: {
                        full_name: name,
                    },
                },
            })

            if (error) throw error

            if (data.user) {
                // Check if email confirmation is required
                if (data.user.identities && data.user.identities.length === 0) {
                     alert('User already exists. Please log in.')
                     navigate('/login')
                } else {
                     // In many cases, signUp might require email verification.
                     // If auto-confirm is on, we can navigate.
                     // If not, we should show a message "Check your email".
                     // For now, assuming we can navigate or show a message.
                     // But given the dev environment, let's assume we want to go to onboarding if session is established.
                     if (data.session) {
                        navigate('/onboarding/intro')
                     } else {
                        alert('Please check your email to confirm your account.')
                     }
                }
            }
        } catch (error) {
            console.error('Error signing up:', error.message)
            alert('Error signing up: ' + error.message)
        } finally {
            setLoading(false)
        }
    }

    const handleChange = (e) => {
        const { name, value } = e.target
        setFormData(prev => ({
            ...prev,
            [name]: value
        }))
    }

    return (
        <div className="min-h-screen bg-canvas antialiased selection:bg-gold selection:text-white font-sans relative">
            {/* Texture Overlay */}
            <div className="fixed inset-0 z-0 pointer-events-none opacity-[0.03] mix-blend-multiply" 
                 style={{ backgroundImage: 'url(/pattern.png)', backgroundSize: '120px' }} />
            
            <div className="grid grid-cols-1 lg:grid-cols-2 min-h-screen relative z-10">

                {/* Left Editorial Section - Hidden on mobile */}
                <div className="hidden lg:flex flex-col justify-between p-12 lg:p-16 border-r border-line">
                    <div>
                        {/* Brand */}
                        <div className="flex items-center gap-3 mb-20">
                            <div className="w-9 h-9 rounded-full border border-charcoal/20 flex items-center justify-center">
                                <span className="font-serif italic text-sm text-aubergine">Rf</span>
                            </div>
                            <div className="font-serif text-2xl font-semibold tracking-tight text-aubergine italic">
                                Raptor<span className="not-italic text-charcoal">flow</span>
                            </div>
                        </div>

                        {/* Editorial Content */}
                        <div className="max-w-md">
                            <p className="text-[11px] tracking-[0.28em] uppercase text-gold mb-4">
                                New War Plan · ~10 Minutes
                            </p>
                            <h1 className="font-serif text-[3rem] lg:text-[3.5rem] leading-[0.95] mb-6">
                                Turn your <span className="italic text-aubergine">chaos</span> into a 90-day outline.
                            </h1>
                            <p className="text-sm md:text-base text-charcoal/70 leading-relaxed">
                                Answer a few sharp questions. We'll build your first plan before we ever
                                ask for payment.
                            </p>
                        </div>
                    </div>

                    {/* Bottom Quote */}
                    <div className="max-w-md">
                        <p className="font-serif italic text-charcoal/60 text-sm">
                            "Most founders don't need more tactics. They need a plan they can actually execute."
                        </p>
                    </div>
                </div>

                {/* Right Auth Section */}
                <div className="flex items-center justify-center p-6 md:p-12">
                    <div className="w-full max-w-md">

                        {/* Mobile Brand - Shown only on mobile */}
                        <div className="lg:hidden flex items-center gap-3 mb-8">
                            <div className="w-9 h-9 rounded-full border border-charcoal/20 flex items-center justify-center">
                                <span className="font-serif italic text-sm text-aubergine">Rf</span>
                            </div>
                            <div className="font-serif text-2xl font-semibold tracking-tight text-aubergine italic">
                                Raptor<span className="not-italic text-charcoal">flow</span>
                            </div>
                        </div>

                        <Card>
                            {/* Card Header */}
                            <div className="mb-8">
                                <h2 className="font-serif text-2xl md:text-3xl mb-2">Create your account</h2>
                                <p className="text-sm text-charcoal/60">
                                    We'll save your answers and plans here. No spam.
                                </p>
                            </div>

                            {/* OAuth Button */}
                            <Button
                                variant="oauth"
                                onClick={handleGoogleSignup}
                                className="mb-6"
                                disabled={loading}
                            >
                                <svg className="w-4 h-4" viewBox="0 0 24 24">
                                    <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                                    <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                                    <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                                    <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
                                </svg>
                                {loading ? 'Connecting...' : 'Continue with Google'}
                            </Button>

                            {/* Divider */}
                            <div className="relative my-6">
                                <div className="absolute inset-0 flex items-center">
                                    <div className="w-full border-t border-line"></div>
                                </div>
                                <div className="relative flex justify-center text-xs uppercase tracking-[0.2em]">
                                    <span className="bg-white/40 px-4 text-charcoal/40">or</span>
                                </div>
                            </div>

                            {/* Signup Form */}
                            <form onSubmit={handleSubmit} className="space-y-4">
                                <Input
                                    label="Name"
                                    type="text"
                                    name="name"
                                    value={formData.name}
                                    onChange={handleChange}
                                    placeholder="Alex Chen"
                                    required
                                />

                                <Input
                                    label="Email"
                                    type="email"
                                    name="email"
                                    value={formData.email}
                                    onChange={handleChange}
                                    placeholder="you@company.com"
                                    required
                                />

                                <Input
                                    label="Password"
                                    type="password"
                                    name="password"
                                    value={formData.password}
                                    onChange={handleChange}
                                    placeholder="••••••••"
                                    required
                                />

                                {/* Submit Button */}
                                <Button type="submit" variant="primary" className="w-full mt-6" disabled={loading}>
                                    {loading ? 'Creating account...' : 'Start my plan'}
                                </Button>
                            </form>

                            {/* Login Link */}
                            <div className="mt-6 text-center text-sm text-charcoal/60">
                                Already have an account?{' '}
                                <button
                                    onClick={() => navigate('/login')}
                                    className="text-charcoal border-b border-charcoal/30 hover:border-aubergine hover:text-aubergine transition-colors"
                                >
                                    Log in
                                </button>
                            </div>
                        </Card>
                    </div>
                </div>
            </div>
        </div>
    )
}
