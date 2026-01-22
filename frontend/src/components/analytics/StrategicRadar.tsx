
"use client";

import { PolarAngleAxis, PolarGrid, PolarRadiusAxis, Radar, RadarChart, ResponsiveContainer } from "recharts";
import { MoveCategory } from "@/components/moves/types";

interface StrategicRadarProps {
    scores?: Record<MoveCategory, number>;
}

export function StrategicRadar({ scores }: StrategicRadarProps) {
    const data = [
        { subject: "Authority", A: scores?.authority || 0, fullMark: 100 },
        { subject: "Capture", A: scores?.capture || 0, fullMark: 100 },
        { subject: "Ignite", A: scores?.ignite || 0, fullMark: 100 },
        { subject: "Rally", A: scores?.rally || 0, fullMark: 100 },
        { subject: "Repair", A: scores?.repair || 0, fullMark: 100 },
    ];

    return (
        <div className="w-full h-[300px] relative">
            <ResponsiveContainer width="100%" height="100%">
                <RadarChart cx="50%" cy="50%" outerRadius="70%" data={data}>
                    <PolarGrid stroke="var(--structure)" strokeOpacity={0.5} />
                    <PolarAngleAxis
                        dataKey="subject"
                        tick={{ fill: "var(--ink-secondary)", fontSize: 10, fontFamily: "var(--font-technical)" }}
                    />
                    <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                    <Radar
                        name="Strategy"
                        dataKey="A"
                        stroke="var(--blueprint)"
                        strokeWidth={2}
                        fill="var(--blueprint)"
                        fillOpacity={0.2}
                    />
                </RadarChart>
            </ResponsiveContainer>
        </div>
    );
}
