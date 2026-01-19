'use client';

import React, { useState, useEffect } from 'react';
import { useCostTracker } from '@/lib/cost-tracker';

export function CostDashboard() {
  const { getMetrics, getDailyUsage, getModelBreakdown, getCostProjection, exportData, resetMetrics } = useCostTracker();
  const [metrics, setMetrics] = useState(getMetrics());
  const [dailyUsage, setDailyUsage] = useState(getDailyUsage(7));
  const [modelBreakdown, setModelBreakdown] = useState(getModelBreakdown());
  const [projections, setProjections] = useState(getCostProjection());

  useEffect(() => {
    const interval = setInterval(() => {
      setMetrics(getMetrics());
      setDailyUsage(getDailyUsage(7));
      setModelBreakdown(getModelBreakdown());
      setProjections(getCostProjection());
    }, 5000); // Update every 5 seconds

    return () => clearInterval(interval);
  }, [getMetrics, getDailyUsage, getModelBreakdown, getCostProjection]);

  const formatCost = (cost: number) => `$${cost.toFixed(4)}`;
  const formatTokens = (tokens: number) => tokens.toLocaleString();

  return (
    <div className="p-6 bg-white rounded-lg shadow-lg">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">AI Cost Monitor</h2>
        <div className="flex gap-2">
          <button
            onClick={() => navigator.clipboard.writeText(exportData())}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Export Data
          </button>
          <button
            onClick={resetMetrics}
            className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
          >
            Reset
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-blue-50 p-4 rounded-lg">
          <div className="text-sm text-gray-600">Total Cost</div>
          <div className="text-2xl font-bold text-blue-600">{formatCost(metrics.totalCost)}</div>
        </div>
        <div className="bg-green-50 p-4 rounded-lg">
          <div className="text-sm text-gray-600">Total Tokens</div>
          <div className="text-2xl font-bold text-green-600">{formatTokens(metrics.totalTokens)}</div>
        </div>
        <div className="bg-purple-50 p-4 rounded-lg">
          <div className="text-sm text-gray-600">Requests</div>
          <div className="text-2xl font-bold text-purple-600">{metrics.requestCount}</div>
        </div>
        <div className="bg-orange-50 p-4 rounded-lg">
          <div className="text-sm text-gray-600">Monthly Projection</div>
          <div className="text-2xl font-bold text-orange-600">{formatCost(projections.monthly)}</div>
        </div>
      </div>

      {/* Daily Usage Chart */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-3">7-Day Usage</h3>
        <div className="bg-gray-50 p-4 rounded-lg">
          {dailyUsage.map((day, index) => (
            <div key={day.date} className="flex justify-between items-center py-2 border-b border-gray-200 last:border-0">
              <span className="text-sm text-gray-600">{day.date}</span>
              <div className="flex gap-4">
                <span className="text-sm">{formatTokens(day.tokens)} tokens</span>
                <span className="text-sm font-semibold">{formatCost(day.cost)}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Model Breakdown */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-3">Model Usage Breakdown</h3>
        <div className="bg-gray-50 p-4 rounded-lg">
          {modelBreakdown.map((model) => (
            <div key={model.model} className="flex justify-between items-center py-2 border-b border-gray-200 last:border-0">
              <span className="text-sm font-medium">{model.model}</span>
              <div className="flex gap-4 text-sm">
                <span>{model.requests} requests</span>
                <span>{formatTokens(model.tokens)} tokens</span>
                <span className="font-semibold">{formatCost(model.cost)}</span>
                <span>{formatCost(model.avgCostPerRequest)}/req</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Projections */}
      <div>
        <h3 className="text-lg font-semibold mb-3">Cost Projections</h3>
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-gray-50 p-3 rounded text-center">
            <div className="text-sm text-gray-600">Daily</div>
            <div className="text-lg font-semibold">{formatCost(projections.daily)}</div>
          </div>
          <div className="bg-gray-50 p-3 rounded text-center">
            <div className="text-sm text-gray-600">Weekly</div>
            <div className="text-lg font-semibold">{formatCost(projections.weekly)}</div>
          </div>
          <div className="bg-gray-50 p-3 rounded text-center">
            <div className="text-sm text-gray-600">Monthly</div>
            <div className="text-lg font-semibold">{formatCost(projections.monthly)}</div>
          </div>
        </div>
      </div>
    </div>
  );
}
