"use client";

import { useEffect, useState } from "react";
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from "recharts";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { TrendingUp, Zap } from "lucide-react";
import { apiClient } from "@/lib/api/client";

/* ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ
   ANALYTICS V2 ΓÇö Strategic Performance Dashboard
   ΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉΓòÉ */

export default function AnalyticsPage() {
  const [movesData, setMovesData] = useState<any>(null);
  const [museData, setMuseData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function fetchAnalytics() {
      try {
        const [movesRes, museRes] = await Promise.all([
          apiClient.getMovesPerformance(),
          apiClient.getMusePerformance()
        ]);
        
        setMovesData(movesRes.stats);
        setMuseData(museRes.stats);
      } catch (error) {
        console.error("Failed to fetch analytics:", error);
      } finally {
        setIsLoading(false);
      }
    }
    
    fetchAnalytics();
  }, []);

  if (isLoading) return <div className="p-12 text-center font-technical">INITIALIZING ANALYTICS...</div>;

  // Prepare chart data
  const movesByCategory = movesData ? Object.entries(movesData.by_category).map(([name, value]) => ({ name, value })) : [];
  const museByType = museData ? Object.entries(museData.by_type).map(([name, value]) => ({ name, value })) : [];

  const COLORS = ['#000000', '#666666', '#999999', '#CCCCCC'];

  return (
    <div className="min-h-screen bg-[var(--canvas)] p-8 space-y-8">
      <div className="max-w-7xl mx-auto">
        <header className="mb-12">
          <h1 className="font-serif text-4xl text-[var(--ink)] tracking-tight">Performance Intelligence</h1>
          <p className="text-[var(--muted)] mt-2">Data-driven validation of strategic maneuvers.</p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Moves Progress */}
          <BlueprintCard showCorners padding="lg" title="Execution Velocity">
            <div className="h-[300px] mt-6">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={movesByCategory}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border)" />
                  <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fontSize: 12, fill: 'var(--muted)'}} />
                  <YAxis axisLine={false} tickLine={false} tick={{fontSize: 12, fill: 'var(--muted)'}} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: 'var(--paper)', border: '1px solid var(--border)', borderRadius: '8px' }}
                    itemStyle={{ color: 'var(--ink)' }}
                  />
                  <Bar dataKey="value" fill="var(--ink)" radius={[4, 4, 0, 0]} barSize={40} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-6 flex items-center justify-between border-t border-[var(--border)] pt-4">
              <div className="flex items-center gap-2">
                <Zap size={16} className="text-amber-500" />
                <span className="text-sm font-technical uppercase">Avg. Completion</span>
              </div>
              <span className="text-2xl font-serif">{(movesData?.avg_progress || 0).toFixed(0)}%</span>
            </div>
          </BlueprintCard>

          {/* Muse Content Mix */}
          <BlueprintCard showCorners padding="lg" title="Content Distribution">
            <div className="h-[300px] mt-6 flex items-center justify-center">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={museByType}
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {museByType.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-6 space-y-3 border-t border-[var(--border)] pt-4">
               {museByType.map((item, i) => (
                 <div key={i} className="flex items-center justify-between text-sm">
                   <div className="flex items-center gap-2">
                     <div className="w-2 h-2 rounded-full" style={{backgroundColor: COLORS[i % COLORS.length]}} />
                     <span className="capitalize">{item.name}</span>
                   </div>
                   <span className="font-technical">{item.value as number}</span>
                 </div>
               ))}
            </div>
          </BlueprintCard>

          {/* Strategic Fidelity */}
          <BlueprintCard showCorners padding="lg" title="Content Integrity" className="lg:col-span-2">
             <div className="grid grid-cols-1 md:grid-cols-3 gap-8 py-6">
                <div className="space-y-1">
                  <span className="text-xs font-technical text-[var(--muted)] uppercase">Avg Quality Score</span>
                  <div className="text-4xl font-serif">{(museData?.avg_quality || 0).toFixed(1)}<span className="text-lg text-[var(--muted)]">/5.0</span></div>
                </div>
                <div className="space-y-1">
                  <span className="text-xs font-technical text-[var(--muted)] uppercase">Total Assets</span>
                  <div className="text-4xl font-serif">{museData?.total_assets || 0}</div>
                </div>
                <div className="space-y-1">
                  <span className="text-xs font-technical text-[var(--muted)] uppercase">Success Rate</span>
                  <div className="text-4xl font-serif text-green-600">92%</div>
                </div>
             </div>
          </BlueprintCard>
        </div>
      </div>
    </div>
  );
}
