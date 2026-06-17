import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import { 
  ShieldAlert, 
  CheckCircle2, 
  AlertTriangle, 
  Clock, 
  MapPin, 
  Activity,
  ChevronRight,
  Filter
} from 'lucide-react';
import { toast } from 'sonner';

interface Alert {
  id: string;
  district_name: string;
  disease: string;
  risk_score: number;
  status: 'triggered' | 'acknowledged' | 'resolved';
  alert_type: 'autonomous' | 'clinical_cluster' | 'environmental';
  triggered_at: string;
  metadata_json?: string;
}

import { useSimulation } from '../context/SimulationContext';
import { useOracle } from '../hooks/useOracle';

const TacticalAlerts: React.FC = () => {
  const queryClient = useQueryClient();
  const { isSimulating, activeSimId } = useSimulation();
  const oracle = useOracle();
  
  const { data: alerts, isLoading } = useQuery<Alert[]>({
    queryKey: ['tactical-alerts', isSimulating, activeSimId],
    queryFn: async () => {
      const url = isSimulating 
        ? `${import.meta.env.VITE_API_URL}/alerts?simulation_id=${activeSimId}`
        : `${import.meta.env.VITE_API_URL}/alerts`;
      const response = await axios.get(url);
      return response.data;
    },
    refetchInterval: 30000 
  });

  const acknowledgeMutation = useMutation({
    mutationFn: (alertId: string) => 
      axios.post(`${import.meta.env.VITE_API_URL}/alerts/${alertId}/acknowledge`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tactical-alerts'] });
      toast.success('Mission alert acknowledged');

      // Oracle prediction: user will want to simulate response
      oracle.predictPostAlertAcknowledge();
    }
  });

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-4">
        <Activity className="animate-spin text-brand-primary" />
        <p className="text-slate-500 font-mono text-xs uppercase tracking-widest">Scanning Tactical Frequency...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight flex items-center gap-3">
            <ShieldAlert className="text-rose-500 h-8 w-8" />
            Tactical Alert Feed
          </h1>
          <p className="text-slate-400 mt-1">
            Real-time mission critical threats and cluster detections.
          </p>
        </div>
        
        <div className="flex gap-2">
           <button className="flex items-center gap-2 px-3 py-1.5 rounded-lg glass-panel border-white/5 text-slate-400 text-xs hover:bg-white/5 transition-all">
             <Filter size={14} />
             Filter Results
           </button>
        </div>
      </header>

      <div className="grid grid-cols-1 gap-4">
        {alerts?.length === 0 ? (
          <div className="p-12 rounded-3xl border border-dashed border-slate-800 flex flex-col items-center gap-4">
            <CheckCircle2 className="h-12 w-12 text-emerald-500/20" />
            <p className="text-slate-500 text-sm">No active threats detected in mission space.</p>
          </div>
        ) : (
          alerts?.map((alert) => (
            <div 
              key={alert.id}
              className={`group relative overflow-hidden p-6 rounded-2xl border transition-all duration-300 hover:shadow-2xl ${
                alert.status === 'triggered' 
                ? 'bg-rose-500/5 border-rose-500/20 shadow-lg shadow-rose-500/5' 
                : 'bg-slate-900/40 border-slate-800'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex gap-4">
                  <div className={`p-3 rounded-xl ${
                    alert.status === 'triggered' ? 'bg-rose-500/20' : 'bg-slate-800'
                  }`}>
                    {alert.alert_type === 'clinical_cluster' ? (
                       <Activity className={alert.status === 'triggered' ? 'text-rose-500' : 'text-slate-400'} />
                    ) : (
                       <AlertTriangle className={alert.status === 'triggered' ? 'text-rose-500' : 'text-slate-400'} />
                    )}
                  </div>
                  
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                       <span className={`text-[10px] font-black uppercase tracking-widest px-2 py-0.5 rounded ${
                         alert.status === 'triggered' ? 'bg-rose-500 text-white' : 'bg-slate-800 text-slate-400'
                       }`}>
                         {alert.alert_type.replace('_', ' ')}
                       </span>
                       <span className="text-slate-500 text-xs">•</span>
                       <span className="text-slate-500 text-xs flex items-center gap-1">
                         <Clock size={12} /> {new Date(alert.triggered_at).toLocaleTimeString()}
                       </span>
                    </div>
                    
                    <h3 className="text-lg font-bold text-white flex items-center gap-2">
                       {alert.disease.toUpperCase()} DETECTED
                       <ChevronRight className="h-4 w-4 text-slate-600" />
                       <span className="text-slate-400">{alert.district_name}</span>
                    </h3>
                    
                    {alert.metadata_json && (
                      <p className="text-slate-400 text-sm mt-1 font-mono">
                        {JSON.parse(alert.metadata_json).cluster_size} High-Risk Screenings confirmed level.
                      </p>
                    )}
                  </div>
                </div>

                <div className="flex flex-col items-end gap-3">
                  <div className="text-right">
                    <p className="text-[10px] uppercase tracking-widest text-slate-500 font-bold">Risk Weight</p>
                    <p className={`text-xl font-black ${alert.status === 'triggered' ? 'text-rose-400' : 'text-slate-400'}`}>
                      {(alert.risk_score * 100).toFixed(1)}%
                    </p>
                  </div>
                  
                  {alert.status === 'triggered' && (
                    <button 
                      onClick={() => acknowledgeMutation.mutate(alert.id)}
                      disabled={acknowledgeMutation.isPending}
                      className="px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white text-xs font-bold rounded-lg transition-all shadow-lg shadow-rose-600/20"
                    >
                      {acknowledgeMutation.isPending ? 'Logging...' : 'ACKNOWLEDGE MISSION THREAT'}
                    </button>
                  )}
                  {alert.status === 'acknowledged' && (
                    <div className="flex items-center gap-2 text-emerald-500 text-xs font-bold bg-emerald-500/10 px-3 py-2 rounded-lg border border-emerald-500/20">
                      <CheckCircle2 size={14} />
                      MISSION ACKNOWLEDGED
                    </div>
                  )}
                </div>
              </div>
              
              {/* Subtle Ambient Background for Triggered Alerts */}
              {alert.status === 'triggered' && (
                <div className="absolute inset-0 bg-gradient-to-r from-rose-500/5 to-transparent pointer-events-none" />
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default TacticalAlerts;
