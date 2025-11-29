
import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useAgentStream, AgentEvent } from '../hooks/useAgentStream';
import { CheckCircle2, Circle, Loader2, AlertCircle } from 'lucide-react';

interface StepStatus {
  step_id: string;
  description: string;
  agent: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
}

export const PlanVisualizer: React.FC = () => {
  const { events } = useAgentStream();
  const [plan, setPlan] = useState<any>(null);
  const [steps, setSteps] = useState<StepStatus[]>([]);

  useEffect(() => {
    // Parse events to reconstruct plan state
    events.forEach(event => {
      if (event.event_type === 'plan') {
        // New plan received
        setPlan(event.payload);
        if (event.payload.steps) {
          setSteps(event.payload.steps.map((s: any) => ({
            ...s,
            status: 'pending'
          })));
        }
      } else if (event.event_type === 'action' || event.event_type === 'result') {
        // Update step status based on correlation/payload
        const stepId = event.payload.step_id; // Assuming payload has step_id
        if (stepId) {
          setSteps(prev => prev.map(s => {
            if (s.step_id === stepId) {
              return {
                ...s,
                status: event.event_type === 'action' ? 'running' : 'completed'
              };
            }
            return s;
          }));
        }
      }
    });
  }, [events]);

  if (!plan) {
    return (
      <Card className="w-full h-full flex items-center justify-center p-8">
        <p className="text-muted-foreground">Waiting for strategic plan...</p>
      </Card>
    );
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex justify-between items-center">
          <span>{plan.plan_name || 'Strategic Execution Plan'}</span>
          <Badge>{plan.objective || 'Objective'}</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {steps.map((step, index) => (
            <div key={step.step_id} className="relative flex gap-4">
              {/* Connecting Line */}
              {index < steps.length - 1 && (
                <div className="absolute left-[15px] top-8 w-0.5 h-full bg-border" />
              )}
              
              {/* Status Icon */}
              <div className="z-10 mt-1">
                {step.status === 'completed' && <CheckCircle2 className="w-8 h-8 text-green-500 bg-background" />}
                {step.status === 'running' && <Loader2 className="w-8 h-8 text-blue-500 animate-spin bg-background" />}
                {step.status === 'pending' && <Circle className="w-8 h-8 text-muted-foreground bg-background" />}
                {step.status === 'failed' && <AlertCircle className="w-8 h-8 text-red-500 bg-background" />}
              </div>

              {/* Content */}
              <div className="flex-1 pb-4">
                <div className="flex items-center justify-between mb-1">
                  <h4 className="font-semibold text-sm">{step.description}</h4>
                  <Badge variant="outline" className="text-xs">{step.agent}</Badge>
                </div>
                <p className="text-xs text-muted-foreground">
                  Status: <span className="capitalize">{step.status}</span>
                </p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};
