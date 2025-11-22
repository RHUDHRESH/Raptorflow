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

export default function WarRoomIntegrated() {
  const { activeSprint, sprints, loading: sprintsLoading } = useSprints();
  const { moves, loading: movesLoading } = useMoves();
  const { icps } = useICPs();
  const [linesOfOperation, setLinesOfOperation] = useState([]);
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

  const getPhaseColor = (phase) => {
    const colors = {
      planning: 'bg-neutral-100 text-neutral-900',
      observe: 'bg-blue-100 text-blue-900',
      orient: 'bg-purple-100 text-purple-900',
      decide: 'bg-amber-100 text-amber-900',
      act: 'bg-green-100 text-green-900',
      complete: 'bg-neutral-200 text-neutral-600',
    };
    return colors[phase] || colors.planning;
  };

  const getHealthColor = (health) => {
    const colors = {
      green: 'bg-green-500',
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
      <div className="space-y-8">
        <div className="runway-card p-12 text-center">
          <Target className="w-16 h-16 text-neutral-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-neutral-900 mb-2">No Active Sprint</h2>
          <p className="text-neutral-600 mb-6">
            Create a sprint to start planning your moves
          </p>
          <Link
            to="/sprints/new"
            className="inline-block px-6 py-3 bg-neutral-900 text-white rounded-lg hover:bg-neutral-800"
          >
            Create Sprint
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="runway-card relative overflow-hidden p-10"
      >
        <div className="absolute inset-0 bg-gradient-to-br from-white via-neutral-50 to-white" />
        <div className="relative z-10">
          <p className="micro-label mb-2">War Room</p>
          <h1 className="font-serif text-4xl md:text-6xl text-black leading-tight mb-3">
            Command Center
          </h1>
          <p className="text-base text-neutral-600 max-w-2xl">
            Kinetic operations dashboard. Deploy moves, monitor capacity, and coordinate execution.
          </p>
        </div>
      </motion.div>

      {/* Operational Context */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {/* Active Sprint */}
        <div className="runway-card p-6">
          <div className="flex items-start justify-between mb-4">
            <Calendar className="w-5 h-5 text-neutral-400" />
            <span className="px-2 py-1 text-[10px] font-mono uppercase tracking-wider bg-green-100 text-green-900 border border-green-200 rounded">
              Active
            </span>
          </div>
          <div className="text-sm text-neutral-600 mb-1">Current Sprint</div>
          <div className="text-lg font-bold text-neutral-900">{activeSprint.name || `Sprint ${activeSprint.id.slice(0, 8)}`}</div>
          <div className="text-xs text-neutral-500 mt-2">
            {new Date(activeSprint.start_date).toLocaleDateString()} - {new Date(activeSprint.end_date).toLocaleDateString()}
          </div>
        </div>

        {/* Capacity */}
        <div className="runway-card p-6">
          <div className="flex items-start justify-between mb-4">
            <Users className="w-5 h-5 text-neutral-400" />
            <span className={`px-2 py-1 text-[10px] font-mono uppercase tracking-wider border rounded ${
              capacityStatus === 'healthy' ? 'bg-green-100 text-green-900 border-green-200' :
              capacityStatus === 'warning' ? 'bg-amber-100 text-amber-900 border-amber-200' :
              'bg-red-100 text-red-900 border-red-200'
            }`}>
              {capacityPercentage}%
            </span>
          </div>
          <div className="text-sm text-neutral-600 mb-1">Capacity</div>
          <div className="text-lg font-bold text-neutral-900">
            {activeSprint.current_load} / {activeSprint.capacity_budget}
          </div>
          <div className="mt-2 h-2 bg-neutral-200 rounded-full overflow-hidden">
            <div 
              className={`h-full ${
                capacityStatus === 'healthy' ? 'bg-green-500' :
                capacityStatus === 'warning' ? 'bg-amber-500' :
                'bg-red-500'
              }`}
              style={{ width: `${Math.min(capacityPercentage, 100)}%` }}
            />
          </div>
        </div>

        {/* Active Moves */}
        <div className="runway-card p-6">
          <div className="flex items-start justify-between mb-4">
            <Target className="w-5 h-5 text-neutral-400" />
            <TrendingUp className="w-4 h-4 text-neutral-400" />
          </div>
          <div className="text-sm text-neutral-600 mb-1">Active Moves</div>
          <div className="text-lg font-bold text-neutral-900">{sprintMoves.length}</div>
          <div className="text-xs text-neutral-500 mt-2">
            {movesByPhase.complete.length} completed
          </div>
        </div>

        {/* Anomalies */}
        <div className="runway-card p-6">
          <div className="flex items-start justify-between mb-4">
            <AlertCircle className="w-5 h-5 text-neutral-400" />
            <span className="px-2 py-1 text-[10px] font-mono uppercase tracking-wider bg-neutral-100 text-neutral-600 border border-neutral-200 rounded">
              Sentinel
            </span>
          </div>
          <div className="text-sm text-neutral-600 mb-1">Active Alerts</div>
          <div className="text-lg font-bold text-neutral-900">{anomalies.length}</div>
          <div className="text-xs text-neutral-500 mt-2">
            No critical issues
          </div>
        </div>
      </div>

      {/* Sprint Lanes (OODA Phases) */}
      <div className="runway-card p-6">
        <h2 className="text-xl font-bold text-neutral-900 mb-6">Sprint Board</h2>
        
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
                  <div className="p-4 border-2 border-dashed border-neutral-200 rounded-lg text-center">
                    <span className="text-xs text-neutral-400">No moves</span>
                  </div>
                ) : (
                  phaseMoves.map(move => (
                    <Link
                      key={move.id}
                      to={`/moves/${move.id}`}
                      className="block p-4 bg-white border border-neutral-200 rounded-lg hover:shadow-md transition-all group"
                    >
                      <div className="flex items-start justify-between mb-2">
                        <span className="text-sm font-medium text-neutral-900 group-hover:text-neutral-600 transition-colors line-clamp-2">
                          {move.name}
                        </span>
                        <div className={`w-2 h-2 rounded-full ${getHealthColor(move.health_status)}`} />
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
      </div>

      {/* Quick Actions */}
      <div className="flex gap-4">
        <Link
          to="/moves/library"
          className="px-6 py-3 bg-neutral-900 text-white rounded-lg hover:bg-neutral-800 transition-colors"
        >
          Add New Move
        </Link>
        <Link
          to="/moves"
          className="px-6 py-3 border border-neutral-200 text-neutral-900 rounded-lg hover:bg-neutral-50 transition-colors"
        >
          View All Moves
        </Link>
      </div>

      {/* System Sentinel (Anomalies) */}
      {anomalies.length > 0 && (
        <div className="runway-card p-6">
          <h2 className="text-xl font-bold text-neutral-900 mb-4 flex items-center gap-2">
            <AlertCircle className="w-5 h-5" />
            System Sentinel
          </h2>
          <div className="space-y-3">
            {anomalies.map((anomaly, i) => (
              <div key={i} className="p-4 bg-red-50 border border-red-200 rounded-lg">
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
        </div>
      )}
    </div>
  );
}



