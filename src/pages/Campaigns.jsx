import { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Plus, Play, Pause, MoreVertical, Calendar, Target, Users } from 'lucide-react';
import { cn } from '../utils/cn';

// Mock campaigns data
const MOCK_CAMPAIGNS = [
    {
        id: '1',
        name: 'Q1 Enterprise CTO Conversion',
        status: 'active',
        objective: 'Conversion',
        start_date: '2024-01-01',
        end_date: '2024-03-31',
        target_cohorts: ['Enterprise CTOs', 'Tech VPs'],
        progress: 65,
    },
    {
        id: '2',
        name: 'Startup Founder Awareness Sprint',
        status: 'draft',
        objective: 'Awareness',
        start_date: '2024-02-01',
        end_date: '2024-02-28',
        target_cohorts: ['Startup Founders'],
        progress: 0,
    },
];

export default function Campaigns() {
    const [campaigns, setCampaigns] = useState(MOCK_CAMPAIGNS);

    return (
        <div className="space-y-8">
            {/* Page Title */}
            <div>
                <h1 className="font-serif text-4xl text-neutral-900 mb-2">Campaigns</h1>
                <div className="flex items-center justify-between">
                    <p className="text-neutral-600">Strategic campaigns that orchestrate your marketing activities</p>
                    <Link
                        to="/campaigns/new"
                        className="flex items-center gap-2 px-4 py-2 bg-neutral-900 text-white rounded-lg text-sm font-medium hover:bg-neutral-800"
                    >
                        <Plus className="w-4 h-4" />
                        New Campaign
                    </Link>
                </div>
            </div>

            {/* Campaigns List */}
            {campaigns.length === 0 ? (
                <div className="border-2 border-dashed border-neutral-200 rounded-xl p-12 text-center bg-white">
                    <Target className="w-12 h-12 text-neutral-300 mx-auto mb-4" />
                    <h3 className="font-semibold text-neutral-900 mb-2">No campaigns yet</h3>
                    <p className="text-neutral-600 mb-4">Create your first strategic campaign to get started</p>
                    <Link
                        to="/campaigns/new"
                        className="inline-flex items-center gap-2 px-4 py-2 bg-neutral-900 text-white rounded-lg text-sm font-medium hover:bg-neutral-800"
                    >
                        <Plus className="w-4 h-4" />
                        Create Campaign
                    </Link>
                </div>
            ) : (
                <div className="grid grid-cols-1 gap-4">
                    {campaigns.map((campaign) => (
                        <motion.div
                            key={campaign.id}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="bg-white border border-neutral-200 rounded-xl p-6 hover:border-neutral-300 transition-colors"
                        >
                            <div className="flex items-start justify-between mb-4">
                                <div className="flex-1">
                                    <div className="flex items-center gap-3 mb-2">
                                        <Link to={`/strategy/campaigns/${campaign.id}`} className="font-semibold text-neutral-900 text-lg hover:underline">{campaign.name}</Link>
                                        <span className={cn(
                                            "px-2 py-0.5 text-xs rounded",
                                            campaign.status === 'active' ? "bg-green-100 text-green-700" :
                                                campaign.status === 'paused' ? "bg-amber-100 text-amber-700" :
                                                    "bg-neutral-100 text-neutral-600"
                                        )}>
                                            {campaign.status}
                                        </span>
                                    </div>
                                    <div className="flex items-center gap-4 text-sm text-neutral-600">
                                        <div className="flex items-center gap-1">
                                            <Target className="w-4 h-4" />
                                            {campaign.objective}
                                        </div>
                                        <div className="flex items-center gap-1">
                                            <Calendar className="w-4 h-4" />
                                            {new Date(campaign.start_date).toLocaleDateString()} - {new Date(campaign.end_date).toLocaleDateString()}
                                        </div>
                                        <div className="flex items-center gap-1">
                                            <Users className="w-4 h-4" />
                                            {campaign.target_cohorts.length} cohorts
                                        </div>
                                    </div>
                                </div>
                                <div className="flex items-center gap-2">
                                    {campaign.status === 'active' && (
                                        <button className="p-2 hover:bg-neutral-100 rounded-lg">
                                            <Pause className="w-4 h-4 text-neutral-600" />
                                        </button>
                                    )}
                                    {campaign.status === 'draft' && (
                                        <button className="p-2 hover:bg-neutral-100 rounded-lg">
                                            <Play className="w-4 h-4 text-neutral-600" />
                                        </button>
                                    )}
                                    <button className="p-2 hover:bg-neutral-100 rounded-lg">
                                        <MoreVertical className="w-4 h-4 text-neutral-600" />
                                    </button>
                                </div>
                            </div>

                            {campaign.status === 'active' && (
                                <div>
                                    <div className="flex items-center justify-between text-xs text-neutral-500 mb-1">
                                        <span>Progress</span>
                                        <span>{campaign.progress}%</span>
                                    </div>
                                    <div className="w-full h-2 bg-neutral-100 rounded-full overflow-hidden">
                                        <div
                                            className="h-full bg-neutral-900 transition-all duration-500"
                                            style={{ width: `${campaign.progress}%` }}
                                        />
                                    </div>
                                </div>
                            )}
                        </motion.div>
                    ))}
                </div>
            )}
        </div>
    );
}
