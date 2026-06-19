import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../api/client';
import { Link } from 'react-router-dom';

interface District {
    id: string;
    name: string;
    state_code: string;
    risk_score: number;
    risk_tier: string;
}

const DistrictMatrix: React.FC = () => {
  const { data: districts, isLoading, error } = useQuery<District[]>({
    queryKey: ['districts'],
    queryFn: async () => {
      const response = await apiClient.get('/districts/');
      return response.data;
    }
  });

  if (isLoading) return <div className="text-slate-400">Loading matrix data...</div>;
  if (error) return <div className="text-red-500">Failed to load matrix data</div>;

  return (
    <div className="glass-panel overflow-hidden rounded-2xl">
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-white/10 text-xs uppercase tracking-widest text-slate-500 font-black">
              <th className="p-4 font-medium">District</th>
              <th className="p-4 font-medium">State Code</th>
              <th className="p-4 font-medium">Risk Score</th>
              <th className="p-4 font-medium">Risk Tier</th>
              <th className="p-4 font-medium text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {districts?.map((district) => (
              <tr key={district.id} className="hover:bg-white/[0.02] transition-colors">
                <td className="p-4 font-medium text-white">{district.name}</td>
                <td className="p-4 text-slate-400">{district.state_code}</td>
                <td className="p-4 text-slate-300">{(district.risk_score * 100).toFixed(1)}%</td>
                <td className="p-4">
                  <span className={`px-2 py-1 rounded-md text-[10px] font-black uppercase tracking-widest ${
                    district.risk_tier === 'high' || district.risk_tier === 'critical' ? 'bg-rose-500/20 text-rose-500 border border-rose-500/30' :
                    district.risk_tier === 'medium' ? 'bg-amber-500/20 text-amber-500 border border-amber-500/30' :
                    'bg-emerald-500/20 text-emerald-500 border border-emerald-500/30'
                  }`}>
                    {district.risk_tier}
                  </span>
                </td>
                <td className="p-4 text-right">
                  <Link
                    to={`/diagnostics?district_id=${district.id}`}
                    className="text-brand-primary text-xs font-bold hover:underline"
                  >
                    Diagnose →
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default DistrictMatrix;
