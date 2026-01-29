"use client";

import React, { useEffect, useMemo, useState } from "react";
import {
  Target,
  TrendingUp,
  Clock,
  CheckCircle2,
  AlertCircle,
  Zap,
  BarChart3,
  Calendar,
  Users,
  FileText,
  Database,
  Activity
} from "lucide-react";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintButton } from "@/components/ui/BlueprintButton";
import { OnboardingProgressEnhanced } from "./OnboardingProgressEnhanced";
import { useBcmSync } from "@/hooks/useBcmSync";

interface DashboardMetrics {
  totalSessions: number;
  activeSessions: number;
  completedSessions: number;
  averageCompletionTime: number;
  averageCompletionPercentage: number;
  sessionsThisWeek: number;
  completionRate: number;
}

interface SessionSummary {
  sessionId: string;
  workspaceId: string;
  clientName: string;
  completionPercentage: number;
  currentPhase: number;
  lastActivity: string;
  status: 'active' | 'completed' | 'abandoned';
  startedAt: string;
  estimatedCompletion?: string;
}

interface BCMStatus {
  generated: boolean;
  version: string;
  checksum: string;
  generatedAt: string;
  size: number;
  tokenCount: number;
}

export function OnboardingDashboard() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedSession, setSelectedSession] = useState<string | null>(null);
  const latestWorkspaceId = useMemo(
    () => sessions[0]?.workspaceId ?? null,
    [sessions]
  );
  const { manifest, status: bcmStatus, error: bcmError, rebuild } = useBcmSync(
    latestWorkspaceId ?? undefined
  );
  const bcmStatusSummary: BCMStatus | null = useMemo(() => {
    if (!manifest) return null;
    const payload = JSON.stringify(manifest || {});
    return {
      generated: true,
      version: manifest.version ?? "1.0.0",
      checksum: manifest.checksum ?? "",
      generatedAt: manifest.generatedAt ?? new Date().toISOString(),
      size: payload.length,
      tokenCount: Math.round(payload.length / 4),
    };
  }, [manifest]);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

        // Fetch metrics
        const metricsResponse = await fetch(`${apiUrl}/api/v1/onboarding/dashboard/metrics`);
        if (metricsResponse.ok) {
          const metricsData = await metricsResponse.json();
          setMetrics(metricsData);
        }

        // Fetch sessions
        const sessionsResponse = await fetch(`${apiUrl}/api/v1/onboarding/dashboard/sessions`);
        if (sessionsResponse.ok) {
          const sessionsData = await sessionsResponse.json();
          setSessions(sessionsData.sessions || []);
        }

      } catch (error) {
        console.error("Failed to fetch dashboard data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 size={16} className="text-[var(--success)]" />;
      case 'active':
        return <Activity size={16} className="text-[var(--accent)]" />;
      case 'abandoned':
        return <AlertCircle size={16} className="text-[var(--error)]" />;
      default:
        return <Clock size={16} className="text-[var(--muted)]" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-[var(--success)]';
      case 'active':
        return 'text-[var(--accent)]';
      case 'abandoned':
        return 'text-[var(--error)]';
      default:
        return 'text-[var(--muted)]';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="w-16 h-16 bg-[var(--blueprint)] rounded-[var(--radius-lg)] flex items-center justify-center mx-auto mb-4">
            <BarChart3 size={32} className="text-[var(--paper)] animate-pulse" />
          </div>
          <p className="text-[var(--muted)]">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[var(--canvas)] p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-[var(--ink)]">Onboarding Dashboard</h1>
            <p className="text-[var(--muted)] mt-1">
              Monitor progress and performance across all onboarding sessions
            </p>
          </div>

          <div className="flex gap-3">
            <BlueprintButton variant="outline" size="sm">
              <Calendar size={16} className="mr-2" />
              Export Report
            </BlueprintButton>
            <BlueprintButton variant="blueprint" size="sm">
              <Users size={16} className="mr-2" />
              New Session
            </BlueprintButton>
          </div>
        </div>

        {/* Metrics Cards */}
        {metrics && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <BlueprintCard className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-[var(--muted)]">Total Sessions</p>
                  <p className="text-2xl font-bold text-[var(--ink)]">{metrics.totalSessions}</p>
                </div>
                <div className="w-12 h-12 bg-[var(--accent-light)] rounded-[var(--radius-md)] flex items-center justify-center">
                  <Users size={24} className="text-[var(--accent)]" />
                </div>
              </div>
              <div className="mt-4 text-sm text-[var(--muted)]">
                {metrics.sessionsThisWeek} this week
              </div>
            </BlueprintCard>

            <BlueprintCard className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-[var(--muted)]">Active Sessions</p>
                  <p className="text-2xl font-bold text-[var(--accent)]">{metrics.activeSessions}</p>
                </div>
                <div className="w-12 h-12 bg-[var(--accent-light)] rounded-[var(--radius-md)] flex items-center justify-center">
                  <Activity size={24} className="text-[var(--accent)]" />
                </div>
              </div>
              <div className="mt-4 text-sm text-[var(--muted)]">
                Currently in progress
              </div>
            </BlueprintCard>

            <BlueprintCard className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-[var(--muted)]">Completion Rate</p>
                  <p className="text-2xl font-bold text-[var(--success)]">{metrics.completionRate}%</p>
                </div>
                <div className="w-12 h-12 bg-[var(--success-light)] rounded-[var(--radius-md)] flex items-center justify-center">
                  <Target size={24} className="text-[var(--success)]" />
                </div>
              </div>
              <div className="mt-4 text-sm text-[var(--muted)]">
                {metrics.completedSessions} completed
              </div>
            </BlueprintCard>

            <BlueprintCard className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-[var(--muted)]">Avg. Completion</p>
                  <p className="text-2xl font-bold text-[var(--ink)]">{metrics.averageCompletionPercentage}%</p>
                </div>
                <div className="w-12 h-12 bg-[var(--surface-elevated)] rounded-[var(--radius-md)] flex items-center justify-center">
                  <TrendingUp size={24} className="text-[var(--ink)]" />
                </div>
              </div>
              <div className="mt-4 text-sm text-[var(--muted)]">
                {metrics.averageCompletionTime}h average
              </div>
            </BlueprintCard>
          </div>
        )}

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Sessions List */}
          <div className="lg:col-span-2">
            <BlueprintCard className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-[var(--ink)]">Recent Sessions</h2>
                <BlueprintButton variant="outline" size="sm">
                  <FileText size={16} className="mr-2" />
                  View All
                </BlueprintButton>
              </div>

              <div className="space-y-4">
                {sessions.map((session) => (
                  <div
                    key={session.sessionId}
                    className={`p-4 border border-[var(--border-subtle)] rounded-[var(--radius-lg)] cursor-pointer transition-colors hover:bg-[var(--canvas-elevated)] ${
                      selectedSession === session.sessionId ? 'bg-[var(--accent-light)] border-[var(--accent)]' : ''
                    }`}
                    onClick={() => setSelectedSession(session.sessionId)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        {getStatusIcon(session.status)}
                        <div>
                          <h3 className="font-medium text-[var(--ink)]">{session.clientName}</h3>
                          <p className="text-sm text-[var(--muted)]">
                            Phase {session.currentPhase} • {session.completionPercentage}% complete
                          </p>
                        </div>
                      </div>

                      <div className="text-right">
                        <div className={`text-sm font-medium ${getStatusColor(session.status)}`}>
                          {session.status.charAt(0).toUpperCase() + session.status.slice(1)}
                        </div>
                        <div className="text-xs text-[var(--muted)]">
                          {new Date(session.lastActivity).toLocaleDateString()}
                        </div>
                      </div>
                    </div>

                    {/* Progress Bar */}
                    <div className="mt-3">
                      <div className="bg-[var(--border-subtle)] rounded-full h-2">
                        <div
                          className="bg-[var(--accent)] h-2 rounded-full transition-all duration-300"
                          style={{ width: `${session.completionPercentage}%` }}
                        />
                      </div>
                    </div>

                    {/* Session Details */}
                    <div className="mt-3 flex items-center justify-between text-xs text-[var(--muted)]">
                      <span>Started {new Date(session.startedAt).toLocaleDateString()}</span>
                      {session.estimatedCompletion && (
                        <span>Est. completion: {session.estimatedCompletion}</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </BlueprintCard>
          </div>

          {/* Side Panel */}
          <div className="space-y-6">
            {/* Selected Session Progress */}
            {selectedSession && (
              <OnboardingProgressEnhanced
                interactive={false}
                showDetails={true}
                compact={false}
              />
            )}

            {/* BCM Status */}
            {bcmStatusSummary && (
              <BlueprintCard className="p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 bg-[var(--success-light)] rounded-[var(--radius-md)] flex items-center justify-center">
                    <Database size={20} className="text-[var(--success)]" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-[var(--ink)]">Business Context</h3>
                    <p className="text-sm text-[var(--muted)]">Latest BCM Status</p>
                  </div>
                </div>

                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-[var(--muted)]">Version</span>
                    <span className="text-sm font-medium text-[var(--ink)]">{bcmStatusSummary.version}</span>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-sm text-[var(--muted)]">Size</span>
                    <span className="text-sm font-medium text-[var(--ink)]">{bcmStatusSummary.size} bytes</span>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-sm text-[var(--muted)]">Tokens</span>
                    <span className="text-sm font-medium text-[var(--ink)]">{bcmStatusSummary.tokenCount}</span>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-sm text-[var(--muted)]">Generated</span>
                    <span className="text-sm font-medium text-[var(--ink)]">
                      {new Date(bcmStatusSummary.generatedAt).toLocaleDateString()}
                    </span>
                  </div>

                  <div className="pt-3 border-t border-[var(--border-subtle)]">
                    <div className="flex items-center gap-2 text-[var(--success)]">
                      <CheckCircle2 size={16} />
                      <span className="text-sm">
                        {bcmStatus === "loading" ? "Syncing BCM" : "BCM Ready"}
                      </span>
                    </div>
                  </div>
                </div>
              </BlueprintCard>
            )}

            {/* Quick Actions */}
            <BlueprintCard className="p-6">
              <h3 className="font-semibold text-[var(--ink)] mb-4">Quick Actions</h3>
              <div className="space-y-3">
                <BlueprintButton
                  variant="outline"
                  size="sm"
                  className="w-full justify-start"
                  disabled={!latestWorkspaceId || bcmStatus === "loading"}
                  onClick={() => {
                    if (!latestWorkspaceId) return;
                    rebuild(true).catch(() => {
                      // errors captured in BCM store state
                    });
                  }}
                >
                  <Zap size={16} className="mr-2" />
                  Generate BCM
                </BlueprintButton>
                <BlueprintButton variant="outline" size="sm" className="w-full justify-start">
                  <FileText size={16} className="mr-2" />
                  Export Session Data
                </BlueprintButton>
                <BlueprintButton variant="outline" size="sm" className="w-full justify-start">
                  <Users size={16} className="mr-2" />
                  View All Sessions
                </BlueprintButton>
              </div>
            </BlueprintCard>
          </div>
        </div>
      </div>
    </div>
  );
}
