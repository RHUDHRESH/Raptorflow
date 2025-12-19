"use client";

import { useMoves } from "@/lib/hooks/useMoves";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { MoveCard } from "@/components/custom/MoveCard";
import { EmptyState } from "@/components/custom/EmptyState";
import { Rocket } from "lucide-react";

export default function MovesPage() {
  const { data: moves, isLoading } = useMoves();

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Moves</h1>
        <Button>Create Move</Button>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <div
              key={i}
              className="h-32 bg-gray-100 rounded-lg animate-pulse"
            />
          ))}
        </div>
      ) : !moves || moves.length === 0 ? (
        <EmptyState
          title="No moves yet"
          description="Create a campaign and add marketing moves to execute"
          action={{
            label: "Create Campaign",
            onClick: () => {
              // Route to campaigns
            },
          }}
          icon={<Rocket size={40} />}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {moves.map((move) => (
            <MoveCard
              key={move.id}
              move={move}
              onOpen={() => {
                // Open move details
              }}
              onShip={() => {
                // Open ship flow
              }}
            />
          ))}
        </div>
      )}
    </div>
  );
}
