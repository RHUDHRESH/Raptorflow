"use client"

import * as React from "react"
import { Area, AreaChart, CartesianGrid, XAxis, YAxis } from "recharts"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import {
    ChartConfig,
    ChartContainer,
    ChartTooltip,
    ChartTooltipContent,
} from "@/components/ui/chart"
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select"
import { cn } from "@/lib/utils"

const chartConfig = {
    tokens: {
        label: "Tokens",
        color: "hsl(var(--chart-1))",
    },
} satisfies ChartConfig

// Mock data generator for "cool" curves
const generateData = (days: number) => {
    const data = []
    let value = 1500
    for (let i = 0; i < days; i++) {
        // Random walk with trend
        const change = (Math.random() - 0.4) * 800
        value = Math.max(500, value + change)
        data.push({
            date: new Date(Date.now() - (days - 1 - i) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
            tokens: Math.round(value),
        })
    }
    return data
}

const timeRanges = [
    { label: "Last 24 Hours", value: "1d", days: 24, interval: "hour" }, // Simulated
    { label: "Last 3 Days", value: "3d", days: 3 },
    { label: "Last Week", value: "7d", days: 7 },
    { label: "Last Month", value: "30d", days: 30 },
]

export function UsageChart() {
    const [timeRange, setTimeRange] = React.useState("7d")
    const [data, setData] = React.useState(generateData(7))

    React.useEffect(() => {
        const range = timeRanges.find(r => r.value === timeRange)
        if (range) {
            // In a real app, you'd fetch data here.
            // For "1d", we'd generate hourly data, but keeping it simple for now with mocks.
            setData(generateData(range.days))
        }
    }, [timeRange])

    const totalTokens = React.useMemo(() => {
        return data.reduce((acc, curr) => acc + curr.tokens, 0)
    }, [data])

    return (
        <Card className="col-span-1 md:col-span-2 border-border/50 shadow-sm transition-all hover:shadow-md bg-card/50 backdrop-blur-sm">
            <CardHeader className="flex items-center gap-2 space-y-0 border-b border-border/50 py-5 sm:flex-row">
                <div className="grid flex-1 gap-1 text-center sm:text-left">
                    <CardTitle className="text-lg font-serif italic tracking-tight">Generation Velocity</CardTitle>
                    <CardDescription className="text-xs uppercase tracking-widest opacity-60">
                        Total Output: {totalTokens.toLocaleString()} Tokens
                    </CardDescription>
                </div>
                <Select value={timeRange} onValueChange={setTimeRange}>
                    <SelectTrigger
                        className="w-[160px] rounded-lg sm:ml-auto"
                        aria-label="Select a time range"
                    >
                        <SelectValue placeholder="Last 3 months" />
                    </SelectTrigger>
                    <SelectContent className="rounded-xl">
                        {timeRanges.map((range) => (
                            <SelectItem key={range.value} value={range.value} className="rounded-lg">
                                {range.label}
                            </SelectItem>
                        ))}
                    </SelectContent>
                </Select>
            </CardHeader>
            <CardContent className="px-2 pt-4 sm:px-6 sm:pt-6">
                <ChartContainer
                    config={chartConfig}
                    className="aspect-auto h-[250px] w-full"
                >
                    <AreaChart data={data}>
                        <defs>
                            <linearGradient id="fillTokens" x1="0" y1="0" x2="0" y2="1">
                                <stop
                                    offset="5%"
                                    stopColor="var(--color-tokens)"
                                    stopOpacity={0.8}
                                />
                                <stop
                                    offset="95%"
                                    stopColor="var(--color-tokens)"
                                    stopOpacity={0.1}
                                />
                            </linearGradient>
                        </defs>
                        <CartesianGrid vertical={false} strokeDasharray="3 3" strokeOpacity={0.2} />
                        <XAxis
                            dataKey="date"
                            tickLine={false}
                            axisLine={false}
                            tickMargin={8}
                            minTickGap={32}
                            tickFormatter={(value) => {
                                const date = new Date(value)
                                return date.toLocaleDateString("en-US", {
                                    month: "short",
                                    day: "numeric",
                                })
                            }}
                        />
                        <ChartTooltip
                            cursor={false}
                            content={
                                <ChartTooltipContent
                                    labelFormatter={(value) => {
                                        return new Date(value).toLocaleDateString("en-US", {
                                            month: "short",
                                            day: "numeric",
                                            year: "numeric"
                                        })
                                    }}
                                    indicator="dot"
                                />
                            }
                        />
                        <Area
                            dataKey="tokens"
                            type="natural"
                            fill="url(#fillTokens)"
                            stroke="var(--color-tokens)"
                            strokeWidth={2} // Premium subtle stroke
                            dot={false} // Clean line
                        //   activeDot={{ r: 4, strokeWidth: 0 }} // Minimal active dot
                        />
                    </AreaChart>
                </ChartContainer>
            </CardContent>
        </Card>
    )
}
