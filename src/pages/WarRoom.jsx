/**
 * War Room - Integrated with Real Supabase Data
 * Command Center for kinetic operations with real-time sprint and move data
 */

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { Target, Calendar, Users, TrendingUp, AlertCircle } from 'lucide-react';
import { useSprints, useMoves, useICPs } from '../hooks/useMoveSystem';
import { sprintService } from '../lib/services/sprint-service';
import {
  HeroSection,
  LuxeCard,
  LuxeBadge,
  LuxeButton,
  EmptyState,
  staggerContainer,
  fadeInUp
} from '../components/ui/PremiumUI';
import { cn } from '../utils/cn';

export default function WarRoomIntegrated() {
  const { activeSprint, sprints, loading: sprintsLoading } = useSprints();
  const { moves, loading: movesLoading } = useMoves();
  const { icps } = useICPs();
  const [anomalies, setAnomalies] = useState([]);

  const loading = sprintsLoading || movesLoading;

  // Get moves for active sprint
  const sprintMoves = moves.filter(m => m.sprint_id === activeSprint?.id);

  // Group moves by status (simplified OODA grouping)
  const movesByPhase = {
    planning: sprintMoves.filter(m => m.status === 'Planning'),
    observe: sprintMoves.filter(m => m.status === 'OODA_Observe'),
    orient: sprintMoves.filter(m => m.status === 'OODA_Orient'),
    decide: sprintMoves.filter(m => m.status === 'OODA_Decide'),
    act: sprintMoves.filter(m => m.status === 'OODA_Act'),
    complete: sprintMoves.filter(m => m.status === 'Complete'),
  };

  // Get capacity data
  const capacityPercentage = activeSprint
    ? sprintService.getCapacityPercentage(activeSprint)
    : 0;

  const capacityStatus =
    capacityPercentage < 70 ? 'healthy' :
      capacityPercentage < 90 ? 'warning' : 'critical';

  const getHealthColor = (health) => {
    const colors = {
      green: 'bg-emerald-500',
      amber: 'bg-amber-500',
      red: 'bg-red-500',
    };
    return colors[health] || colors.green;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-neutral-200 border-t-neutral-900 rounded-full animate-spin mx-auto mb-4" />
          <p className="text-neutral-600">Loading War Room...</p>
        </div>
      </div>
    );
  }

  if (!activeSprint) {
    return (
      <motion.div
        className="max-w-[1440px] mx-auto px-6 py-8"
        initial="initial"
        animate="animate"
        variants={staggerContainer}
      >
        <LuxeCard className="p-12">
          <EmptyState
            icon={Target}
            title="No Active Sprint"
            description="Create a sprint to start planning your moves"
            action={
              <Link to="/sprints/new">
                <LuxeButton>Create Sprint</LuxeButton>
              </Link>
            }
          />
        </LuxeCard>
      </motion.div>
    );
  }

  return (
    <motion.div
      className="max-w-[1440px] mx-auto px-6 py-8 space-y-8"
      initial="initial"
      animate="animate"
      exit="exit"
      variants={staggerContainer}
    >
      {/* Header */}
      <motion.div variants={fadeInUp}>
        <HeroSection
          title="War Room"
          subtitle="Kinetic operations dashboard. Deploy moves, monitor capacity, and coordinate execution."
          metrics={[
            { label: 'Active Moves', value: sprintMoves.length.toString() },
            { label: 'Capacity', value: `${capacityPercentage}%` },
            { label: 'Alerts', value: anomalies.length.toString() }
          ]}
        />
      </motion.div>

      {/* Operational Context */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {/* Active Sprint */}
        <motion.div variants={fadeInUp}>
          <LuxeCard className="p-6">
            <div className="flex items-start justify-between mb-4">
              <Calendar className="w-5 h-5 text-neutral-400" />
              <LuxeBadge variant="success">Active</LuxeBadge>
            </div>
            <div className="text-sm text-neutral-600 mb-1">Current Sprint</div>
            <div className="text-lg font-medium text-neutral-900">{activeSprint.name || `Sprint ${activeSprint.id.slice(0, 8)}`}</div>
            <div className="text-xs text-neutral-500 mt-2">
              {new Date(activeSprint.start_date).toLocaleDateString()} - {new Date(activeSprint.end_date).toLocaleDateString()}
            </div>
          </LuxeCard>
        </motion.div>

        {/* Capacity */}
        <motion.div variants={fadeInUp}>
          <LuxeCard className="p-6">
            <div className="flex items-start justify-between mb-4">
              <Users className="w-5 h-5 text-neutral-400" />
              <LuxeBadge variant={
                capacityStatus === 'healthy' ? 'success' :
                  capacityStatus === 'warning' ? 'warning' : 'error'
              }>
                {capacityPercentage}%
              </LuxeBadge>
            </div>
            <div className="text-sm text-neutral-600 mb-1">Capacity</div>
            <div className="text-lg font-medium text-neutral-900">
              {activeSprint.current_load} / {activeSprint.capacity_budget}
            </div>
            <div className="mt-2 h-2 bg-neutral-200 rounded-full overflow-hidden">
              <div
                className={cn(
                  "h-full transition-all",
                  capacityStatus === 'healthy' ? 'bg-emerald-500' :
                    capacityStatus === 'warning' ? 'bg-amber-500' : 'bg-red-500'
                )}
                style={{ width: `${Math.min(capacityPercentage, 100)}%` }}
              />
            </div>
          </LuxeCard>
        </motion.div>

        {/* Active Moves */}
        <motion.div variants={fadeInUp}>
          <LuxeCard className="p-6">
            <div className="flex items-start justify-between mb-4">
              <Target className="w-5 h-5 text-neutral-400" />
              <TrendingUp className="w-4 h-4 text-neutral-400" />
            </div>
            <div className="text-sm text-neutral-600 mb-1">Active Moves</div>
            <div className="text-lg font-medium text-neutral-900">{sprintMoves.length}</div>
            <div className="text-xs text-neutral-500 mt-2">
              {movesByPhase.complete.length} completed
            </div>
          </LuxeCard>
        </motion.div>

        {/* Anomalies */}
        <motion.div variants={fadeInUp}>
          <LuxeCard className="p-6">
            <div className="flex items-start justify-between mb-4">
              <AlertCircle className="w-5 h-5 text-neutral-400" />
              <LuxeBadge variant="neutral">Sentinel</LuxeBadge>
            </div>
            <div className="text-sm text-neutral-600 mb-1">Active Alerts</div>
            <div className="text-lg font-medium text-neutral-900">{anomalies.length}</div>
            <div className="text-xs text-neutral-500 mt-2">
              No critical issues
            </div>
          </LuxeCard>
        </motion.div>
      </div>

      {/* Sprint Board (OODA Phases) */}
      <motion.div variants={fadeInUp}>
        <LuxeCard className="p-6">
          <h2 className="font-display text-xl font-medium text-neutral-900 mb-6">Sprint Board</h2>

          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {Object.entries(movesByPhase).map(([phase, phaseMoves]) => (
              <div key={phase} className="space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold uppercase tracking-wider text-neutral-700">
                    {phase}
                  </h3>
                  <span className="text-xs font-mono text-neutral-500">
                    {phaseMoves.length}
                  </span>
                </div>

                <div className="space-y-2">
                  {phaseMoves.length === 0 ? (
                    <div className="p-4 border-2 border-dashed border-neutral-200 rounded-xl text-center">
                      <span className="text-xs text-neutral-400">No moves</span>
                    </div>
                  ) : (
                    phaseMoves.map(move => (
                      <Link
                        key={move.id}
                        to={`/moves/${move.id}`}
                        className="block p-4 bg-white border border-neutral-200 rounded-xl hover:shadow-md transition-all group"
                      >
                        <div className="flex items-start justify-between mb-2">
                          <span className="text-sm font-medium text-neutral-900 group-hover:text-neutral-600 transition-colors line-clamp-2">
                            {move.name}
                          </span>
                          <div className={cn("w-2 h-2 rounded-full", getHealthColor(move.health_status))} />
                        </div>

                        <div className="flex items-center justify-between text-xs text-neutral-500">
                          <span>{move.progress_percentage}%</span>
                          {move.end_date && (
                            <span>Due {new Date(move.end_date).toLocaleDateString()}</span>
                          )}
                        </div>

                        {move.progress_percentage > 0 && (
                          <div className="mt-2 h-1 bg-neutral-100 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-neutral-900"
                              style={{ width: `${move.progress_percentage}%` }}
                            />
                          </div>
                        )}
                      </Link>
                    ))
                  )}
                </div>
              </div>
            ))}
          </div>
        </LuxeCard>
      </motion.div>

      {/* Quick Actions */}
      <motion.div variants={fadeInUp} className="flex gap-4">
        <Link to="/moves/library">
          <LuxeButton>Add New Move</LuxeButton>
        </Link>
        <Link to="/moves">
          <LuxeButton variant="outline">View All Moves</LuxeButton>
        </Link>
      </motion.div>

      {/* System Sentinel (Anomalies) */}
      {anomalies.length > 0 && (
        <motion.div variants={fadeInUp}>
          <LuxeCard className="p-6">
            <h2 className="font-display text-xl font-medium text-neutral-900 mb-4 flex items-center gap-2">
              <AlertCircle className="w-5 h-5" />
              System Sentinel
            </h2>
            <div className="space-y-3">
              {anomalies.map((anomaly, i) => (
                <div key={i} className="p-4 bg-red-50 border border-red-200 rounded-xl">
                  <div className="flex items-start justify-between">
                    <div>
                      <span className="text-sm font-bold text-red-900">{anomaly.type}</span>
                      <p className="text-sm text-red-700 mt-1">{anomaly.description}</p>
                    </div>
                    <span className="text-xs text-red-600">Severity {anomaly.severity}/5</span>
                  </div>
                </div>
              ))}
            </div>
          </LuxeCard>
        </motion.div>
      )}
    </motion.div>
  );
}
