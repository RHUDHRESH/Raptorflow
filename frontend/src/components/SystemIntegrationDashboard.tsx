'use client';

import React, { useEffect, useState } from 'react';
import { useMovesStore } from '../stores/movesStore';
import { useEnhancedCampaignStore } from '../stores/enhancedCampaignStore';
import { useDailyWinsStore } from '../stores/dailyWinsStore';
import { useBlackboxStore } from '../stores/blackboxStore';
import { useMuseStore } from '../stores/museStore';
import { useBCMStore } from '../stores/bcmStore';
import { useToolsStore } from '../stores/toolsStore';
import { useAgentsStore } from '../stores/agentsStore';
import { useAnalyticsStore } from '../stores/analyticsStore';
import { getCurrentWorkspaceId, getCurrentUserId } from '../lib/auth-helpers';
import BusinessContextForm from './BusinessContextForm';

interface SystemStatus {
  name: string;
  status: 'loading' | 'connected' | 'error';
  lastCheck: string;
  data?: any;
}

export default function SystemIntegrationDashboard() {
  const [systemStatuses, setSystemStatuses] = useState<Record<string, SystemStatus>>({});
  const [isInitializing, setIsInitializing] = useState(true);

  // Store hooks
  const movesStore = useMovesStore();
  const campaignsStore = useEnhancedCampaignStore();
  const dailyWinsStore = useDailyWinsStore();
  const blackboxStore = useBlackboxStore();
  const museStore = useMuseStore();
  const bcmStore = useBCMStore();
  const toolsStore = useToolsStore();
  const agentsStore = useAgentsStore();
  const analyticsStore = useAnalyticsStore();

  // Initialize all systems
  useEffect(() => {
    const initializeSystems = async () => {
      const workspaceId = getCurrentWorkspaceId();
      const userId = getCurrentUserId();

      if (!workspaceId || !userId) {
        console.error('Authentication required for system initialization');
        setIsInitializing(false);
        return;
      }

      const systems: Record<string, SystemStatus> = {};

      // Initialize each system
      try {
        // Moves System
        setSystemStatuses(prev => ({ ...prev, moves: { name: 'Moves', status: 'loading', lastCheck: new Date().toISOString() } }));
        await movesStore.fetchMoves();
        systems.moves = { name: 'Moves', status: 'connected', lastCheck: new Date().toISOString(), data: movesStore.moves };

        // Campaigns System
        setSystemStatuses(prev => ({ ...prev, campaigns: { name: 'Campaigns', status: 'loading', lastCheck: new Date().toISOString() } }));
        await campaignsStore.fetchCampaigns();
        systems.campaigns = { name: 'Campaigns', status: 'connected', lastCheck: new Date().toISOString(), data: campaignsStore.campaigns };

        // Daily Wins System
        setSystemStatuses(prev => ({ ...prev, dailyWins: { name: 'Daily Wins', status: 'loading', lastCheck: new Date().toISOString() } }));
        await dailyWinsStore.fetchWins(workspaceId, userId);
        systems.dailyWins = { name: 'Daily Wins', status: 'connected', lastCheck: new Date().toISOString(), data: dailyWinsStore.wins };

        // Blackbox System
        setSystemStatuses(prev => ({ ...prev, blackbox: { name: 'Blackbox', status: 'loading', lastCheck: new Date().toISOString() } }));
        await blackboxStore.fetchStrategies(workspaceId, userId);
        systems.blackbox = { name: 'Blackbox', status: 'connected', lastCheck: new Date().toISOString(), data: blackboxStore.strategies };

        // Muse System
        setSystemStatuses(prev => ({ ...prev, muse: { name: 'Muse', status: 'loading', lastCheck: new Date().toISOString() } }));
        await museStore.fetchAssets(workspaceId, userId);
        systems.muse = { name: 'Muse', status: 'connected', lastCheck: new Date().toISOString(), data: museStore.assets };

        // BCM System
        setSystemStatuses(prev => ({ ...prev, bcm: { name: 'BCM', status: 'loading', lastCheck: new Date().toISOString() } }));
        await bcmStore.fetchContext(workspaceId);
        await bcmStore.fetchEvolution(workspaceId);
        systems.bcm = { name: 'BCM', status: 'connected', lastCheck: new Date().toISOString(), data: bcmStore.context };

        // Tools System
        setSystemStatuses(prev => ({ ...prev, tools: { name: 'Tools', status: 'loading', lastCheck: new Date().toISOString() } }));
        await toolsStore.fetchAvailableTools();
        await toolsStore.fetchServicesStatus();
        systems.tools = { name: 'Tools', status: 'connected', lastCheck: new Date().toISOString(), data: toolsStore.tools };

        // Agents System
        setSystemStatuses(prev => ({ ...prev, agents: { name: 'Agents', status: 'loading', lastCheck: new Date().toISOString() } }));
        await agentsStore.fetchAvailableAgents();
        systems.agents = { name: 'Agents', status: 'connected', lastCheck: new Date().toISOString(), data: agentsStore.agents };

        // Analytics System
        setSystemStatuses(prev => ({ ...prev, analytics: { name: 'Analytics', status: 'loading', lastCheck: new Date().toISOString() } }));
        await analyticsStore.fetchDashboard();
        systems.analytics = { name: 'Analytics', status: 'connected', lastCheck: new Date().toISOString(), data: analyticsStore.dashboard };

      } catch (error) {
        console.error('System initialization error:', error);
        // Mark failed systems as error
        Object.keys(systems).forEach(key => {
          if (!systems[key].data) {
            systems[key] = { ...systems[key], status: 'error' as const };
          }
        });
      }

      setSystemStatuses(systems);
      setIsInitializing(false);
    };

    initializeSystems();
  }, []);

  // Test system integration
  const testIntegration = async () => {
    const workspaceId = getCurrentWorkspaceId();
    const userId = getCurrentUserId();

    if (!workspaceId || !userId) {
      alert('Please authenticate first');
      return;
    }

    try {
      // Test 1: Create a Move
      const moveId = await movesStore.addMove({
        name: 'Integration Test Move',
        focusArea: 'Testing',
        desiredOutcome: 'Verify full system integration',
        volatilityLevel: 3,
        steps: ['Initialize', 'Test', 'Verify', 'Complete']
      });

      // Test 2: Generate a Daily Win
      const dailyWin = await dailyWinsStore.generateWin({
        workspace_id: workspaceId,
        user_id: userId,
        platform: 'LinkedIn'
      });

      // Test 3: Generate Strategy with Blackbox
      const strategy = await blackboxStore.generateStrategy({
        focus_area: 'integration_testing',
        business_context: 'Testing full system integration with BCM',
        workspace_id: workspaceId,
        user_id: userId
      });

      // Test 4: Generate Content with Muse
      const content = await museStore.generateContent({
        prompt: 'Create content about successful system integration',
        platform: 'blog',
        workspace_id: workspaceId,
        user_id: userId
      });

      // Test 5: Execute Agent with BCM Context
      const agentExecution = await agentsStore.executeAgent('muse', 'Generate integration summary', {
        bcm_context: bcmStore.context,
        recent_activities: {
          moves_created: 1,
          strategies_generated: 1,
          content_created: 1
        }
      });

      // Test 6: Record BCM Interaction
      await bcmStore.recordInteraction({
        agent: 'integration_test',
        action: 'full_system_test',
        context: {
          move_id: moveId,
          strategy_id: strategy.id,
          content_id: content.id,
          agent_execution: agentExecution
        }
      });

      alert('✅ Integration test completed successfully! All systems are working together.');

    } catch (error) {
      console.error('Integration test failed:', error);
      alert('❌ Integration test failed. Check console for details.');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'connected': return 'text-green-600';
      case 'loading': return 'text-yellow-600';
      case 'error': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'connected': return '✅';
      case 'loading': return '⏳';
      case 'error': return '❌';
      default: return '❓';
    }
  };

  if (isInitializing) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-800">Initializing Raptorflow Systems...</h2>
          <p className="text-gray-600 mt-2">Connecting all components with BCM integration</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">🚀 Raptorflow System Integration</h1>
          <p className="text-gray-600">Complete integration of all systems with BCM, tools, and agents</p>
        </div>

        {/* System Status Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {Object.entries(systemStatuses).map(([key, system]) => (
            <div key={key} className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">{system.name}</h3>
                <span className={`text-2xl ${getStatusColor(system.status)}`}>
                  {getStatusIcon(system.status)}
                </span>
              </div>
              <div className="text-sm text-gray-600">
                <p>Status: <span className={`font-medium ${getStatusColor(system.status)}`}>{system.status}</span></p>
                <p>Last Check: {new Date(system.lastCheck).toLocaleTimeString()}</p>
                {system.data && (
                  <p>Data Points: {Object.keys(system.data).length} items</p>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* BCM Context Display */}
        {bcmStore.context && (
          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">🧠 Business Context Management</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div>
                <h4 className="font-medium text-gray-700 mb-2">Business Stage</h4>
                <p className="text-sm text-gray-600">{bcmStore.context.business_stage}</p>
              </div>
              <div>
                <h4 className="font-medium text-gray-700 mb-2">Industry</h4>
                <p className="text-sm text-gray-600">{bcmStore.context.industry}</p>
              </div>
              <div>
                <h4 className="font-medium text-gray-700 mb-2">Team Size</h4>
                <p className="text-sm text-gray-600">{bcmStore.context.team_size} people</p>
              </div>
              <div>
                <h4 className="font-medium text-gray-700 mb-2">Revenue Range</h4>
                <p className="text-sm text-gray-600">{bcmStore.context.revenue_range}</p>
              </div>
              <div>
                <h4 className="font-medium text-gray-700 mb-2">Strategic Priorities</h4>
                <ul className="text-sm text-gray-600">
                  {bcmStore.context.strategic_priorities.slice(0, 3).map((priority, i) => (
                    <li key={i}>• {priority}</li>
                  ))}
                </ul>
              </div>
              <div>
                <h4 className="font-medium text-gray-700 mb-2">Current Challenges</h4>
                <ul className="text-sm text-gray-600">
                  {bcmStore.context.current_challenges.map((challenge, i) => (
                    <li key={i}>• {challenge}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}

        <BusinessContextForm />

        {/* Tools and Services Status */}
        {toolsStore.servicesStatus && (
          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">🔧 Tools & Services Status</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium text-gray-700 mb-3">AI Services</h4>
                <div className="space-y-2">
                  {Object.entries(toolsStore.servicesStatus.ai_services).map(([service, status]) => (
                    <div key={service} className="flex justify-between text-sm">
                      <span className="text-gray-600">{service}</span>
                      <span className={`font-medium ${status.status === 'healthy' ? 'text-green-600' : 'text-red-600'}`}>
                        {status.status}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
              <div>
                <h4 className="font-medium text-gray-700 mb-3">Data Services</h4>
                <div className="space-y-2">
                  {Object.entries(toolsStore.servicesStatus.data_services).map(([service, status]) => (
                    <div key={service} className="flex justify-between text-sm">
                      <span className="text-gray-600">{service}</span>
                      <span className={`font-medium ${status.status === 'healthy' ? 'text-green-600' : 'text-red-600'}`}>
                        {status.status}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
            <div className="mt-4 text-center">
              <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${
                toolsStore.overallHealth === 'healthy' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
              }`}>
                Overall Health: {toolsStore.overallHealth}
              </span>
            </div>
          </div>
        )}

        {/* Available Agents */}
        {agentsStore.agents && Object.keys(agentsStore.agents).length > 0 && (
          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">🤖 Available Agents</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {Object.values(agentsStore.agents).map((agent) => (
                <div key={agent.id} className="border rounded-lg p-4">
                  <h4 className="font-medium text-gray-900">{agent.name}</h4>
                  <p className="text-sm text-gray-600 mb-2">{agent.type}</p>
                  <div className="flex flex-wrap gap-1">
                    {agent.specializations.slice(0, 2).map((spec, i) => (
                      <span key={i} className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                        {spec}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Analytics Overview */}
        {analyticsStore.dashboard && (
          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">📊 Analytics Overview</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{analyticsStore.dashboard.overview.total_users}</div>
                <div className="text-sm text-gray-600">Total Users</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{analyticsStore.dashboard.overview.active_campaigns}</div>
                <div className="text-sm text-gray-600">Active Campaigns</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">{(analyticsStore.dashboard.overview.engagement_rate * 100).toFixed(1)}%</div>
                <div className="text-sm text-gray-600">Engagement Rate</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">{(analyticsStore.dashboard.overview.conversion_rate * 100).toFixed(1)}%</div>
                <div className="text-sm text-gray-600">Conversion Rate</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-600">${analyticsStore.dashboard.overview.revenue_this_month.toLocaleString()}</div>
                <div className="text-sm text-gray-600">Monthly Revenue</div>
              </div>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex flex-wrap gap-4 justify-center">
          <button
            onClick={testIntegration}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors"
          >
            🧪 Run Integration Test
          </button>
          <button
            onClick={() => window.location.reload()}
            className="bg-gray-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-gray-700 transition-colors"
          >
            🔄 Refresh Systems
          </button>
        </div>

        {/* System Health Summary */}
        <div className="mt-8 text-center">
          <div className="inline-block bg-white rounded-lg shadow px-6 py-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">System Health Summary</h3>
            <div className="flex items-center justify-center space-x-8">
              <div>
                <span className="text-2xl font-bold text-green-600">
                  {Object.values(systemStatuses).filter(s => s.status === 'connected').length}
                </span>
                <span className="text-sm text-gray-600 ml-1">Connected</span>
              </div>
              <div>
                <span className="text-2xl font-bold text-yellow-600">
                  {Object.values(systemStatuses).filter(s => s.status === 'loading').length}
                </span>
                <span className="text-sm text-gray-600 ml-1">Loading</span>
              </div>
              <div>
                <span className="text-2xl font-bold text-red-600">
                  {Object.values(systemStatuses).filter(s => s.status === 'error').length}
                </span>
                <span className="text-sm text-gray-600 ml-1">Errors</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
