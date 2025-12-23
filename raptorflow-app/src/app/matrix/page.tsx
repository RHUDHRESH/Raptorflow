import { Metadata } from "next";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { SystemStatusHeader } from "@/components/matrix/SystemStatusHeader";
import { AgentPoolList } from "@/components/matrix/AgentPoolList";
import { GlobalKillSwitch } from "@/components/matrix/GlobalKillSwitch";
import { DriftChart } from "@/components/matrix/DriftChart";
import { FinancialBurnChart } from "@/components/matrix/FinancialBurnChart";
import { InferenceLogExplorer } from "@/components/matrix/InferenceLogExplorer";
import { Activity, Zap, Shield, AlertTriangle } from "lucide-react";

export const metadata: Metadata = {
  title: "Matrix | RaptorFlow",
  description: "The Agentic Control Center",
};

export default function MatrixPage() {
  return (
    <div className="flex-1 space-y-8 p-8 pt-6 animate-slide-up-fade">
      {/* 1. Page Header (Serif) */}
      <div className="flex items-center justify-between space-y-2">
        <div>
          <h1 className="text-4xl font-display font-semibold tracking-tight text-primary">
            Matrix
          </h1>
          <p className="text-muted-foreground">
            The industrial-grade command and control center for your agentic ecosystem.
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <GlobalKillSwitch />
        </div>
      </div>

      {/* 2. System Status (Phase 092) */}
      <SystemStatusHeader />

      {/* 3. Core Metrics Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Card className="rounded-2xl border-border bg-card/50 shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Agents</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold font-mono">12</div>
            <p className="text-xs text-muted-foreground">
              Across 4 parallel threads
            </p>
          </CardContent>
        </Card>

        <Card className="rounded-2xl border-border bg-card/50 shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">System Latency</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold font-mono">142ms</div>
            <p className="text-xs text-muted-foreground">
              P95 across all inference calls
            </p>
          </CardContent>
        </Card>

        <Card className="rounded-2xl border-border bg-card/50 shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Financial Burn</CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold font-mono">$12.45</div>
            <p className="text-xs text-muted-foreground">
              Estimated daily token cost
            </p>
          </CardContent>
        </Card>

        <Card className="rounded-2xl border-border bg-card/50 shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Data Drift</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold font-mono">0.02</div>
            <Badge variant="outline" className="mt-1 font-mono text-[10px] text-green-600 bg-green-50 border-green-200">
              STABLE
            </Badge>
          </CardContent>
        </Card>
      </div>

                        {/* 4. Secondary Panels */}

                        <div className="grid gap-6 lg:grid-cols-12">

                          <div className="lg:col-span-4">

                            <AgentPoolList />

                          </div>

                          

                          <div className="lg:col-span-4">

                            <InferenceLogExplorer />

                          </div>

                  

                          <div className="lg:col-span-4">

                            <div className="flex flex-col space-y-6">

                              <DriftChart />

                              <FinancialBurnChart />

                            </div>

                          </div>

                        </div>

                      </div>

                  

      
  );
}
