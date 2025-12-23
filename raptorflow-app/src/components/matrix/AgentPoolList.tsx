"use client";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Activity, Cpu, Clock } from "lucide-react";
import { useMatrixOverview } from "@/hooks/useMatrixOverview";

export function AgentPoolList() {
  const { data } = useMatrixOverview("verify_ws");
  const agents = data?.system_state?.active_agents || {};
  const agentIds = Object.keys(agents);

  return (
    <Card className="rounded-2xl border-border bg-card/50 shadow-sm overflow-hidden h-full">
      <CardHeader className="border-b border-border/50 bg-muted/5">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="font-display text-xl">Agent Pool</CardTitle>
            <CardDescription className="text-xs">Active cognitive threads in parallel.</CardDescription>
          </div>
          <Badge variant="outline" className="font-mono text-xs">
            {agentIds.length} ACTIVE
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="p-0">
        <ScrollArea className="h-[400px]">
          <div className="divide-y divide-border/50">
            {agentIds.length === 0 ? (
              <div className="p-12 text-center text-muted-foreground italic text-sm">
                No active threads detected.
              </div>
            ) : (
              agentIds.map((id) => (
                <div key={id} className="p-4 hover:bg-muted/10 transition-colors">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="p-2 rounded-lg bg-primary/5 border border-primary/10">
                        <Cpu className="h-4 w-4 text-primary" />
                      </div>
                      <div>
                        <h4 className="text-sm font-bold font-sans tracking-tight">{id}</h4>
                        <p className="text-xs text-muted-foreground line-clamp-1">
                          {agents[id].current_task || "Awaiting task..."}
                        </p>
                      </div>
                    </div>
                    <Badge className="bg-green-500/10 text-green-600 border-green-200 hover:bg-green-500/20 text-[10px]">
                      LIVE
                    </Badge>
                  </div>
                  
                  <div className="mt-3 flex items-center space-x-4 text-[10px] text-muted-foreground font-medium uppercase tracking-wider">
                    <div className="flex items-center">
                      <Activity className="mr-1 h-3 w-3" />
                      Inference Active
                    </div>
                    <div className="flex items-center">
                      <Clock className="mr-1 h-3 w-3" />
                      {new Date(agents[id].last_heartbeat).toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
