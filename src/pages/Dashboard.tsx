import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useWorkspace } from '../context/WorkspaceContext';
import { positioningService, type PositioningRow } from '../services/positioningService';
import { Loader2, TrendingUp, Users, Zap, Target, Edit, ArrowRight } from 'lucide-react';
import { LuxeHeading, LuxeStat, LuxeCard, LuxeButton, LuxeEmptyState, LuxeBadge, LuxeSkeleton } from '../components/ui/PremiumUI';
import { motion } from 'framer-motion';
import { fadeInUp } from '../utils/animations';

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
            <div className="space-y-8">
                <LuxeSkeleton className="h-12 w-1/3 mb-8" />
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    {[...Array(4)].map((_, i) => (
                        <LuxeSkeleton key={i} className="h-32 rounded-xl" />
                    ))}
                </div>
                <LuxeSkeleton className="h-96 rounded-xl" />
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
        <div className="space-y-10">
            {/* Page Header */}
            <motion.div
                initial="hidden"
                animate="show"
                variants={fadeInUp}
                className="flex flex-col md:flex-row md:items-end justify-between gap-4"
            >
                <div>
                    <LuxeHeading level={1}>Dashboard</LuxeHeading>
                    <p className="text-neutral-500 mt-2 text-lg">
                        Welcome to <span className="font-semibold text-neutral-900">{currentWorkspace.name}</span>
                    </p>
                </div>
                <div className="flex gap-3">
                    <LuxeButton variant="secondary" size="sm" onClick={() => navigate('/settings')}>
                        Settings
                    </LuxeButton>
                    <LuxeButton size="sm" onClick={() => navigate('/campaigns/new')}>
                        <Zap className="w-4 h-4 mr-2" />
                        New Campaign
                    </LuxeButton>
                </div>
            </motion.div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <LuxeStat
                    icon={Target}
                    label="Positioning"
                    value={positioning ? 'Defined' : 'Not Set'}
                    delay={0.1}
                />
                <LuxeStat
                    icon={Users}
                    label="Cohorts"
                    value="0"
                    delay={0.2}
                />
                <LuxeStat
                    icon={Zap}
                    label="Campaigns"
                    value="0"
                    delay={0.3}
                />
                <LuxeStat
                    icon={TrendingUp}
                    label="Performance"
                    value="—"
                    delay={0.4}
                />
            </div>

            {/* Brand Snapshot Section */}
            <section>
                <div className="flex items-center justify-between mb-6">
                    <LuxeHeading level={3}>Brand Snapshot</LuxeHeading>
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
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 pt-6 border-t border-neutral-100">
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
                    <LuxeEmptyState
                        icon={Target}
                        title="Define Your Positioning"
                        description="Complete the Positioning workshop to unlock your Brand Snapshot. This foundation powers all your campaigns."
                        action={
                            <LuxeButton onClick={() => navigate('/positioning')}>
                                Start Positioning Workshop <ArrowRight className="w-4 h-4 ml-2" />
                            </LuxeButton>
                        }
                    />
                ) : (
                    <LuxeCard className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                        <div className="lg:col-span-1 space-y-6 border-b lg:border-b-0 lg:border-r border-neutral-100 pb-6 lg:pb-0 lg:pr-6">
                            <div>
                                <h4 className="text-xs font-bold text-neutral-400 uppercase tracking-widest mb-2">Identity</h4>
                                <h3 className="font-serif text-2xl font-bold text-neutral-900">{positioning.name}</h3>
                                <div className="mt-2">
                                    <LuxeBadge variant="neutral">
                                        Last updated: {new Date(positioning.updated_at).toLocaleDateString()}
                                    </LuxeBadge>
                                </div>
                            </div>

                            {positioning.category_frame && (
                                <div>
                                    <h4 className="text-xs font-bold text-neutral-400 uppercase tracking-widest mb-2">Category</h4>
                                    <p className="text-neutral-900 font-medium leading-relaxed">{positioning.category_frame}</p>
                                </div>
                            )}
                        </div>

                        <div className="lg:col-span-2 space-y-8">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                {positioning.who_statement && (
                                    <div>
                                        <h4 className="text-xs font-bold text-neutral-400 uppercase tracking-widest mb-3">Target Audience</h4>
                                        <p className="text-neutral-700 leading-relaxed">{positioning.who_statement}</p>
                                    </div>
                                )}

                                {positioning.differentiator && (
                                    <div>
                                        <h4 className="text-xs font-bold text-neutral-400 uppercase tracking-widest mb-3">Differentiator</h4>
                                        <p className="text-neutral-700 leading-relaxed">{positioning.differentiator}</p>
                                    </div>
                                )}
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 pt-6 border-t border-neutral-100">
                                {positioning.reason_to_believe && (
                                    <div>
                                        <h4 className="text-xs font-bold text-neutral-400 uppercase tracking-widest mb-3">Reason to Believe</h4>
                                        <p className="text-neutral-700 leading-relaxed">{positioning.reason_to_believe}</p>
                                    </div>
                                )}

                                {positioning.competitive_alternative && (
                                    <div>
                                        <h4 className="text-xs font-bold text-neutral-400 uppercase tracking-widest mb-3">Competitive Alternative</h4>
                                        <p className="text-neutral-700 leading-relaxed">{positioning.competitive_alternative}</p>
                                    </div>
                                )}
                            </div>
                        </div>
                    </LuxeCard>
                )}
            </section>

            {/* Quick Actions */}
            <section>
                <LuxeHeading level={3} className="mb-6">Quick Actions</LuxeHeading>

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
            </section>
        </div>
    );
}

function ActionCard({ title, description, href, icon: Icon, delay = 0 }: { title: string, description: string, href: string, icon: any, delay?: number }) {
    const navigate = useNavigate();

    return (
        <LuxeCard
            onClick={() => navigate(href)}
            hover={true}
            delay={delay}
            className="group h-full flex flex-col justify-between"
        >
            <div>
                <div className="w-12 h-12 rounded-xl bg-neutral-50 flex items-center justify-center mb-4 group-hover:bg-neutral-900 group-hover:text-white transition-colors duration-300">
                    <Icon className="w-6 h-6 text-neutral-400 group-hover:text-white transition-colors duration-300" />
                </div>
                <h3 className="font-serif text-lg font-bold text-neutral-900 mb-2 group-hover:translate-x-1 transition-transform duration-300">{title}</h3>
                <p className="text-sm text-neutral-500 leading-relaxed">{description}</p>
            </div>
            <div className="mt-6 flex justify-end opacity-0 group-hover:opacity-100 transition-opacity duration-300 transform translate-y-2 group-hover:translate-y-0">
                <ArrowRight className="w-5 h-5 text-neutral-900" />
            </div>
        </LuxeCard>
    );
}
