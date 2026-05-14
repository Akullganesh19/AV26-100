import React from 'react';
import { 
  TrendingUp, 
  Users, 
  Map as MapIcon, 
  Bell, 
  Activity,
  ArrowUpRight,
  ArrowDownRight
} from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  Cell,
  AreaChart,
  Area
} from 'recharts';
import DistrictMatrix from '../components/DistrictMatrix';

import { useQuery } from '@tanstack/react-query';
import axios from 'axios';

const Dashboard: React.FC = () => {
  const { data: dashboardStats } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: async () => {
      const response = await axios.get(`${import.meta.env.VITE_API_URL}/districts/stats`);
      return response.data;
    }
  });

  const stats = [
    { label: 'System Risk Index', value: dashboardStats?.avg_risk || '42.8', delta: '+2.4%', trend: 'up', icon: Activity },
    { label: 'Active Alerts', value: dashboardStats?.active_alerts || '12', delta: '-1', trend: 'down', icon: Bell },
    { label: 'Population Covered', value: dashboardStats?.population_covered || '4.2M', delta: 'stable', trend: 'neutral', icon: Users },
    { label: 'Monitored Districts', value: dashboardStats?.total_districts || '50', delta: 'all active', trend: 'neutral', icon: MapIcon },
  ];

  const chartData = [
    { name: 'Low', count: 28, color: 'var(--color-risk-low)' },
    { name: 'Medium', count: 14, color: 'var(--color-risk-medium)' },
    { name: 'High', count: 6, color: 'var(--color-risk-high)' },
    { name: 'Critical', count: 2, color: 'var(--color-risk-critical)' },
  ];

  const trendData = [
    { week: 'W1', risk: 35 },
    { week: 'W2', risk: 38 },
    { week: 'W3', risk: 42 },
    { week: 'W4', risk: 40 },
    { week: 'W5', risk: 45 },
    { week: 'W6', risk: 42.8 },
  ];

  return (
    <div className="space-y-8 animate-in fade-in duration-700">
      {/* Page Header */}
      <div className="flex flex-col gap-2">
        <h2 className="text-3xl font-bold tracking-tight text-white">Command Center</h2>
        <p className="text-slate-400 text-sm">Real-time epidemiological monitoring and predictive risk analysis.</p>
      </div>

      {/* Stat Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, i) => {
          const Icon = stat.icon;
          return (
            <div key={i} className="glass-panel p-6 rounded-2xl group hover:border-brand-primary/30 transition-all">
              <div className="flex items-start justify-between">
                <div>
                  <p className="tactical-header">{stat.label}</p>
                  <h3 className="text-3xl font-bold text-white mt-1">{stat.value}</h3>
                  <div className="flex items-center gap-1 mt-2">
                    {stat.trend === 'up' && <ArrowUpRight className="w-3 h-3 text-rose-500" />}
                    {stat.trend === 'down' && <ArrowDownRight className="w-3 h-3 text-emerald-500" />}
                    <span className={`text-xs font-medium ${
                      stat.trend === 'up' ? 'text-rose-500' : 
                      stat.trend === 'down' ? 'text-emerald-500' : 'text-slate-500'
                    }`}>
                      {stat.delta}
                    </span>
                  </div>
                </div>
                <div className="p-3 rounded-xl bg-white/[0.03] text-slate-400 group-hover:text-brand-primary group-hover:bg-brand-primary/10 transition-all">
                  <Icon className="w-5 h-5" />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Chart */}
        <div className="lg:col-span-2 glass-panel p-6 rounded-2xl">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h3 className="text-lg font-bold text-white">Aggregated Risk Trend</h3>
              <p className="text-xs text-slate-500">National 6-week rolling risk average</p>
            </div>
            <div className="flex items-center gap-2 px-3 py-1 rounded-lg bg-white/[0.03] border border-white/[0.05]">
              <TrendingUp className="w-4 h-4 text-brand-primary" />
              <span className="text-xs font-semibold text-slate-300">Live Feed</span>
            </div>
          </div>
          
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trendData}>
                <defs>
                  <linearGradient id="colorRisk" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="var(--color-brand-primary)" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="var(--color-brand-primary)" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
                <XAxis 
                  dataKey="week" 
                  axisLine={false} 
                  tickLine={false} 
                  tick={{ fill: '#64748b', fontSize: 12 }}
                  dy={10}
                />
                <YAxis 
                  axisLine={false} 
                  tickLine={false} 
                  tick={{ fill: '#64748b', fontSize: 12 }}
                  dx={-10}
                />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1a1a1c', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px' }}
                  itemStyle={{ color: '#fff' }}
                />
                <Area 
                  type="monotone" 
                  dataKey="risk" 
                  stroke="var(--color-brand-primary)" 
                  strokeWidth={3}
                  fillOpacity={1} 
                  fill="url(#colorRisk)" 
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Risk Distribution */}
        <div className="glass-panel p-6 rounded-2xl">
          <h3 className="text-lg font-bold text-white mb-8">Risk Distribution</h3>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="rgba(255,255,255,0.05)" />
                <XAxis type="number" hide />
                <YAxis 
                  dataKey="name" 
                  type="category" 
                  axisLine={false} 
                  tickLine={false} 
                  tick={{ fill: '#fff', fontSize: 12, fontWeight: 600 }}
                  width={70}
                />
                <Tooltip 
                   cursor={{ fill: 'rgba(255,255,255,0.03)' }}
                   contentStyle={{ backgroundColor: '#1a1a1c', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px' }}
                />
                <Bar dataKey="count" radius={[0, 4, 4, 0]} barSize={24}>
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-6 space-y-3">
            <p className="text-[10px] uppercase tracking-widest text-slate-500 font-bold">Priority Resolution</p>
            <div className="flex items-center justify-between p-3 rounded-xl bg-rose-500/5 border border-rose-500/10">
              <span className="text-sm font-medium text-rose-400">Critical Outbreak Risk</span>
              <span className="px-2 py-0.5 rounded-full bg-rose-500 text-white text-[10px] font-bold">2 DISTRICTS</span>
            </div>
          </div>
        </div>
      </div>

      {/* District Matrix */}
      <div className="space-y-4">
        <div className="flex flex-col gap-1">
          <h3 className="text-xl font-bold text-white">Operational Jurisdiction Matrix</h3>
          <p className="text-xs text-slate-500">Granular district-level monitoring and target selection.</p>
        </div>
        <DistrictMatrix />
      </div>
    </div>
  );
};

export default Dashboard;
