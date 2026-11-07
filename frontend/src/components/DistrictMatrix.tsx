import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../api/client';
import { Activity, Star } from 'lucide-react';
import { useSimulation } from '../context/SimulationContext';

const DistrictMatrix: React.FC = () => {
  const [viewMode, setViewMode] = useState<'national' | 'jurisdiction'>('national');
  const { isSimulating, activeSimId } = useSimulation();
  const queryClient = useQueryClient();

  const { data: districts, isLoading } = useQuery({
    queryKey: ['districts', viewMode, isSimulating, activeSimId],
    queryFn: async () => {
      const params = viewMode === 'jurisdiction' ? { jurisdiction_only: true } : {};
      const url = isSimulating ? '/districts' : '/districts';
      const response = await apiClient.get(url, { params });
      return response.data;
    }
  });

  const watchMutation = useMutation({
    mutationFn: async ({ id, watch }: { id: string, watch: boolean }) => {
      if (watch) {
        await apiClient.post(`/districts/${id}/watch`);
      } else {
        await apiClient.delete(`/districts/${id}/watch`);
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['districts'] });
    }
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-12 glass-panel rounded-2xl">
        <Activity className="w-8 h-8 text-brand-primary animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex gap-2 p-1 bg-white/[0.02] rounded-xl w-fit border border-white/[0.05]">
        <button
          onClick={() => setViewMode('national')}
          className={`px-4 py-2 rounded-lg text-xs font-bold transition-all ${
            viewMode === 'national'
              ? 'bg-brand-primary text-white shadow-lg'
              : 'text-slate-400 hover:text-white hover:bg-white/5'
          }`}
        >
          National Overview
        </button>
        <button
          onClick={() => setViewMode('jurisdiction')}
          className={`px-4 py-2 rounded-lg text-xs font-bold transition-all flex items-center gap-2 ${
            viewMode === 'jurisdiction'
              ? 'bg-brand-primary text-white shadow-lg'
              : 'text-slate-400 hover:text-white hover:bg-white/5'
          }`}
        >
          <Star size={14} className={viewMode === 'jurisdiction' ? 'fill-white' : ''} />
          My Jurisdiction
        </button>
      </div>

      <div className="glass-panel rounded-2xl overflow-hidden">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-white/5 bg-white/[0.02]">
              <th className="p-4 text-xs font-black uppercase tracking-widest text-slate-500">District</th>
              <th className="p-4 text-xs font-black uppercase tracking-widest text-slate-500">State</th>
              <th className="p-4 text-xs font-black uppercase tracking-widest text-slate-500">Risk Score</th>
              <th className="p-4 text-xs font-black uppercase tracking-widest text-slate-500">Risk Tier</th>
              <th className="p-4 text-xs font-black uppercase tracking-widest text-slate-500 text-right">Watch</th>
            </tr>
          </thead>
          <tbody>
            {districts?.map((d: any) => (
              <tr key={d.id} className="border-b border-white/5 hover:bg-white/[0.02] transition-colors">
                <td className="p-4 font-medium text-white">{d.name}</td>
                <td className="p-4 text-slate-400">{d.state}</td>
                <td className="p-4 font-mono text-brand-primary">{Number(d.risk_score).toFixed(1)}</td>
                <td className="p-4">
                  <span className={`px-2 py-1 rounded-md text-[10px] font-bold uppercase tracking-wider ${
                    d.risk_tier === 'critical' ? 'bg-rose-500/20 text-rose-400 border border-rose-500/20' :
                    d.risk_tier === 'high' ? 'bg-orange-500/20 text-orange-400 border border-orange-500/20' :
                    d.risk_tier === 'medium' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/20' :
                    'bg-emerald-500/20 text-emerald-400 border border-emerald-500/20'
                  }`}>
                    {d.risk_tier}
                  </span>
                </td>
                <td className="p-4 text-right">
                  <button
                    onClick={() => watchMutation.mutate({ id: d.id, watch: !d.is_watched })}
                    className={`p-2 rounded-lg transition-all ${
                      d.is_watched
                        ? 'text-brand-primary bg-brand-primary/10 hover:bg-brand-primary/20'
                        : 'text-slate-500 hover:text-white hover:bg-white/10'
                    }`}
                  >
                    <Star size={16} className={d.is_watched ? 'fill-current' : ''} />
                  </button>
                </td>
              </tr>
            ))}
            {districts?.length === 0 && (
              <tr>
                <td colSpan={5} className="p-8 text-center text-slate-500">
                  {viewMode === 'jurisdiction'
                    ? "No districts in your jurisdiction. Watch districts from the National Overview."
                    : "No districts found."}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default DistrictMatrix;
