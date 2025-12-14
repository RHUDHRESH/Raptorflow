import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { TrendingUp, TrendingDown, Activity, Users, DollarSign, ShoppingCart } from 'lucide-react';

const generateMockData = (period = '7d') => {
  const days = period === '7d' ? 7 : period === '30d' ? 30 : 90;
  const data = [];
  
  for (let i = 0; i < days; i++) {
    const date = new Date();
    date.setDate(date.getDate() - (days - i));
    
    data.push({
      date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      revenue: Math.floor(Math.random() * 5000) + 3000,
      users: Math.floor(Math.random() * 200) + 100,
      orders: Math.floor(Math.random() * 100) + 50,
      conversion: (Math.random() * 5 + 2).toFixed(1),
    });
  }
  
  return data;
};

const pieData = [
  { name: 'Direct', value: 400, color: '#8884d8' },
  { name: 'Social', value: 300, color: '#82ca9d' },
  { name: 'Referral', value: 300, color: '#ffc658' },
  { name: 'Organic', value: 200, color: '#ff7c7c' },
];

export function RevenueChart({ period, setPeriod }) {
  const [data, setData] = useState([]);
  
  useEffect(() => {
    setData(generateMockData(period));
  }, [period]);

  return (
    <Card className="col-span-2 bg-zinc-900/50 border border-white/5">
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle className="flex items-center gap-2 text-white">
            <DollarSign className="w-5 h-5 text-green-400" />
            Revenue Overview
          </CardTitle>
          <CardDescription className="text-white/40">Daily revenue trends</CardDescription>
        </div>
        <Select value={period} onValueChange={setPeriod}>
          <SelectTrigger className="w-[120px] bg-white/5 border-white/10 text-white">
            <SelectValue />
          </SelectTrigger>
          <SelectContent className="bg-zinc-900 border-white/10">
            <SelectItem value="7d" className="text-white hover:bg-white/5">7 days</SelectItem>
            <SelectItem value="30d" className="text-white hover:bg-white/5">30 days</SelectItem>
            <SelectItem value="90d" className="text-white hover:bg-white/5">90 days</SelectItem>
          </SelectContent>
        </Select>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={data}>
            <defs>
              <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#8884d8" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#8884d8" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="date" stroke="#888" fontSize={12} />
            <YAxis stroke="#888" fontSize={12} />
            <Tooltip 
              contentStyle={{ backgroundColor: '#fff', border: '1px solid #e2e8f0', borderRadius: '8px' }}
              labelStyle={{ color: '#1a202c', fontWeight: 'bold' }}
            />
            <Area 
              type="monotone" 
              dataKey="revenue" 
              stroke="#8884d8" 
              fillOpacity={1} 
              fill="url(#colorRevenue)"
              strokeWidth={2}
            />
          </AreaChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}

export function UserActivityChart() {
  const [data, setData] = useState([]);
  
  useEffect(() => {
    setData(generateMockData('7d'));
  }, []);

  return (
    <Card className="bg-zinc-900/50 border border-white/5">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-white">
          <Users className="w-5 h-5 text-blue-400" />
          User Activity
        </CardTitle>
        <CardDescription className="text-white/40">Daily active users</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="date" stroke="#888" fontSize={12} />
            <YAxis stroke="#888" fontSize={12} />
            <Tooltip 
              contentStyle={{ backgroundColor: '#fff', border: '1px solid #e2e8f0', borderRadius: '8px' }}
            />
            <Line 
              type="monotone" 
              dataKey="users" 
              stroke="#3b82f6" 
              strokeWidth={2}
              dot={{ fill: '#3b82f6', r: 4 }}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}

export function TrafficSourcesChart() {
  return (
    <Card className="bg-zinc-900/50 border border-white/5">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-white">
          <Activity className="w-5 h-5 text-purple-400" />
          Traffic Sources
        </CardTitle>
        <CardDescription className="text-white/40">Where your users come from</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={200}>
          <PieChart>
            <Pie
              data={pieData}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={80}
              paddingAngle={5}
              dataKey="value"
            >
              {pieData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
        <div className="grid grid-cols-2 gap-2 mt-4">
          {pieData.map((item, index) => (
            <div key={index} className="flex items-center gap-2">
              <div 
                className="w-3 h-3 rounded-full" 
                style={{ backgroundColor: item.color }}
              />
              <span className="text-sm text-white/60">{item.name}</span>
              <Badge variant="secondary" className="ml-auto bg-white/10 text-white/60">
                {item.value}
              </Badge>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

export function ConversionRateChart() {
  const [data, setData] = useState([]);
  
  useEffect(() => {
    setData(generateMockData('7d'));
  }, []);

  return (
    <Card className="bg-zinc-900/50 border border-white/5">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-white">
          <ShoppingCart className="w-5 h-5 text-orange-400" />
          Conversion Rate
        </CardTitle>
        <CardDescription className="text-white/40">Daily conversion percentage</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="date" stroke="#888" fontSize={12} />
            <YAxis stroke="#888" fontSize={12} />
            <Tooltip 
              contentStyle={{ backgroundColor: '#fff', border: '1px solid #e2e8f0', borderRadius: '8px' }}
            />
            <Bar 
              dataKey="conversion" 
              fill="#f97316" 
              radius={[4, 4, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
