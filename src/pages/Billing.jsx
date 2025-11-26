import { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import { paymentAPI } from '../services/paymentAPI';
import { motion, AnimatePresence } from 'framer-motion';
import {
    CreditCard,
    Calendar,
    Download,
    CheckCircle2,
    AlertCircle,
    ArrowRight,
    Loader2,
    Shield,
    Sparkles,
    Zap,
    Crown,
    Star,
    TrendingUp
} from 'lucide-react';

// Animated counter component
const AnimatedCounter = ({ end, duration = 2, suffix = '', prefix = '' }) => {
    const [count, setCount] = useState(0)
    const nodeRef = useRef(null)

    useEffect(() => {
        let startTime = null
        const animate = (currentTime) => {
            if (!startTime) startTime = currentTime
            const progress = Math.min((currentTime - startTime) / (duration * 1000), 1)
            const easeOutQuart = 1 - Math.pow(1 - progress, 4)
            setCount(Math.floor(easeOutQuart * end))

            if (progress < 1) {
                requestAnimationFrame(animate)
            }
        }
        requestAnimationFrame(animate)
    }, [end, duration])

    return <span ref={nodeRef}>{prefix}{count}{suffix}</span>
}

// Magnetic card component
const MagneticCard = ({ children, className }) => {
    const [position, setPosition] = useState({ x: 0, y: 0 })
    const cardRef = useRef(null)

    const handleMouseMove = (e) => {
        if (!cardRef.current) return
        const rect = cardRef.current.getBoundingClientRect()
        const x = (e.clientX - rect.left - rect.width / 2) * 0.03
        const y = (e.clientY - rect.top - rect.height / 2) * 0.03
        setPosition({ x, y })
    }

    const handleMouseLeave = () => {
        setPosition({ x: 0, y: 0 })
    }

    return (
        <motion.div
            ref={cardRef}
            onMouseMove={handleMouseMove}
            onMouseLeave={handleMouseLeave}
            animate={{ x: position.x, y: position.y }}
            transition={{ type: 'spring', stiffness: 150, damping: 15 }}
            className={className}
        >
            {children}
        </motion.div>
    )
}

export default function BillingLuxe() {
    const { user, subscription } = useAuth();
    const [billingHistory, setBillingHistory] = useState([]);
    const [plans, setPlans] = useState([]);
    const [error, setError] = useState(null);
    const [loadingPlan, setLoadingPlan] = useState(null);

    useEffect(() => {
        fetchPlans();
        fetchBillingHistory();
    }, []);

    const fetchPlans = async () => {
        try {
            const data = await paymentAPI.getPlans();
            const plansArray = Object.entries(data.plans).map(([key, plan]) => ({
                name: plan.name.charAt(0).toUpperCase() + plan.name.slice(1),
                price: plan.price_monthly,
                period: 'month',
                description: getDescription(plan.name),
                features: formatFeatures(plan.features, plan.limits),
                popular: plan.name === 'glide',
                icon: plan.name === 'ascent' ? Zap : plan.name === 'glide' ? Crown : Sparkles
            }));
            setPlans(plansArray);
        } catch (err) {
            console.error('Error fetching plans:', err);
            setError('Failed to load plans');
        }
    };

    const fetchBillingHistory = async () => {
        try {
            const data = await paymentAPI.getBillingHistory();
            setBillingHistory(data.history || []);
        } catch (err) {
            console.error('Error fetching billing history:', err);
        }
    };

    const getDescription = (planName) => {
        const descriptions = {
            ascent: 'Perfect for solo founders',
            glide: 'For growing teams',
            soar: 'For agencies & enterprises'
        };
        return descriptions[planName] || '';
    };

    const formatFeatures = (features, limits) => {
        return [
            `${limits.cohorts} cohorts`,
            `${limits.moves_per_month} moves per week`,
            '3 actions per day',
            features.analytics ? 'Advanced analytics' : 'Basic analytics',
            features.support === 'priority_phone' ? '24/7 priority support' :
                features.support === 'priority_email' ? 'Priority email support' : 'Email support',
            ...(features.integrations?.length > 3 ? ['Custom integrations'] : [])
        ];
    };

    const handleUpgrade = async (planName) => {
        setLoadingPlan(planName);
        setError(null);

        try {
            const successUrl = `${window.location.origin}/billing?payment=success`;
            const checkout = await paymentAPI.createCheckout(
                planName.toLowerCase(),
                'monthly',
                successUrl
            );

            window.location.href = checkout.checkout_url;
        } catch (err) {
            console.error('Error creating checkout:', err);
            setError(err.message || 'Failed to initiate payment');
            setLoadingPlan(null);
        }
    };

    const currentPlan = subscription?.plan || 'free';

    return (
        <div className="space-y-12 animate-fade-in-up">
            {/* Hero Section */}
            <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
                className="relative overflow-hidden"
            >
                <div className="flex items-center gap-4 mb-8">
                    <motion.span
                        className="text-micro text-gray-400"
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.2 }}
                    >
                        Billing
                    </motion.span>
                    <motion.span
                        className="h-px w-20 bg-black/10"
                        initial={{ width: 0 }}
                        animate={{ width: 80 }}
                        transition={{ delay: 0.4, duration: 0.6 }}
                    />
                </div>
                <motion.h1
                    className="text-hero mb-4"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3, duration: 0.6 }}
                >
                    Subscription & Billing
                </motion.h1>
                <motion.p
                    className="text-body max-w-2xl"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.5 }}
                >
                    Manage your subscription, payment methods, and billing history
                </motion.p>
            </motion.div>

            {/* Error Alert */}
            <AnimatePresence>
                {error && (
                    <motion.div
                        initial={{ opacity: 0, y: -10, scale: 0.95 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: -10, scale: 0.95 }}
                        className="p-6 bg-oxblood/5 border-2 border-oxblood/20 rounded flex items-start gap-4"
                    >
                        <motion.div
                            animate={{ rotate: [0, 5, -5, 0] }}
                            transition={{ duration: 0.5 }}
                        >
                            <AlertCircle className="h-6 w-6 text-oxblood flex-shrink-0" />
                        </motion.div>
                        <p className="text-oxblood font-medium">{error}</p>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Current Plan Card */}
            <MagneticCard className="relative overflow-hidden border-2 border-black bg-black text-white">
                {/* Animated background grid */}
                <motion.div
                    className="absolute inset-0 opacity-[0.03]"
                    style={{
                        backgroundImage: `linear-gradient(to right, white 1px, transparent 1px),
                                        linear-gradient(to bottom, white 1px, transparent 1px)`,
                        backgroundSize: '40px 40px'
                    }}
                    animate={{
                        backgroundPosition: ['0px 0px', '40px 40px'],
                    }}
                    transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
                />

                {/* Floating orbs */}
                <motion.div
                    className="absolute top-0 right-0 w-64 h-64 bg-white/[0.05] rounded-full blur-3xl"
                    animate={{
                        scale: [1, 1.2, 1],
                        opacity: [0.3, 0.5, 0.3],
                    }}
                    transition={{ duration: 4, repeat: Infinity }}
                />

                <div className="relative z-10 p-10">
                    <motion.div
                        className="flex items-start justify-between"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.6 }}
                    >
                        <div>
                            <div className="flex items-center gap-3 mb-4">
                                <motion.div
                                    animate={{
                                        rotate: [0, 360],
                                    }}
                                    transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
                                >
                                    <Shield className="h-8 w-8" strokeWidth={1.5} />
                                </motion.div>
                                <span className="text-micro text-white/60">Current Plan</span>
                            </div>
                            <motion.p
                                className="font-serif text-5xl font-black mb-3 capitalize"
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.7 }}
                            >
                                {currentPlan}
                            </motion.p>
                            {currentPlan === 'free' && (
                                <motion.p
                                    className="text-white/70 text-sm max-w-md"
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    transition={{ delay: 0.8 }}
                                >
                                    No active subscription. Choose a plan below to unlock premium features.
                                </motion.p>
                            )}
                        </div>
                        <div className="text-right">
                            <p className="text-micro text-white/60 mb-2">Next billing date</p>
                            <motion.p
                                className="text-2xl font-bold"
                                initial={{ opacity: 0, scale: 0.9 }}
                                animate={{ opacity: 1, scale: 1 }}
                                transition={{ delay: 0.9, type: 'spring' }}
                            >
                                {subscription?.current_period_end
                                    ? new Date(subscription.current_period_end).toLocaleDateString('en-US', {
                                        month: 'short',
                                        day: 'numeric',
                                        year: 'numeric'
                                    })
                                    : 'N/A'
                                }
                            </motion.p>
                        </div>
                    </motion.div>
                </div>
            </MagneticCard>

            {/* Plans Grid */}
            <div>
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.8 }}
                    className="mb-8"
                >
                    <span className="text-micro text-gray-400 block mb-2">Choose Your Altitude</span>
                    <h2 className="text-heading">Available Plans</h2>
                </motion.div>

                <div className="grid gap-8 md:grid-cols-3">
                    {plans.map((plan, index) => {
                        const Icon = plan.icon
                        const isCurrent = currentPlan.toLowerCase() === plan.name.toLowerCase()

                        return (
                            <MagneticCard
                                key={plan.name}
                                className={`relative border-2 ${plan.popular
                                        ? 'border-black bg-black text-white'
                                        : 'border-black/10 bg-white hover:border-black/30'
                                    } transition-all duration-300 overflow-hidden group`}
                            >
                                <motion.div
                                    initial={{ opacity: 0, y: 30, scale: 0.95 }}
                                    animate={{ opacity: 1, y: 0, scale: 1 }}
                                    transition={{ delay: 1.0 + index * 0.15, type: 'spring', stiffness: 100 }}
                                    className="relative z-10 p-8"
                                >
                                    {/* Popular badge */}
                                    {plan.popular && (
                                        <motion.div
                                            initial={{ opacity: 0, y: -10 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            className="absolute -top-4 left-8 bg-white px-4 py-1.5 text-xs font-mono uppercase tracking-widest text-black"
                                        >
                                            Most Popular
                                        </motion.div>
                                    )}

                                    {/* Shimmer effect */}
                                    <motion.div
                                        className={`absolute inset-0 bg-gradient-to-r ${plan.popular
                                                ? 'from-transparent via-white/10 to-transparent'
                                                : 'from-transparent via-black/[0.02] to-transparent'
                                            }`}
                                        initial={{ x: '-100%' }}
                                        whileHover={{ x: '100%' }}
                                        transition={{ duration: 0.6 }}
                                    />

                                    {/* Icon */}
                                    <motion.div
                                        className={`w-14 h-14 rounded-lg flex items-center justify-center mb-6 ${plan.popular ? 'bg-white/10' : 'bg-black/5'
                                            }`}
                                        whileHover={{ scale: 1.1, rotate: 5 }}
                                        transition={{ type: 'spring', stiffness: 300 }}
                                    >
                                        <Icon className={`w-7 h-7 ${plan.popular ? 'text-white' : 'text-black'}`} strokeWidth={1.5} />
                                    </motion.div>

                                    {/* Plan details */}
                                    <div className="mb-8">
                                        <h3 className="font-serif text-3xl font-black mb-2">{plan.name}</h3>
                                        <p className={`text-sm mb-6 ${plan.popular ? 'text-white/70' : 'text-gray-600'}`}>
                                            {plan.description}
                                        </p>
                                        <div className="flex items-baseline gap-2">
                                            <span className="font-serif text-6xl font-black">
                                                ₹<AnimatedCounter end={plan.price} />
                                            </span>
                                            <span className={plan.popular ? 'text-white/60' : 'text-gray-600'}>
                                                /{plan.period}
                                            </span>
                                        </div>
                                    </div>

                                    {/* Features */}
                                    <ul className="space-y-3 mb-8">
                                        {plan.features.map((feature, i) => (
                                            <motion.li
                                                key={i}
                                                className="flex items-start gap-3"
                                                initial={{ opacity: 0, x: -10 }}
                                                animate={{ opacity: 1, x: 0 }}
                                                transition={{ delay: 1.2 + index * 0.15 + i * 0.03 }}
                                                whileHover={{ x: 5 }}
                                            >
                                                <CheckCircle2 className={`h-5 w-5 flex-shrink-0 mt-0.5 ${plan.popular ? 'text-white' : 'text-black'
                                                    }`} strokeWidth={2} />
                                                <span className="text-sm leading-relaxed">{feature}</span>
                                            </motion.li>
                                        ))}
                                    </ul>

                                    {/* CTA Button */}
                                    <motion.button
                                        onClick={() => handleUpgrade(plan.name)}
                                        disabled={loadingPlan === plan.name || isCurrent}
                                        whileHover={!isCurrent && !loadingPlan ? { scale: 1.02 } : {}}
                                        whileTap={!isCurrent && !loadingPlan ? { scale: 0.98 } : {}}
                                        className={`w-full py-4 rounded font-semibold transition-all duration-300 flex items-center justify-center gap-2 ${isCurrent
                                                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                                                : plan.popular
                                                    ? 'bg-white text-black hover:bg-gray-100 button-enhanced'
                                                    : 'border-2 border-black text-black hover:bg-black hover:text-white'
                                            }`}
                                    >
                                        {loadingPlan === plan.name ? (
                                            <Loader2 className="h-5 w-5 animate-spin" />
                                        ) : isCurrent ? (
                                            <>
                                                <CheckCircle2 className="h-5 w-5" />
                                                Current Plan
                                            </>
                                        ) : (
                                            <>
                                                Subscribe to {plan.name}
                                                <motion.div
                                                    animate={{ x: [0, 3, 0] }}
                                                    transition={{ duration: 1.5, repeat: Infinity }}
                                                >
                                                    <ArrowRight className="h-5 w-5" />
                                                </motion.div>
                                            </>
                                        )}
                                    </motion.button>
                                </motion.div>
                            </MagneticCard>
                        )
                    })}
                </div>
            </div>

            {/* Payment Method */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1.5 }}
                className="card-luxe p-8"
            >
                <div className="flex items-center gap-3 mb-6">
                    <motion.div
                        className="w-12 h-12 rounded-lg bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center"
                        whileHover={{ scale: 1.1, rotate: 5 }}
                        transition={{ type: 'spring', stiffness: 300 }}
                    >
                        <CreditCard className="h-6 w-6 text-white" strokeWidth={1.5} />
                    </motion.div>
                    <div>
                        <span className="text-micro text-gray-400 block">Secure</span>
                        <h2 className="text-title">Payment Method</h2>
                    </div>
                </div>
                <div className="flex items-center gap-4 p-6 bg-gray-50 rounded-lg">
                    <div className="flex h-14 w-20 items-center justify-center rounded-lg bg-gradient-to-br from-blue-600 to-purple-600">
                        <CreditCard className="h-7 w-7 text-white" strokeWidth={1.5} />
                    </div>
                    <div>
                        <p className="font-semibold text-lg">PhonePe / UPI / Cards</p>
                        <p className="text-sm text-gray-600">Secure payment via PhonePe</p>
                    </div>
                </div>
            </motion.div>

            {/* Billing History */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1.6 }}
                className="card-luxe p-8"
            >
                <div className="flex items-center gap-3 mb-6">
                    <motion.div
                        className="w-12 h-12 rounded-lg border border-black/10 bg-white flex items-center justify-center"
                        animate={{ rotate: [0, 5, -5, 0] }}
                        transition={{ duration: 3, repeat: Infinity, repeatDelay: 2 }}
                    >
                        <Calendar className="h-6 w-6 text-black" strokeWidth={1.5} />
                    </motion.div>
                    <div>
                        <span className="text-micro text-gray-400 block">History</span>
                        <h2 className="text-title">Billing History</h2>
                    </div>
                </div>
                <div className="space-y-3">
                    {billingHistory.length === 0 ? (
                        <motion.p
                            className="text-gray-500 text-center py-12"
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                        >
                            No billing history yet
                        </motion.p>
                    ) : (
                        billingHistory.map((invoice, index) => (
                            <motion.div
                                key={invoice.id}
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: 1.7 + index * 0.05 }}
                                whileHover={{ x: 5, backgroundColor: 'rgba(0,0,0,0.02)' }}
                                className="flex items-center justify-between p-5 bg-gray-50 rounded-lg transition-all duration-300 cursor-pointer"
                            >
                                <div className="flex items-center gap-4">
                                    <motion.div
                                        className="flex h-12 w-12 items-center justify-center rounded-lg bg-green-100"
                                        whileHover={{ scale: 1.1, rotate: 5 }}
                                    >
                                        <CheckCircle2 className="h-6 w-6 text-green-600" strokeWidth={2} />
                                    </motion.div>
                                    <div>
                                        <p className="font-semibold capitalize">{invoice.plan} Plan</p>
                                        <p className="text-sm text-gray-600">
                                            {new Date(invoice.created_at).toLocaleDateString('en-US', {
                                                month: 'long',
                                                day: 'numeric',
                                                year: 'numeric'
                                            })}
                                        </p>
                                    </div>
                                </div>
                                <div className="flex items-center gap-4">
                                    <p className="font-bold text-xl">₹{invoice.amount / 100}</p>
                                    <motion.button
                                        className="flex items-center gap-2 text-sm font-semibold text-black hover:underline"
                                        whileHover={{ scale: 1.05 }}
                                        whileTap={{ scale: 0.95 }}
                                    >
                                        <Download className="h-4 w-4" strokeWidth={2} />
                                        Invoice
                                    </motion.button>
                                </div>
                            </motion.div>
                        ))
                    )}
                </div>
            </motion.div>

            {/* Support Card */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1.8 }}
                className="card-luxe p-8 bg-gradient-to-br from-gray-50 to-white"
            >
                <div className="flex items-start gap-4">
                    <motion.div
                        className="flex h-14 w-14 items-center justify-center rounded-full bg-blue-100 flex-shrink-0"
                        animate={{
                            boxShadow: [
                                '0 0 0 0 rgba(59, 130, 246, 0.4)',
                                '0 0 0 10px rgba(59, 130, 246, 0)',
                            ],
                        }}
                        transition={{ duration: 2, repeat: Infinity }}
                    >
                        <AlertCircle className="h-7 w-7 text-blue-600" strokeWidth={2} />
                    </motion.div>
                    <div>
                        <h3 className="font-serif text-2xl font-bold mb-3">Need help with billing?</h3>
                        <p className="text-gray-700 mb-5 leading-relaxed">
                            Our support team is here to help with any billing questions or concerns.
                        </p>
                        <motion.a
                            href="mailto:billing@raptorflow.in"
                            className="inline-flex items-center gap-2 text-sm font-semibold text-black hover:underline group"
                            whileHover={{ x: 5 }}
                        >
                            Contact Support
                            <motion.div
                                animate={{ x: [0, 3, 0] }}
                                transition={{ duration: 1.5, repeat: Infinity }}
                            >
                                <ArrowRight className="h-4 w-4" strokeWidth={2} />
                            </motion.div>
                        </motion.a>
                    </div>
                </div>
            </motion.div>
        </div>
    );
}
