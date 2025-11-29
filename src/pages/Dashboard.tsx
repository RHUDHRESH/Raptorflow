import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useWorkspace } from '../context/WorkspaceContext';
import { positioningService, type PositioningRow } from '../services/positioningService';
import { Loader2, TrendingUp, Users, Zap, Target, Edit, ArrowRight, Sparkles, Layout } from 'lucide-react';
import {
    LuxeHeading,
    LuxeCard,
    LuxeButton,
    LuxeBadge,
    LuxeSkeleton,
    HeroSection,
    StatCard,
    EmptyState,
    fadeInUp,
    staggerContainer
} from '../components/ui/PremiumUI';
import { motion } from 'framer-motion';

export default function Dashboard() {
    const { currentWorkspace, loading: workspaceLoading } = useWorkspace();
    const navigate = useNavigate();

    // Positioning state
    const [positioning, setPositioning] = useState<PositioningRow | null>(null);
    const [isLoadingPositioning, setIsLoadingPositioning] = useState(true);
    const [positioningError, setPositioningError] = useState<string | null>(null);

    // Redirect to workspace selection if no workspace selected
    useEffect(() => {
        if (!workspaceLoading && !currentWorkspace) {
            navigate('/workspace', { replace: true });
        }
    }, [currentWorkspace, workspaceLoading, navigate]);

    // Fetch positioning data
    useEffect(() => {
        if (!currentWorkspace?.id) return;

        let isCancelled = false;
        setIsLoadingPositioning(true);
        setPositioningError(null);

        positioningService
            .getPositioningByWorkspaceId(currentWorkspace.id)
            .then((data) => {
                if (isCancelled) return;
                setPositioning(data);
            })
            .catch(() => {
                if (isCancelled) return;
                setPositioningError('Could not load positioning yet.');
            })
            .finally(() => {
                if (isCancelled) return;
                setIsLoadingPositioning(false);
            });

        return () => {
            isCancelled = true;
        };
    }, [currentWorkspace?.id]);

    // Show loading state while workspace is being determined
    if (workspaceLoading) {
        return (
            <div className="space-y-8 max-w-[1440px] mx-auto px-6 py-8">
                <LuxeSkeleton className="h-64 w-full rounded-2xl mb-8" />
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    {[...Array(4)].map((_, i) => (
                        <LuxeSkeleton key={i} className="h-48 rounded-xl" />
                    ))}
                </div>
            </div>
        );
    }

    // Show redirecting state if no workspace
    if (!currentWorkspace) {
        return (
            <div className="flex min-h-screen items-center justify-center bg-neutral-50">
                <div className="text-center">
                    <Loader2 className="h-12 w-12 animate-spin text-neutral-900 mx-auto mb-4" />
                    <p className="text-neutral-600 font-medium">Redirecting to workspace selection...</p>
                </div>
            </div>
        );
    }

    return (
        <motion.div
            className="space-y-12 max-w-[1440px] mx-auto px-6 py-8"
            initial="initial"
            animate="animate"
            variants={staggerContainer}
        >
            {/* Hero Section */}
            <motion.div variants={fadeInUp}>
                <HeroSection
                    title={`Welcome back, ${currentWorkspace.name}`}
                    subtitle="Here's what's happening across your campaigns and cohorts today."
                    metrics={[
                        { label: 'Active Campaigns', value: '3' },
                        { label: 'Total Reach', value: '12.5k' },
                        { label: 'Avg. Engagement', value: '4.2%' }
                    ]}
                    actions={
                        <>
                            <LuxeButton
                                onClick={() => navigate('/campaigns/new')}
                                className="bg-white text-neutral-900 hover:bg-neutral-100 border-none"
                            >
                                <Zap className="w-4 h-4 mr-2" />
                                New Campaign
                            </LuxeButton>
                            <LuxeButton
                                variant="outline"
                                onClick={() => navigate('/settings')}
                                className="text-white border-white/20 hover:bg-white/10"
                            >
                                Settings
                            </LuxeButton>
                        </>
                    }
                />
            </motion.div>

            {/* Stats Grid */}
            <motion.div
                variants={fadeInUp}
                className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
            >
                <StatCard
                    icon={Target}
                    label="Positioning"
                    value={positioning ? 'Defined' : 'Not Set'}
                    change={positioning ? 'Ready to scale' : 'Action needed'}
                    trend={positioning ? 'up' : 'neutral'}
                />
                <StatCard
                    icon={Users}
                    label="Cohorts"
                    value="0"
                    change="+0 this week"
                    trend="neutral"
                    sparklineData={[0, 0, 0, 0, 0, 0, 0]}
                />
                <StatCard
                    icon={Zap}
                    label="Campaigns"
                    value="0"
                    change="+0 this week"
                    trend="neutral"
                    sparklineData={[0, 0, 0, 0, 0, 0, 0]}
                />
                <StatCard
                    icon={TrendingUp}
                    label="Performance"
                    value="—"
                    change="No data yet"
                    trend="neutral"
                />
            </motion.div>

            {/* Brand Snapshot Section */}
            <motion.div variants={fadeInUp} className="space-y-6">
                <div className="flex items-center justify-between">
                    <LuxeHeading level={2}>Brand Snapshot</LuxeHeading>
                    {positioning && (
                        <LuxeButton variant="ghost" size="sm" onClick={() => navigate('/positioning')}>
                            <Edit className="w-4 h-4 mr-2" />
                            Edit Positioning
                        </LuxeButton>
                    )}
                </div>

                {isLoadingPositioning ? (
                    <LuxeCard className="grid grid-cols-1 lg:grid-cols-3 gap-8 h-[400px]">
                        <div className="lg:col-span-1 space-y-6 border-b lg:border-b-0 lg:border-r border-neutral-100 pb-6 lg:pb-0 lg:pr-6">
                            <LuxeSkeleton className="h-8 w-3/4 mb-4" />
                            <LuxeSkeleton className="h-20 w-full" />
                        </div>
                        <div className="lg:col-span-2 space-y-8">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                <LuxeSkeleton className="h-24 w-full" />
                                <LuxeSkeleton className="h-24 w-full" />
                            </div>
                        </div>
                    </LuxeCard>
                ) : positioningError ? (
                    <LuxeCard className="py-12">
                        <div className="text-center">
                            <p className="text-neutral-600">{positioningError}</p>
                        </div>
                    </LuxeCard>
                ) : !positioning ? (
                    <EmptyState
                        icon={Target}
                        title="Define Your Positioning"
                        description="Complete the Positioning workshop to unlock your Brand Snapshot. This foundation powers all your campaigns."
                        action={() => navigate('/positioning')}
                        actionLabel="Start Positioning Workshop"
                    />
                ) : (
                    <LuxeCard className="grid grid-cols-1 lg:grid-cols-3 gap-12 p-8">
                        <div className="lg:col-span-1 space-y-8 border-b lg:border-b-0 lg:border-r border-neutral-100 pb-8 lg:pb-0 lg:pr-8">
                            <div>
                                <h4 className="text-xs font-bold text-neutral-400 uppercase tracking-widest mb-3">Identity</h4>
                                <h3 className="font-display text-3xl font-medium text-neutral-900 leading-tight">{positioning.name}</h3>
                                <div className="mt-4">
                                    <LuxeBadge variant="neutral">
                                        Last updated: {new Date(positioning.updated_at).toLocaleDateString()}
                                    </LuxeBadge>
                                </div>
                            </div>

                            {positioning.category_frame && (
                                <div>
                                    <h4 className="text-xs font-bold text-neutral-400 uppercase tracking-widest mb-3">Category</h4>
                                    <p className="text-lg text-neutral-900 font-medium leading-relaxed">{positioning.category_frame}</p>
                                </div>
                            )}
                        </div>

                        <div className="lg:col-span-2 space-y-10">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
                                {positioning.who_statement && (
                                    <div>
                                        <h4 className="text-xs font-bold text-neutral-400 uppercase tracking-widest mb-4">Target Audience</h4>
                                        <p className="text-neutral-600 leading-relaxed text-lg">{positioning.who_statement}</p>
                                    </div>
                                )}

                                {positioning.differentiator && (
                                    <div>
                                        <h4 className="text-xs font-bold text-neutral-400 uppercase tracking-widest mb-4">Differentiator</h4>
                                        <p className="text-neutral-600 leading-relaxed text-lg">{positioning.differentiator}</p>
                                    </div>
                                )}
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-10 pt-8 border-t border-neutral-100">
                                {positioning.reason_to_believe && (
                                    <div>
                                        <h4 className="text-xs font-bold text-neutral-400 uppercase tracking-widest mb-4">Reason to Believe</h4>
                                        <p className="text-neutral-600 leading-relaxed text-lg">{positioning.reason_to_believe}</p>
                                    </div>
                                )}

                                {positioning.competitive_alternative && (
                                    <div>
                                        <h4 className="text-xs font-bold text-neutral-400 uppercase tracking-widest mb-4">Competitive Alternative</h4>
                                        <p className="text-neutral-600 leading-relaxed text-lg">{positioning.competitive_alternative}</p>
                                    </div>
                                )}
                            </div>
                        </div>
                    </LuxeCard>
                )}
            </motion.div>

            {/* Quick Actions */}
            <motion.div variants={fadeInUp} className="space-y-6">
                <LuxeHeading level={2}>Quick Actions</LuxeHeading>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <ActionCard
                        title="Define Positioning"
                        description="Complete the positioning workshop"
                        href="/positioning"
                        icon={Target}
                        delay={0.5}
                    />
                    <ActionCard
                        title="Create Cohorts"
                        description="Define your target audiences"
                        href="/cohorts"
                        icon={Users}
                        delay={0.6}
                    />
                    <ActionCard
                        title="Launch Campaign"
                        description="Start a new marketing campaign"
                        href="/campaigns"
                        icon={Zap}
                        delay={0.7}
                    />
                </div>
            </motion.div>
        </motion.div>
    );
}

function ActionCard({ title, description, href, icon: Icon, delay = 0 }: { title: string, description: string, href: string, icon: any, delay?: number }) {
    const navigate = useNavigate();

    return (
        <LuxeCard
            onClick={() => navigate(href)}
            hover={true}
            delay={delay}
            className="group h-full flex flex-col justify-between p-8"
        >
            <div>
                <div className="w-14 h-14 rounded-2xl bg-neutral-50 flex items-center justify-center mb-6 group-hover:bg-neutral-900 group-hover:text-white transition-colors duration-300">
                    <Icon className="w-7 h-7 text-neutral-400 group-hover:text-white transition-colors duration-300" />
                </div>
                <h3 className="font-display text-xl font-medium text-neutral-900 mb-3 group-hover:translate-x-1 transition-transform duration-300">{title}</h3>
                <p className="text-neutral-500 leading-relaxed">{description}</p>
            </div>
            <div className="mt-8 flex justify-end opacity-0 group-hover:opacity-100 transition-opacity duration-300 transform translate-y-2 group-hover:translate-y-0">
                <ArrowRight className="w-5 h-5 text-neutral-900" />
            </div>
        </LuxeCard>
    );
}
