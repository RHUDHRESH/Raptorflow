import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Plus, 
  MoreHorizontal, 
  Calendar,
  Target,
  Zap,
  TrendingUp,
  ChevronRight,
  Users,
  BarChart3
} from 'lucide-react'

const CampaignCard = ({ campaign, delay }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay }}
      className="group bg-zinc-900/50 border border-white/5 rounded-xl overflow-hidden hover:border-amber-500/30 transition-all cursor-pointer"
    >
      {/* Header with gradient */}
      <div className={`h-2 ${campaign.gradient}`} />
      
      <div className="p-5">
        <div className="flex items-start justify-between mb-4">
          <div>
            <span className={`px-2 py-1 rounded text-xs font-medium ${
              campaign.status === 'active' 
                ? 'bg-emerald-500/10 text-emerald-400'
                : campaign.status === 'planning'
                ? 'bg-amber-500/10 text-amber-400'
                : 'bg-white/5 text-white/40'
            }`}>
              {campaign.status}
            </span>
          </div>
          <button className="opacity-0 group-hover:opacity-100 p-1 hover:bg-white/10 rounded transition-all">
            <MoreHorizontal className="w-4 h-4 text-white/40" />
          </button>
        </div>

        <h3 className="text-lg text-white font-medium mb-2">{campaign.name}</h3>
        <p className="text-sm text-white/40 mb-4">{campaign.objective}</p>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-3 mb-4">
          <div className="text-center p-2 bg-white/5 rounded-lg">
            <p className="text-lg text-white font-light">{campaign.moves}</p>
            <p className="text-[10px] text-white/40 uppercase tracking-wider">Moves</p>
          </div>
          <div className="text-center p-2 bg-white/5 rounded-lg">
            <p className="text-lg text-white font-light">{campaign.cohorts}</p>
            <p className="text-[10px] text-white/40 uppercase tracking-wider">Cohorts</p>
          </div>
          <div className="text-center p-2 bg-white/5 rounded-lg">
            <p className="text-lg text-white font-light">{campaign.progress}%</p>
            <p className="text-[10px] text-white/40 uppercase tracking-wider">Progress</p>
          </div>
        </div>

        {/* Progress bar */}
        <div className="mb-4">
          <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
            <div 
              className={`h-full rounded-full ${campaign.gradient}`}
              style={{ width: `${campaign.progress}%` }}
            />
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between pt-4 border-t border-white/5">
          <div className="flex items-center gap-2 text-xs text-white/40">
            <Calendar className="w-3.5 h-3.5" />
            <span>{campaign.dateRange}</span>
          </div>
          <ChevronRight className="w-4 h-4 text-white/20 group-hover:text-amber-400 transition-colors" />
        </div>
      </div>
    </motion.div>
  )
}

const Campaigns = () => {
  const campaigns = [
    {
      id: 1,
      name: 'Q1 Awareness',
      objective: 'Build brand awareness and establish thought leadership among tech founders',
      status: 'active',
      moves: 8,
      cohorts: 3,
      progress: 67,
      dateRange: 'Jan 1 - Mar 31',
      gradient: 'bg-gradient-to-r from-amber-500 to-orange-500'
    },
    {
      id: 2,
      name: 'Product Launch',
      objective: 'Coordinated launch across all channels with community support and PR',
      status: 'planning',
      moves: 12,
      cohorts: 4,
      progress: 25,
      dateRange: 'Feb 1 - Feb 28',
      gradient: 'bg-gradient-to-r from-violet-500 to-purple-500'
    },
    {
      id: 3,
      name: 'Growth Engine',
      objective: 'Systematic acquisition and activation of new users through content and partnerships',
      status: 'active',
      moves: 6,
      cohorts: 2,
      progress: 45,
      dateRange: 'Ongoing',
      gradient: 'bg-gradient-to-r from-emerald-500 to-teal-500'
    },
    {
      id: 4,
      name: 'Social Proof',
      objective: 'Collect and amplify customer success stories and testimonials',
      status: 'completed',
      moves: 4,
      cohorts: 1,
      progress: 100,
      dateRange: 'Nov 1 - Nov 30',
      gradient: 'bg-gradient-to-r from-blue-500 to-cyan-500'
    },
  ]

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h1 className="text-3xl font-light text-white">Campaigns</h1>
          <p className="text-white/40 mt-1">
            Strategic initiatives that group your moves
          </p>
        </motion.div>

        <motion.button
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="flex items-center gap-2 px-5 py-2.5 bg-amber-500 hover:bg-amber-400 text-black font-medium rounded-lg transition-colors"
        >
          <Plus className="w-4 h-4" />
          New Campaign
        </motion.button>
      </div>

      {/* Stats overview */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8"
      >
        {[
          { icon: Target, label: 'Active Campaigns', value: '3' },
          { icon: Zap, label: 'Total Moves', value: '30' },
          { icon: Users, label: 'Cohorts Engaged', value: '5' },
          { icon: TrendingUp, label: 'Avg Progress', value: '59%' },
        ].map((stat, i) => (
          <div key={i} className="bg-zinc-900/50 border border-white/5 rounded-xl p-5">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-amber-500/10 rounded-lg">
                <stat.icon className="w-5 h-5 text-amber-400" strokeWidth={1.5} />
              </div>
              <div>
                <p className="text-2xl font-light text-white">{stat.value}</p>
                <p className="text-xs text-white/40">{stat.label}</p>
              </div>
            </div>
          </div>
        ))}
      </motion.div>

      {/* Campaigns grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {campaigns.map((campaign, index) => (
          <CampaignCard key={campaign.id} campaign={campaign} delay={0.15 + index * 0.05} />
        ))}
      </div>

      {/* Empty state for new campaign */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
        className="mt-6 border-2 border-dashed border-white/10 rounded-xl p-8 text-center hover:border-amber-500/30 transition-colors cursor-pointer group"
      >
        <div className="inline-flex items-center justify-center w-12 h-12 bg-white/5 rounded-xl mb-4 group-hover:bg-amber-500/10 transition-colors">
          <Plus className="w-6 h-6 text-white/40 group-hover:text-amber-400" />
        </div>
        <p className="text-white/60 group-hover:text-white transition-colors">Create a new campaign</p>
        <p className="text-sm text-white/30 mt-1">Group related moves under a strategic initiative</p>
      </motion.div>
    </div>
  )
}

export default Campaigns

