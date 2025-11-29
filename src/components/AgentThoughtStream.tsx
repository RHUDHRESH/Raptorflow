
import React, { useEffect, useRef } from 'react';
import { useAgentStream, AgentEvent } from '../hooks/useAgentStream';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { Brain, Activity, CheckCircle, AlertTriangle } from 'lucide-react';

export const AgentThoughtStream: React.FC = () => {
  const { events, isConnected } = useAgentStream();
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [events]);

  const getIcon = (type: string) => {
    switch (type) {
      case 'thought': return <Brain className="w-4 h-4 text-blue-500" />;
      case 'action': return <Activity className="w-4 h-4 text-yellow-500" />;
      case 'result': return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'error': return <AlertTriangle className="w-4 h-4 text-red-500" />;
      default: return <Activity className="w-4 h-4" />;
    }
  };

  return (
    <Card className="w-full h-[600px] flex flex-col">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">
          Neural Stream
        </CardTitle>
        <Badge variant={isConnected ? "default" : "destructive"}>
          {isConnected ? "Live" : "Disconnected"}
        </Badge>
      </CardHeader>
      <CardContent className="flex-1 overflow-hidden">
        <ScrollArea className="h-full pr-4">
          <div className="space-y-4">
            {events.map((event) => (
              <div key={event.id} className="flex items-start space-x-3 p-2 rounded-md bg-muted/50">
                <div className="mt-1">{getIcon(event.event_type)}</div>
                <div className="flex-1 space-y-1">
                  <div className="flex items-center justify-between">
                    <p className="text-xs font-medium capitalize">{event.event_type}</p>
                    <span className="text-[10px] text-muted-foreground">
                      {new Date(event.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  <p className="text-sm text-foreground/90 font-mono">
                    {typeof event.payload === 'string' 
                      ? event.payload 
                      : JSON.stringify(event.payload, null, 2)}
                  </p>
                </div>
              </div>
            ))}
            <div ref={scrollRef} />
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
};
