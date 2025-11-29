import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
    ArrowLeft,
    CheckCircle2,
    AlertTriangle,
    Play,
    FileText,
    BarChart3,
    Clock,
    ExternalLink,
    Wand2,
    Send
} from 'lucide-react';
import { PageHeader, LuxeHeading, LuxeButton, LuxeCard, LuxeBadge, LuxeTabs } from '../components/ui/PremiumUI';
import { pageTransition, fadeInUp } from '../utils/animations';
import { moveService } from '../services/moveService';
import { campaignService } from '../services/campaignService';
import { toast } from '../components/Toast';

export default function MoveDetail() {
    const { moveId } = useParams();
    const [move, setMove] = useState(null);
    const [assets, setAssets] = useState([]);
    const [loading, setLoading] = useState(true);
    const [preflightResult, setPreflightResult] = useState(null);
    const [activeTab, setActiveTab] = useState('overview');

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                // Mock fetching if API fails or returns null
                // In reality, moveService should return the move
                // const moveData = await moveService.getMove(moveId);
                // setMove(moveData);

                // Fetch assets
                // const assetsData = await moveService.getAssets(moveId);
                // setAssets(assetsData);

                // Mock Data for now to show UI
                setMove({
                    id: moveId,
                    name: 'Authority Sprint – Week 1-2',
                    status: 'planned',
                    move_type: 'authority',
                    journey_stage_from: 'problem_aware',
                    journey_stage_to: 'solution_aware',
                    start_date: '2025-01-10',
                    end_date: '2025-01-24',
                    campaign: { id: 'c1', name: 'Q1 Enterprise CTO Conversion' },
                    cohort: { name: 'Enterprise CTOs' },
                    message_variant: 'Strategic OS vs random hacks'
                });

                setAssets([
                    { id: 'a1', name: 'Authority Post 1', format: 'post', channel: 'linkedin', status: 'draft' },
                    { id: 'a2', name: 'Value Add Email', format: 'email', channel: 'email', status: 'published', metrics: { opens: 450, clicks: 120 } }
                ]);

            } catch (error) {
                console.error(error);
                toast.error('Failed to load move details');
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [moveId]);

    const handlePreflight = async () => {
        // Mock preflight call
        const result = {
            status: 'warn',
            issues: [
                { code: 'EMAIL_LIST_SIZE', message: 'Email list < 1000', severity: 'warn', recommendation: 'Add more contacts or expect lower volume.' }
            ]
        };
        setPreflightResult(result);
        toast('Pre-flight check complete');
    };

    const handleGenerateAssets = async () => {
        toast.success('Generating assets...');
        // In real app, call API
        setTimeout(() => {
            setAssets(prev => [...prev, { id: 'a3', name: 'Generated Post', format: 'post', channel: 'linkedin', status: 'draft' }]);
        }, 1500);
    };

    if (loading) return <div className="p-10 text-center">Loading...</div>;
    if (!move) return <div className="p-10 text-center">Move not found</div>;

    return (
        <motion.div
            className="max-w-6xl mx-auto px-6 py-8 space-y-8"
            initial="initial"
            animate="animate"
            exit="exit"
            variants={pageTransition}
        >
            {/* Header (Task 14) */}
            <PageHeader
                backUrl={`/campaigns/${move.campaign?.id}`}
                title={move.name}
                subtitle={
                    <span>
                        Goal: Move <span className="font-medium text-neutral-900">{move.cohort?.name}</span> from <span className="font-medium text-neutral-900">{move.journey_stage_from}</span> → <span className="font-medium text-neutral-900">{move.journey_stage_to}</span>
                    </span>
                }
                action={
                    <div className="flex items-center gap-3">
                        <LuxeBadge variant={
                            move.status === 'active' ? 'success' :
                                move.status === 'completed' ? 'info' : 'neutral'
                        } className="px-3 py-1">
                            {move.status}
                        </LuxeBadge>

                        {move.status === 'planned' && (
                            <LuxeButton onClick={handlePreflight} variant="secondary" icon={CheckCircle2}>Run Pre-flight</LuxeButton>
                        )}
                        {move.status === 'ready' && (
                            <LuxeButton icon={Play}>Launch Move</LuxeButton>
                        )}
                    </div>
                }
            />

            {/* Tabs (Task 15) */}
            <div className="border-b border-neutral-200 pb-1">
                <LuxeTabs
                    tabs={[
                        { id: 'overview', label: 'Overview' },
                        { id: 'assets', label: 'Assets' },
                        { id: 'performance', label: 'Performance' }
                    ]}
                    activeTab={activeTab}
                    onChange={setActiveTab}
                    className="bg-transparent p-0 gap-6"
                />
            </div>

            {/* Tab Content */}
            <div className="min-h-[400px] pt-6">
                {activeTab === 'overview' && (
                    <motion.div variants={fadeInUp} className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                        {/* Left: Intent & Strategy */}
                        <div className="lg:col-span-2 space-y-8">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                {/* Move Intent Card */}
                                <LuxeCard title="Move Intent" className="h-full">
                                    <div className="space-y-4">
                                        <div>
                                            <label className="text-xs font-bold text-neutral-400 uppercase tracking-wider block mb-1">Campaign</label>
                                            <Link to={`/campaigns/${move.campaign?.id}`} className="text-sm font-medium text-neutral-900 hover:underline">
                                                {move.campaign?.name}
                                            </Link>
                                        </div>
                                        <div>
                                            <label className="text-xs font-bold text-neutral-400 uppercase tracking-wider block mb-1">Timeline</label>
                                            <div className="flex items-center gap-2 text-sm font-medium text-neutral-900">
                                                <Clock className="w-4 h-4 text-neutral-400" />
                                                {new Date(move.start_date).toLocaleDateString()} — {new Date(move.end_date).toLocaleDateString()}
                                            </div>
                                        </div>
                                        <div>
                                            <label className="text-xs font-bold text-neutral-400 uppercase tracking-wider block mb-1">Move Type</label>
                                            <span className="text-sm font-medium text-neutral-900 capitalize">{move.move_type}</span>
                                        </div>
                                    </div>
                                </LuxeCard>

                                {/* Target & Message Card */}
                                <LuxeCard title="Target & Message" className="h-full">
                                    <div className="space-y-6">
                                        <div>
                                            <label className="text-xs font-bold text-neutral-400 uppercase tracking-wider block mb-1">Cohort</label>
                                            <LuxeBadge variant="neutral" icon={Clock} className="py-1 px-2">
                                                {move.cohort?.name}
                                            </LuxeBadge>
                                        </div>
                                        <div>
                                            <label className="text-xs font-bold text-neutral-400 uppercase tracking-wider block mb-2">Single Minded Proposition</label>
                                            <p className="text-lg font-serif italic text-neutral-900 leading-relaxed">
                                                "{move.message_variant}"
                                            </p>
                                        </div>
                                    </div>
                                </LuxeCard>
                            </div>
                        </div>

                        {/* Right: Pre-flight Checklist */}
                        <div>
                            <LuxeCard title="Pre-flight Checklist" className="h-full bg-neutral-50/50 border-dashed">
                                {preflightResult ? (
                                    <div className="space-y-4">
                                        <div className={`p-4 rounded border ${preflightResult.status === 'pass'
                                                ? 'bg-neutral-100 text-neutral-800 border-neutral-200'
                                                : 'bg-neutral-50 text-neutral-600 border-neutral-100'
                                            }`}>
                                            <div className="flex items-center gap-2 mb-1">
                                                {preflightResult.status === 'pass' ? <CheckCircle2 className="w-5 h-5" /> : <AlertTriangle className="w-5 h-5" />}
                                                <span className="font-bold uppercase text-xs tracking-wider">Status: {preflightResult.status}</span>
                                            </div>
                                        </div>

                                        <div className="space-y-0 divide-y divide-neutral-100 border-t border-b border-neutral-100">
                                            {preflightResult.issues.map((issue, i) => (
                                                <div key={i} className="py-3">
                                                    <div className="flex gap-3">
                                                        {issue.severity === 'fail'
                                                            ? <AlertTriangle className="w-4 h-4 text-neutral-700 shrink-0 mt-0.5" />
                                                            : <CheckCircle2 className="w-4 h-4 text-neutral-900 shrink-0 mt-0.5" />
                                                        }
                                                        <div>
                                                            <p className="text-sm font-medium text-neutral-900">{issue.message}</p>
                                                            {issue.recommendation && (
                                                                <p className="text-xs text-neutral-500 mt-1">{issue.recommendation}</p>
                                                            )}
                                                        </div>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                ) : (
                                    <div className="flex flex-col items-center justify-center h-40 text-center">
                                        <p className="text-sm text-neutral-500 mb-4">Validation not run yet.</p>
                                        <LuxeButton size="sm" variant="secondary" onClick={handlePreflight} icon={CheckCircle2}>Run Check</LuxeButton>
                                    </div>
                                )}
                            </LuxeCard>
                        </div>
                    </motion.div>
                )}

                {activeTab === 'assets' && (
                    <motion.div variants={fadeInUp} className="space-y-6">
                        <div className="flex justify-between items-center">
                            <div>
                                <h3 className="font-display text-lg font-medium text-neutral-900">Required Assets</h3>
                                <p className="text-sm text-neutral-500">Content needed to execute this move.</p>
                            </div>
                            <LuxeButton icon={Wand2} onClick={handleGenerateAssets}>Generate Briefs</LuxeButton>
                        </div>

                        <div className="bg-white border border-neutral-200 rounded-lg overflow-hidden">
                            <table className="w-full text-left text-sm">
                                <thead className="bg-neutral-50 border-b border-neutral-200">
                                    <tr>
                                        <th className="px-6 py-3 font-bold text-neutral-400 uppercase tracking-wider text-xs">Asset Name</th>
                                        <th className="px-6 py-3 font-bold text-neutral-400 uppercase tracking-wider text-xs">Channel</th>
                                        <th className="px-6 py-3 font-bold text-neutral-400 uppercase tracking-wider text-xs">Status</th>
                                        <th className="px-6 py-3 font-bold text-neutral-400 uppercase tracking-wider text-xs text-right">Actions</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-neutral-100">
                                    {assets.map(asset => (
                                        <tr key={asset.id} className="group hover:bg-neutral-50 transition-colors">
                                            <td className="px-6 py-4">
                                                <div className="flex items-center gap-3">
                                                    <div className="w-8 h-8 rounded bg-neutral-100 flex items-center justify-center text-neutral-500">
                                                        {asset.format === 'post' ? <FileText className="w-4 h-4" /> :
                                                            asset.format === 'email' ? <Send className="w-4 h-4" /> : <FileText className="w-4 h-4" />}
                                                    </div>
                                                    <span className="font-medium text-neutral-900">{asset.name}</span>
                                                </div>
                                            </td>
                                            <td className="px-6 py-4">
                                                <span className="capitalize text-neutral-600">{asset.channel}</span>
                                            </td>
                                            <td className="px-6 py-4">
                                                <LuxeBadge variant={asset.status === 'published' ? 'success' : 'neutral'} className="capitalize">
                                                    {asset.status}
                                                </LuxeBadge>
                                            </td>
                                            <td className="px-6 py-4 text-right">
                                                <div className="flex justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                                    <button className="text-neutral-400 hover:text-neutral-900 font-medium text-xs transition-colors">View Brief</button>
                                                    <button className="text-neutral-400 hover:text-neutral-900 transition-colors"><ExternalLink className="w-4 h-4" /></button>
                                                </div>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                            {assets.length === 0 && (
                                <div className="p-12 text-center text-neutral-500">No assets generated yet.</div>
                            )}
                        </div>
                    </motion.div>
                )}

                {activeTab === 'performance' && (
                    <motion.div variants={fadeInUp} className="space-y-8">
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                            <LuxeCard className="p-6">
                                <div className="text-sm text-neutral-500 font-medium mb-2">Primary KPI</div>
                                <div className="text-3xl font-display font-medium text-neutral-900">
                                    {move.status === 'active' ? '12' : '0'} <span className="text-lg text-neutral-400">/ 50</span>
                                </div>
                                <div className="text-xs text-neutral-400 mt-1 uppercase tracking-wider">Qualified Leads</div>
                            </LuxeCard>

                            <LuxeCard className="p-6">
                                <div className="text-sm text-neutral-500 font-medium mb-2">Efficiency</div>
                                <div className="text-3xl font-display font-medium text-neutral-900">$450</div>
                                <div className="text-xs text-neutral-400 mt-1 uppercase tracking-wider">Cost Per Lead</div>
                            </LuxeCard>

                            <LuxeCard className="p-6">
                                <div className="text-sm text-neutral-500 font-medium mb-2">Engagement</div>
                                <div className="text-3xl font-display font-medium text-neutral-900">4.2%</div>
                                <div className="text-xs text-neutral-400 mt-1 uppercase tracking-wider">Avg Click Rate</div>
                            </LuxeCard>
                        </div>

                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                            <LuxeCard title="Stage Shift Velocity">
                                <div className="h-64 bg-neutral-50 rounded border border-neutral-100 flex items-center justify-center">
                                    <span className="text-neutral-400 text-sm italic">Funnel Visualization Placeholder</span>
                                </div>
                            </LuxeCard>

                            <LuxeCard title="Asset Leaderboard">
                                <div className="space-y-4">
                                    {assets.slice(0, 3).map((asset, i) => (
                                        <div key={asset.id} className="flex items-center justify-between p-3 border border-neutral-100 rounded bg-neutral-50/50">
                                            <div className="flex items-center gap-3">
                                                <div className="font-bold text-neutral-300 text-lg">#{i + 1}</div>
                                                <div className="text-sm font-medium text-neutral-900">{asset.name}</div>
                                            </div>
                                            <div className="text-sm font-bold text-neutral-900">
                                                {asset.metrics?.clicks || 0} <span className="text-neutral-400 font-normal text-xs">clicks</span>
                                            </div>
                                        </div>
                                    ))}
                                    {assets.length === 0 && <div className="text-sm text-neutral-400 italic">No data available</div>}
                                </div>
                            </LuxeCard>
                        </div>
                    </motion.div>
                )}
            </div>
        </motion.div>
    );
}
