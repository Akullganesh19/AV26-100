import React from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import { Activity } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const DistrictMatrix: React.FC = () => {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { data: districts, isLoading } = useQuery({
    queryKey: ['districts-matrix'],
    queryFn: async () => {
      const response = await axios.get(`${import.meta.env.VITE_API_URL}/districts`);
      return response.data;
    }
  });

  const handleMouseEnter = (districtId: string) => {
    // Prefetch district detail
    queryClient.prefetchQuery({
      queryKey: ['district-detail', districtId],
      queryFn: async () => {
        const response = await axios.get(`${import.meta.env.VITE_API_URL}/districts/${districtId}`);
        return response.data;
      },
      staleTime: 60 * 1000, // Keep fresh for 1 minute
    });
  };

  if (isLoading) {
    return (
      <div className="flex justify-center p-8">
        <Activity className="animate-spin text-brand-primary" />
      </div>
    );
  }

  return (
    <div className="glass-panel p-6 rounded-2xl overflow-x-auto">
      <table className="w-full text-left border-collapse">
        <thead>
          <tr className="border-b border-white/10 text-xs font-semibold text-slate-400 uppercase tracking-wider">
            <th className="py-4 px-4">District</th>
            <th className="py-4 px-4">State</th>
            <th className="py-4 px-4">Risk Tier</th>
            <th className="py-4 px-4">Probability</th>
            <th className="py-4 px-4">Last Updated</th>
          </tr>
        </thead>
        <tbody>
          {districts?.map((d: any) => (
            <tr
              key={d.id}
              className="border-b border-white/5 hover:bg-white/5 transition-colors cursor-pointer"
              onMouseEnter={() => handleMouseEnter(d.id)}
              onClick={() => navigate(`/district/${d.id}`)}
            >
              <td className="py-4 px-4 font-bold text-white">{d.name}</td>
              <td className="py-4 px-4 text-slate-300">{d.state}</td>
              <td className="py-4 px-4">
                <span className={`px-2 py-1 rounded text-xs font-bold ${
                  d.risk_tier === 'HIGH' ? 'bg-rose-500/20 text-rose-400' :
                  d.risk_tier === 'MEDIUM' ? 'bg-amber-500/20 text-amber-400' :
                  d.risk_tier === 'LOW' ? 'bg-emerald-500/20 text-emerald-400' :
                  'bg-slate-500/20 text-slate-400'
                }`}>
                  {d.risk_tier}
                </span>
              </td>
              <td className="py-4 px-4 text-slate-300">{(d.risk_score * 100).toFixed(1)}%</td>
              <td className="py-4 px-4 text-slate-400 text-sm">{new Date(d.last_updated).toLocaleDateString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default DistrictMatrix;
