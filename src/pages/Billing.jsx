import { useState, useEffect } from 'react';
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
    Shield,
    Sparkles,
    Zap,
    Crown,
    HelpCircle
} from 'lucide-react';
import {
    HeroSection,
    LuxeCard,
    LuxeButton,
    LuxeBadge,
    staggerContainer,
    fadeInUp
} from '../components/ui/PremiumUI';
import { cn } from '../utils/cn';

export default function Billing() {
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
                icon: plan.name === 'ascent' ? Zap : plan.name === 'glide' ? Crown : Sparkles,
                key: plan.name // Store original key for API calls
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
        <motion.div
            className="max-w-[1440px] mx-auto px-6 py-8 space-y-8"
            initial="initial"
            animate="animate"
            exit="exit"
            variants={staggerContainer}
        >
            {/* Hero Section */}
            <motion.div variants={fadeInUp}>
                <HeroSection
                    title="Subscription & Billing"
                    subtitle="Manage your subscription, payment methods, and billing history."
                    metrics={[
                        { label: 'Current Plan', value: currentPlan.charAt(0).toUpperCase() + currentPlan.slice(1) },
                        { label: 'Status', value: subscription?.status === 'active' ? 'Active' : 'Inactive' },
                        { label: 'Next Billing', value: subscription?.current_period_end ? new Date(subscription.current_period_end).toLocaleDateString() : 'N/A' }
                    ]}
                />
            </motion.div>

            {/* Error Alert */}
            <AnimatePresence>
                {error && (
                    <motion.div
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="p-4 bg-red-50 border border-red-200 rounded-xl flex items-center gap-3 text-red-700"
                    >
                        <AlertCircle className="h-5 w-5" />
                        <p className="font-medium">{error}</p>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Current Plan Card */}
            <motion.div variants={fadeInUp}>
                <LuxeCard className="bg-neutral-900 text-white border-none p-8 relative overflow-hidden">
                    <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full blur-3xl -mr-32 -mt-32 pointer-events-none" />

                    <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
                        <div>
                            <div className="flex items-center gap-2 mb-4">
                                <Shield className="h-5 w-5 text-white/60" />
                                <span className="text-xs font-bold uppercase tracking-wider text-white/60">Current Plan</span>
                            </div>
                            <h2 className="font-display text-4xl font-medium mb-2 capitalize">
                                {currentPlan}
                            </h2>
                            {currentPlan === 'free' && (
                                <p className="text-white/70 max-w-md">
                                    No active subscription. Choose a plan below to unlock premium features.
                                </p>
                            )}
                        </div>
                        <div className="text-left md:text-right">
                            <p className="text-xs font-bold uppercase tracking-wider text-white/60 mb-1">Next billing date</p>
                            <p className="text-xl font-medium">
                                {subscription?.current_period_end
                                    ? new Date(subscription.current_period_end).toLocaleDateString('en-US', {
                                        month: 'long',
                                        day: 'numeric',
                                        year: 'numeric'
                                    })
                                    : 'N/A'
                                }
                            </p>
                        </div>
                    </div>
                </LuxeCard>
            </motion.div>

            {/* Plans Grid */}
            <motion.div variants={staggerContainer}>
                <div className="mb-6">
                    <h2 className="font-display text-2xl font-medium text-neutral-900">Available Plans</h2>
                    <p className="text-neutral-500">Choose the plan that fits your needs.</p>
                </div>

                <div className="grid gap-6 md:grid-cols-3">
                    {plans.map((plan) => {
                        const Icon = plan.icon
                        const isCurrent = currentPlan.toLowerCase() === plan.name.toLowerCase()

                        return (
                            <motion.div key={plan.name} variants={fadeInUp} className="h-full">
                                <LuxeCard
                                    className={cn(
                                        "h-full flex flex-col p-8 relative overflow-hidden transition-all duration-300",
                                        plan.popular ? "border-neutral-900 ring-1 ring-neutral-900" : "",
                                        isCurrent ? "bg-neutral-50" : "bg-white"
                                    )}
                                >
                                    {plan.popular && (
                                        <div className="absolute top-0 right-0 bg-neutral-900 text-white px-3 py-1 text-[10px] font-bold uppercase tracking-wider rounded-bl-xl">
                                            Most Popular
                                        </div>
                                    )}

                                    <div className="mb-6">
                                        <div className={cn(
                                            "w-12 h-12 rounded-xl flex items-center justify-center mb-4",
                                            plan.popular ? "bg-neutral-900 text-white" : "bg-neutral-100 text-neutral-900"
                                        )}>
                                            <Icon className="w-6 h-6" />
                                        </div>
                                        <h3 className="font-display text-2xl font-medium text-neutral-900 mb-2">{plan.name}</h3>
                                        <p className="text-sm text-neutral-600 h-10">{plan.description}</p>
                                    </div>

                                    <div className="mb-8">
                                        <div className="flex items-baseline gap-1">
                                            <span className="text-4xl font-display font-medium text-neutral-900">₹{plan.price}</span>
                                            <span className="text-neutral-500">/{plan.period}</span>
                                        </div>
                                    </div>

                                    <ul className="space-y-3 mb-8 flex-1">
                                        {plan.features.map((feature, i) => (
                                            <li key={i} className="flex items-start gap-3 text-sm text-neutral-700">
                                                <CheckCircle2 className="h-5 w-5 text-emerald-600 shrink-0" />
                                                <span>{feature}</span>
                                            </li>
                                        ))}
                                    </ul>

                                    <LuxeButton
                                        onClick={() => handleUpgrade(plan.name)}
                                        disabled={loadingPlan === plan.name || isCurrent}
                                        variant={isCurrent ? "secondary" : plan.popular ? "primary" : "outline"}
                                        className="w-full justify-center"
                                        isLoading={loadingPlan === plan.name}
                                    >
                                        {isCurrent ? (
                                            <>
                                                <CheckCircle2 className="h-4 w-4 mr-2" />
                                                Current Plan
                                            </>
                                        ) : (
                                            <>
                                                Subscribe to {plan.name}
                                                <ArrowRight className="h-4 w-4 ml-2" />
                                            </>
                                        )}
                                    </LuxeButton>
                                </LuxeCard>
                            </motion.div>
                        )
                    })}
                </div>
            </motion.div>

            {/* Billing History & Payment Method */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Payment Method */}
                <motion.div variants={fadeInUp}>
                    <LuxeCard className="h-full p-8">
                        <div className="flex items-center gap-3 mb-6">
                            <div className="w-10 h-10 rounded-lg bg-blue-50 flex items-center justify-center">
                                <CreditCard className="h-5 w-5 text-blue-600" />
                            </div>
                            <div>
                                <h2 className="font-display text-xl font-medium text-neutral-900">Payment Method</h2>
                                <p className="text-sm text-neutral-500">Secure payment via PhonePe</p>
                            </div>
                        </div>
                        <div className="p-4 bg-neutral-50 rounded-xl border border-neutral-100 flex items-center gap-4">
                            <div className="w-12 h-8 bg-white border border-neutral-200 rounded flex items-center justify-center">
                                <span className="text-xs font-bold text-neutral-900">UPI</span>
                            </div>
                            <div>
                                <p className="font-medium text-neutral-900">PhonePe / UPI / Cards</p>
                                <p className="text-xs text-neutral-500">Managed by PhonePe Gateway</p>
                            </div>
                        </div>
                    </LuxeCard>
                </motion.div>

                {/* Billing History */}
                <motion.div variants={fadeInUp}>
                    <LuxeCard className="h-full p-8">
                        <div className="flex items-center gap-3 mb-6">
                            <div className="w-10 h-10 rounded-lg bg-purple-50 flex items-center justify-center">
                                <Calendar className="h-5 w-5 text-purple-600" />
                            </div>
                            <div>
                                <h2 className="font-display text-xl font-medium text-neutral-900">Billing History</h2>
                                <p className="text-sm text-neutral-500">View past invoices</p>
                            </div>
                        </div>
                        <div className="space-y-2 max-h-[300px] overflow-y-auto pr-2 custom-scrollbar">
                            {billingHistory.length === 0 ? (
                                <div className="text-center py-8 text-neutral-500 text-sm">
                                    No billing history yet
                                </div>
                            ) : (
                                billingHistory.map((invoice) => (
                                    <div
                                        key={invoice.id}
                                        className="flex items-center justify-between p-4 bg-white border border-neutral-100 rounded-xl hover:border-neutral-300 transition-colors"
                                    >
                                        <div className="flex items-center gap-3">
                                            <div className="w-8 h-8 rounded-full bg-emerald-50 flex items-center justify-center">
                                                <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                                            </div>
                                            <div>
                                                <p className="font-medium text-sm capitalize">{invoice.plan} Plan</p>
                                                <p className="text-xs text-neutral-500">
                                                    {new Date(invoice.created_at).toLocaleDateString()}
                                                </p>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-3">
                                            <span className="font-medium text-sm">₹{invoice.amount / 100}</span>
                                            <button className="text-neutral-400 hover:text-neutral-900 transition-colors">
                                                <Download className="h-4 w-4" />
                                            </button>
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    </LuxeCard>
                </motion.div>
            </div>

            {/* Support Banner */}
            <motion.div variants={fadeInUp}>
                <LuxeCard className="p-8 bg-neutral-50 border-neutral-200">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-full bg-white border border-neutral-200 flex items-center justify-center shrink-0">
                            <HelpCircle className="h-6 w-6 text-neutral-400" />
                        </div>
                        <div>
                            <h3 className="font-display text-lg font-medium text-neutral-900">Need help with billing?</h3>
                            <p className="text-sm text-neutral-600 mb-1">
                                Our support team is here to help with any billing questions or concerns.
                            </p>
                            <a href="mailto:billing@raptorflow.in" className="text-sm font-bold text-neutral-900 hover:underline inline-flex items-center gap-1">
                                Contact Support <ArrowRight className="w-3 h-3" />
                            </a>
                        </div>
                    </div>
                </LuxeCard>
            </motion.div>
        </motion.div>
    );
}
