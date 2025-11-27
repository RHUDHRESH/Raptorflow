/**
 * Move Detail - Integrated with Real Supabase Data
 * Complete view of a move with editable OODA configuration
 */

import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Target, ArrowLeft, Edit2, Save, X, Play, Pause, CheckCircle, XCircle, TrendingUp
} from 'lucide-react';
import { moveService } from '../lib/services/move-service';
import { analyticsService } from '../lib/services/analytics-service';

export default function MoveDetailIntegrated() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [move, setMove] = useState(null);
  const [maneuverType, setManeuverType] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editing, setEditing] = useState(false);
  const [metrics, setMetrics] = useState([]);

  // Editable fields
  const [editedName, setEditedName] = useState('');
  const [editedGoal, setEditedGoal] = useState('');
  const [editedOODA, setEditedOODA] = useState({});

  // Mock move data
  const MOCK_MOVE = {
    id: id,
    name: '14-Day Conversion Sprint',
    status: 'Planning',
    goal: 'Drive 500 qualified leads',
    progress_percentage: 48,
    start_date: '2025-01-15',
    end_date: '2025-01-29',
    targetCohorts: ['Enterprise CTOs', 'Startup Founders'],
    channels: ['LinkedIn', 'Email', 'Content'],
    tasksCompleted: 12,
    totalTasks: 25,
    health_status: 'green',
    ooda_config: {
      observe_sources: ['Google Analytics', 'LinkedIn Insights'],
      orient_rules: 'Analyze conversion funnel data',
      decide_logic: 'Optimize top 3 bottlenecks',
      act_tasks: ['A/B test landing page', 'Email campaign', 'LinkedIn ads']
    }
  };

  useEffect(() => {
    // Simulate loading with mock data
    setLoading(true);
    setTimeout(() => {
      setMove(MOCK_MOVE);
      setEditedName(MOCK_MOVE.name);
      setEditedGoal(MOCK_MOVE.goal || '');
      setEditedOODA(MOCK_MOVE.ooda_config || {});
      setLoading(false);
    }, 300);
  }, [id]);

  const handleSave = async () => {
    try {
      const updated = await moveService.updateMove(id, {
        name: editedName,
        goal: editedGoal,
        ooda_config: editedOODA,
      });
      setMove(updated);
      setEditing(false);
    } catch (err) {
      console.error('Error saving move:', err);
      alert('Failed to save changes');
    }
  };

  const handleStatusTransition = async (newStatus) => {
    try {
      const updated = await moveService.updateMove(id, { status: newStatus });
      setMove(updated);
    } catch (err) {
      console.error('Error updating status:', err);
      alert('Failed to update status');
    }
  };

  const handleProgressUpdate = async (newProgress) => {
    try {
      const updated = await moveService.updateMove(id, { progress_percentage: newProgress });
      setMove(updated);
    } catch (err) {
      console.error('Error updating progress:', err);
    }
  };

  const getStatusLabel = (status) => {
    const labels = {
      'Planning': 'Planning',
      'OODA_Observe': 'Observe',
      'OODA_Orient': 'Orient',
      'OODA_Decide': 'Decide',
      'OODA_Act': 'Act',
      'Complete': 'Complete',
      'Killed': 'Killed',
    };
    return labels[status] || status;
  };

  const getNextStatus = (currentStatus) => {
    const flow = {
      'Planning': 'OODA_Observe',
      'OODA_Observe': 'OODA_Orient',
      'OODA_Orient': 'OODA_Decide',
      'OODA_Decide': 'OODA_Act',
      'OODA_Act': 'Complete',
    };
    return flow[currentStatus];
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
          <p className="text-neutral-600">Loading move details...</p>
        </div>
      </div>
    );
  }

  if (error || !move) {
    return (
      <div className="runway-card p-12 text-center">
        <XCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-neutral-900 mb-2">Error</h2>
        <p className="text-neutral-600 mb-6">{error || 'Move not found'}</p>
        <button
          onClick={() => navigate('/moves')}
          className="px-6 py-3 bg-neutral-900 text-white rounded-lg hover:bg-neutral-800"
        >
          Back to Moves
        </button>
      </div>
    );
  }

  const nextStatus = getNextStatus(move.status);

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Back Navigation */}
      <Link
        to="/moves"
        className="inline-flex items-center gap-2 text-neutral-600 hover:text-neutral-900"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to Moves
      </Link>

      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="runway-card p-10"
      >
        <div className="flex items-start justify-between mb-6">
          <div className="flex-1">
            {editing ? (
              <input
                type="text"
                value={editedName}
                onChange={(e) => setEditedName(e.target.value)}
                className="text-3xl font-bold text-neutral-900 border-b-2 border-neutral-300 focus:outline-none focus:border-neutral-900 w-full mb-4"
              />
            ) : (
              <h1 className="text-3xl font-bold text-neutral-900 mb-4">{move.name}</h1>
            )}

            <div className="flex flex-wrap gap-3">
              <span className="px-3 py-1 text-sm font-medium bg-neutral-100 text-neutral-900 border border-neutral-200 rounded">
                {getStatusLabel(move.status)}
              </span>
              {maneuverType && (
                <span className="px-3 py-1 text-sm font-medium bg-blue-100 text-blue-900 border border-blue-200 rounded">
                  {maneuverType.category} - {maneuverType.name}
                </span>
              )}
              <div className="flex items-center gap-2">
                <div className={`w-3 h-3 rounded-full ${getHealthColor(move.health_status)}`} />
                <span className="text-sm text-neutral-600">Health: {move.health_status}</span>
              </div>
            </div>
          </div>

          <div className="flex gap-2">
            {editing ? (
              <>
                <button
                  onClick={handleSave}
                  className="p-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                >
                  <Save className="w-5 h-5" />
                </button>
                <button
                  onClick={() => setEditing(false)}
                  className="p-2 bg-neutral-200 text-neutral-900 rounded-lg hover:bg-neutral-300"
                >
                  <X className="w-5 h-5" />
                </button>
              </>
            ) : (
              <button
                onClick={() => setEditing(true)}
                className="p-2 bg-neutral-100 text-neutral-900 rounded-lg hover:bg-neutral-200"
              >
                <Edit2 className="w-5 h-5" />
              </button>
            )}
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mb-6">
          <div className="flex justify-between text-sm text-neutral-600 mb-2">
            <span>Progress</span>
            <span>{move.progress_percentage}%</span>
          </div>
          <div className="h-3 bg-neutral-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-neutral-900 transition-all duration-300"
              style={{ width: `${move.progress_percentage}%` }}
            />
          </div>
        </div>

        {/* Quick Actions */}
        <div className="flex gap-3">
          {nextStatus && move.status !== 'Complete' && (
            <button
              onClick={() => handleStatusTransition(nextStatus)}
              className="px-6 py-2 bg-neutral-900 text-white rounded-lg hover:bg-neutral-800 flex items-center gap-2"
            >
              <Play className="w-4 h-4" />
              Move to {getStatusLabel(nextStatus)}
            </button>
          )}
          {move.status !== 'Complete' && move.status !== 'Killed' && (
            <button
              onClick={() => handleStatusTransition('Complete')}
              className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2"
            >
              <CheckCircle className="w-4 h-4" />
              Mark Complete
            </button>
          )}
          <button
            onClick={() => handleStatusTransition('Killed')}
            className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 flex items-center gap-2"
          >
            <XCircle className="w-4 h-4" />
            Kill Move
          </button>
        </div>
      </motion.div>

      {/* Details Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Timeline */}
        <div className="runway-card p-6">
          <h2 className="text-lg font-bold text-neutral-900 mb-4">Timeline</h2>
          <div className="space-y-4">
            <div>
              <p className="text-sm text-neutral-600">Start Date</p>
              <p className="text-neutral-900">
                {move.start_date ? new Date(move.start_date).toLocaleDateString() : 'Not set'}
              </p>
            </div>
            <div>
              <p className="text-sm text-neutral-600">End Date</p>
              <p className="text-neutral-900">
                {move.end_date ? new Date(move.end_date).toLocaleDateString() : 'Not set'}
              </p>
            </div>
            {maneuverType && (
              <div>
                <p className="text-sm text-neutral-600">Duration</p>
                <p className="text-neutral-900">{maneuverType.base_duration_days} days</p>
              </div>
            )}
          </div>
        </div>

        {/* Metadata */}
        <div className="runway-card p-6">
          <h2 className="text-lg font-bold text-neutral-900 mb-4">Metadata</h2>
          <div className="space-y-4">
            <div>
              <p className="text-sm text-neutral-600">ICP</p>
              <p className="text-neutral-900">{move.primary_icp_id?.slice(0, 8) || 'None'}</p>
            </div>
            <div>
              <p className="text-sm text-neutral-600">Sprint</p>
              <p className="text-neutral-900">{move.sprint_id ? move.sprint_id.slice(0, 8) : 'Unassigned'}</p>
            </div>
            <div>
              <p className="text-sm text-neutral-600">Line of Operation</p>
              <p className="text-neutral-900">{move.line_of_operation_id ? move.line_of_operation_id.slice(0, 8) : 'None'}</p>
            </div>
          </div>
        </div>

        {/* Channels */}
        <div className="runway-card p-6">
          <h2 className="text-lg font-bold text-neutral-900 mb-4">Channels</h2>
          <div className="flex flex-wrap gap-2">
            {move.channels && move.channels.length > 0 ? (
              move.channels.map((channel, i) => (
                <span
                  key={i}
                  className="px-3 py-1 text-sm bg-neutral-100 text-neutral-900 border border-neutral-200 rounded"
                >
                  {channel}
                </span>
              ))
            ) : (
              <p className="text-neutral-600 text-sm">No channels specified</p>
            )}
          </div>
        </div>
      </div>

      {/* Goal */}
      <div className="runway-card p-6">
        <h2 className="text-lg font-bold text-neutral-900 mb-4">Goal</h2>
        {editing ? (
          <textarea
            value={editedGoal}
            onChange={(e) => setEditedGoal(e.target.value)}
            className="w-full p-4 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-neutral-900 min-h-[100px]"
            placeholder="Describe the goal of this move..."
          />
        ) : (
          <p className="text-neutral-700">{move.goal || 'No goal specified'}</p>
        )}
      </div>

      {/* OODA Configuration */}
      <div className="runway-card p-6">
        <h2 className="text-lg font-bold text-neutral-900 mb-6">OODA Loop Configuration</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="text-sm font-bold text-neutral-700 mb-2">Observe</h3>
            <p className="text-sm text-neutral-600">Data sources and monitoring</p>
            <div className="mt-3 text-neutral-700">
              {JSON.stringify(editedOODA.observe_sources || [], null, 2)}
            </div>
          </div>
          <div>
            <h3 className="text-sm font-bold text-neutral-700 mb-2">Orient</h3>
            <p className="text-sm text-neutral-600">Context and interpretation rules</p>
            <div className="mt-3 text-neutral-700">
              {editedOODA.orient_rules || 'Not configured'}
            </div>
          </div>
          <div>
            <h3 className="text-sm font-bold text-neutral-700 mb-2">Decide</h3>
            <p className="text-sm text-neutral-600">Decision logic and thresholds</p>
            <div className="mt-3 text-neutral-700">
              {editedOODA.decide_logic || 'Not configured'}
            </div>
          </div>
          <div>
            <h3 className="text-sm font-bold text-neutral-700 mb-2">Act</h3>
            <p className="text-sm text-neutral-600">Action tasks and execution</p>
            <div className="mt-3 text-neutral-700">
              {JSON.stringify(editedOODA.act_tasks || [], null, 2)}
            </div>
          </div>
        </div>
      </div>

      {/* Metrics */}
      {metrics.length > 0 && (
        <div className="runway-card p-6">
          <h2 className="text-lg font-bold text-neutral-900 mb-4 flex items-center gap-2">
            <TrendingUp className="w-5 h-5" />
            Performance Metrics
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-neutral-200">
                  <th className="text-left p-2 text-sm text-neutral-600">Date</th>
                  <th className="text-right p-2 text-sm text-neutral-600">Actions</th>
                  <th className="text-right p-2 text-sm text-neutral-600">Notes</th>
                </tr>
              </thead>
              <tbody>
                {metrics.map((metric, i) => (
                  <tr key={i} className="border-b border-neutral-100">
                    <td className="p-2 text-sm">{metric.date}</td>
                    <td className="p-2 text-sm text-right">{metric.actions_completed || 0}</td>
                    <td className="p-2 text-sm text-right">{metric.notes || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}


