import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../api/client';
import { 
  Play, 
  FastForward, 
  RotateCcw, 
  ShieldAlert, 
  Activity, 
  TrendingUp, 
  CheckCircle2,
  AlertTriangle,
  Beaker
} from 'lucide-react';
import { useSimulation } from '../context/SimulationContext';
import StrategicMap from './StrategicMap';
import TacticalAlerts from './TacticalAlerts';

type SimulationView = 'selection' | 'console' | 'debrief';

const SimulationLab: React.FC = () => {
  const queryClient = useQueryClient();
  const { isSimulating, activeSimId, startSimulation, stopSimulation } = useSimulation();
  const [view, setView] = useState<SimulationView>(isSimulating ? 'console' : 'selection');

  // Fetch Scenarios
  const { data: scenarios, isLoading: loadingScenarios } = useQuery({
    queryKey: ['sim-scenarios'],
    queryFn: async () => {
      const response = await apiClient.get(`${import.meta.env.VITE_API_URL}/scenarios/`);
      return response.data;
    }
  });

  // Fetch Active Sim State
  const { data: activeSim } = useQuery({
    queryKey: ['active-sim', activeSimId],
    queryFn: async () => {
      if (!activeSimId) return null;
      const response = await apiClient.get(`${import.meta.env.VITE_API_URL}/scenarios/active`);
      return response.data;
    },
    enabled: !!isSimulating
  });

  // Mutations
  const startMutation = useMutation({
    mutationFn: async (scenarioId: string) => {
      const response = await apiClient.post(`${import.meta.env.VITE_API_URL}/scenarios/${scenarioId}/start`);
      return response.data;
    },
    onSuccess: (data) => {
      startSimulation(data.id);
      setView('console');
      queryClient.invalidateQueries({ queryKey: ['active-sim'] });
    }
  });

  const advanceMutation = useMutation({
    mutationFn: async () => {
      const response = await apiClient.post(`${import.meta.env.VITE_API_URL}/scenarios/active/advance`);
      return response.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries(); // Refresh everything
      if (data.current_day >= 7) { // Mock check for max days for demo
         // setView('debrief'); 
      }
    }
  });

  if (view === 'selection') {
    return (
      <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
        <header>
          <div className="flex items-center gap-3">
            <Beaker className="text-brand-primary h-8 w-8" />
            <h1 className="text-3xl font-bold text-white tracking-tight">Scenario Lab</h1>
          </div>
          <p className="text-slate-400 mt-2 max-w-2xl">
            Controlled environment for regional outbreak simulations and response calibration. 
            Test mission readiness against guided epidemiological threats.
          </p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {scenarios?.map((scenario: any) => (
            <div key={scenario.id} className="glass-panel p-6 rounded-3xl border-white/5 hover:border-brand-primary/30 transition-all group flex flex-col justify-between h-full">
              <div>
                <div className="flex justify-between items-start mb-4">
                   <div className="p-3 rounded-2xl bg-brand-primary/10 text-brand-primary">
                     <TrendingUp size={24} />
                   </div>
                   <span className="text-[10px] font-black uppercase tracking-widest px-3 py-1 bg-white/5 rounded-full text-slate-400">
                     {scenario.total_days} Days
                   </span>
                </div>
                <h3 className="text-xl font-bold text-white mb-2">{scenario.name}</h3>
                <p className="text-sm text-slate-400 leading-relaxed mb-6">
                  {scenario.description}
                </p>
              </div>
              
              <button 
                onClick={() => startMutation.mutate(scenario.id)}
                className="w-full py-4 bg-brand-primary hover:bg-brand-secondary text-white font-bold rounded-xl transition-all flex items-center justify-center gap-2 group-hover:scale-[1.02]"
              >
                <Play size={18} fill="white" />
                Launch Mission
              </button>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (view === 'debrief') {
    return (
      <div className="max-w-4xl mx-auto space-y-8 animate-in zoom-in duration-500">
        <header className="text-center">
          <div className="w-20 h-20 bg-emerald-500/10 text-emerald-500 rounded-full flex items-center justify-center mx-auto mb-6 border border-emerald-500/20 shadow-[0_0_30px_rgba(16,185,129,0.1)]">
            <CheckCircle2 size={40} />
          </div>
          <h1 className="text-4xl font-bold text-white tracking-tighter">Mission Debrief complete</h1>
          <p className="text-slate-400 mt-2 font-mono uppercase tracking-[0.2em] text-xs">Final Intelligence Report // Sector: KA_BENGALURU_URBAN</p>
        </header>

        <div className="grid grid-cols-2 gap-6">
          <div className="glass-panel p-6 rounded-3xl border-white/5 bg-white/[0.01]">
            <p className="text-[10px] font-black uppercase tracking-widest text-slate-500 mb-2">Total Alerts Logged</p>
            <p className="text-4xl font-bold text-white">05</p>
            <div className="mt-4 flex items-center gap-2 text-emerald-500">
              <CheckCircle2 size={14} />
              <span className="text-xs font-bold uppercase">All Acknowledged</span>
            </div>
          </div>
          <div className="glass-panel p-6 rounded-3xl border-white/5 bg-white/[0.01]">
            <p className="text-[10px] font-black uppercase tracking-widest text-slate-500 mb-2">Peak Risk Probability</p>
            <p className="text-4xl font-bold text-white">92.4%</p>
            <div className="mt-4 flex items-center gap-2 text-rose-500">
              <AlertTriangle size={14} />
              <span className="text-xs font-bold uppercase">Tier 4 Critical</span>
            </div>
          </div>
        </div>

        <div className="glass-panel p-8 rounded-3xl border-brand-primary/20 bg-brand-primary/5 space-y-6">
           <div className="space-y-1">
             <h3 className="text-lg font-bold text-white">Mission Summary</h3>
             <p className="text-sm text-slate-400">The simulation has successfully replicated the regional transmission patterns of the selected template. Regional health officers demonstrated 100% response synchronization.</p>
           </div>
           
           <button 
             onClick={() => { stopSimulation(); setView('selection'); }}
             className="w-full py-4 bg-brand-primary hover:bg-brand-secondary text-white font-black uppercase tracking-tighter rounded-xl transition-all shadow-lg"
           >
             Finish Mission & Reset Telemetry
           </button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col gap-6">
      <header className="flex items-center justify-between glass-panel p-4 rounded-2xl border-brand-primary/20 bg-brand-primary/5">
        <div className="flex items-center gap-6">
           <div className="flex flex-col">
             <span className="text-[10px] font-black uppercase tracking-widest text-brand-primary">Active Simulation</span>
             <h2 className="text-lg font-bold text-white">Mission Day {activeSim?.current_day || 0} / {scenarios?.find((s:any) => s.id === activeSim?.scenario_id)?.total_days || 7}</h2>
           </div>
           
           <div className="flex gap-2">
             <button 
               onClick={() => {
                 if (activeSim?.current_day >= (scenarios?.find((s:any) => s.id === activeSim?.scenario_id)?.total_days || 7)) {
                   setView('debrief');
                 } else {
                   advanceMutation.mutate();
                 }
               }}
               disabled={advanceMutation.isPending}
               className="px-6 py-2 bg-brand-primary hover:bg-brand-secondary text-white text-xs font-black uppercase tracking-widest rounded-lg flex items-center gap-2 disabled:opacity-50"
             >
               {activeSim?.current_day >= (scenarios?.find((s:any) => s.id === activeSim?.scenario_id)?.total_days || 7) ? <ShieldAlert size={14}/> : <FastForward size={14} />}
               {activeSim?.current_day >= (scenarios?.find((s:any) => s.id === activeSim?.scenario_id)?.total_days || 7) ? 'Generate Debrief' : 'Advance Day'}
             </button>
             <button 
               onClick={() => { stopSimulation(); setView('selection'); }}
               className="px-4 py-2 bg-white/5 hover:bg-rose-500/10 text-slate-400 hover:text-rose-500 text-xs font-black uppercase tracking-widest rounded-lg flex items-center gap-2 transition-all"
             >
               <RotateCcw size={14} />
               Abort
             </button>
           </div>
        </div>

        <div className="flex items-center gap-4">
           <div className="text-right">
             <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">Live Telemetry</p>
             <p className="text-xs font-mono text-emerald-500">CONNECTED // SIM_MODE</p>
           </div>
           <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
        </div>
      </header>

      <div className="flex-1 grid grid-cols-12 gap-6 overflow-hidden">
        {/* Map Context */}
        <div className="col-span-8 overflow-hidden rounded-3xl border border-white/5 relative">
          <StrategicMap />
          <div className="absolute top-4 left-4 z-[1000] px-3 py-1 bg-brand-primary text-white text-[10px] font-black uppercase tracking-widest rounded-lg shadow-2xl">
            Simulation Overlay
          </div>
        </div>

        {/* Alert Context */}
        <div className="col-span-4 overflow-hidden flex flex-col">
          <TacticalAlerts />
        </div>
      </div>
    </div>
  );
};

export default SimulationLab;
