"use client";

import { useTodaysMoves } from "@/lib/hooks/useMoves";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { DailyChecklist } from "@/components/custom/DailyChecklist";
import { EmptyState } from "@/components/custom/EmptyState";
import { CheckCircle2, Zap } from "lucide-react";
import { formatDateTime } from "@/lib/utils/formatters";

export default function DashboardPage() {
  const { data: todaysMoves, isLoading } = useTodaysMoves();

  const items = (todaysMoves || []).map((move) => ({
    id: move.id,
    text: move.title,
    completed: move.status === "completed",
    dueTime: move.due_date ? formatDateTime(move.due_date) : undefined,
  }));

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Good Morning</h1>
        <p className="text-gray-600">
          {new Date().toLocaleDateString("en-US", {
            weekday: "long",
            month: "long",
            day: "numeric",
          })}
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-lg">Today's Moves</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="space-y-3">
                {[1, 2, 3].map((i) => (
                  <div
                    key={i}
                    className="h-16 bg-gray-100 rounded-md animate-pulse"
                  />
                ))}
              </div>
            ) : items.length === 0 ? (
              <EmptyState
                title="No moves today"
                description="Create a campaign to get started"
                action={{
                  label: "Create Campaign",
                  onClick: () => {
                    // Route to campaigns
                  },
                }}
                icon={<Zap size={40} />}
              />
            ) : (
              <DailyChecklist items={items} />
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Quick Stats</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                <div className="flex items-center gap-2 mb-2">
                  <CheckCircle2 size={20} className="text-green-600" />
                  <p className="text-sm font-semibold text-green-900">
                    Completed Today
                  </p>
                </div>
                <p className="text-2xl font-bold text-green-600">
                  {items.filter((i) => i.completed).length}
                </p>
              </div>

              <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                <p className="text-sm font-semibold text-blue-900 mb-2">
                  Pending Moves
                </p>
                <p className="text-2xl font-bold text-blue-600">
                  {items.filter((i) => !i.completed).length}
                </p>
              </div>

              <Button variant="outline" className="w-full">
                View All Moves
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
