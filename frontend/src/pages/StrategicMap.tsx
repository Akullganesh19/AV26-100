import React, { useMemo } from 'react';
import { MapContainer, TileLayer, GeoJSON, Tooltip, ZoomControl } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import { ShieldAlert, Activity, Users, Map as MapIcon } from 'lucide-react';
import indiaDistricts from '../assets/india_districts.json';

// Theme for the Tactical Map
const RISK_COLORS: Record<string, string> = {
  HIGH: "#e11d48", // Rose 600
  MEDIUM: "#f59e0b", // Amber 500
  LOW: "#10b981", // Emerald 500
  UNKNOWN: "#475569" // Slate 600
};

import { useSimulation } from '../context/SimulationContext';

const StrategicMap: React.FC = () => {
  const { isSimulating, activeSimId } = useSimulation();
  const queryClient = useQueryClient();

  const { data: districtData, isLoading } = useQuery({
    queryKey: ['choropleth-data', isSimulating, activeSimId],
    queryFn: async () => {
      const url = isSimulating 
        ? `${import.meta.env.VITE_API_URL}/districts` // Simulation could have its own mapping
        : `${import.meta.env.VITE_API_URL}/districts`;
      const response = await axios.get(url);
      return response.data;
    }
  });

  const riskMap = useMemo(() => {
    if (!districtData) return {};
    return Object.fromEntries(districtData.map((d: any) => [d.id, d]));
  }, [districtData]);

  const stats = useMemo(() => {
    if (!districtData) return { HIGH: 0, MEDIUM: 0, LOW: 0 };
    return districtData.reduce((acc: any, curr: any) => {
      const tier = curr.risk_tier.toUpperCase();
      acc[tier] = (acc[tier] || 0) + 1;
      return acc;
    }, { HIGH: 0, MEDIUM: 0, LOW: 0 });
  }, [districtData]);

  const styleFeature = (feature: any) => {
    const districtId = feature.properties.district_id;
    const district = riskMap[districtId];
    return {
      fillColor: RISK_COLORS[district?.risk_tier || "UNKNOWN"],
      fillOpacity: 0.7,
      color: "#1f2937",
      weight: 0.8,
    };
  };

  const onEachFeature = (feature: any, layer: any) => {
    const districtId = feature.properties.district_id;
    const d = riskMap[districtId];
    if (d) {
      // 🛸 Oracle: Predict user will investigate HIGH/CRITICAL districts if they hover
      layer.on('mouseover', () => {
        if (d.risk_tier === 'HIGH' || d.risk_tier === 'CRITICAL') {
          queryClient.prefetchQuery({
            queryKey: ['district-detail', districtId],
            queryFn: async () => {
              const response = await axios.get(`${import.meta.env.VITE_API_URL}/districts/${districtId}`);
              return response.data;
            },
            staleTime: 60000
          });
        }
      });

      layer.bindTooltip(`
        <div class="tactical-tooltip p-3">
          <strong class="text-brand-primary text-base">${d.name}</strong><br/>
          <div class="mt-1 space-y-1">
            <span class="text-[10px] uppercase tracking-widest text-slate-400">Risk Tier:</span>
            <span class="text-xs font-bold text-white ml-2">${d.risk_tier}</span><br/>
            <span class="text-[10px] uppercase tracking-widest text-slate-400">Probability:</span>
            <span class="text-xs font-bold text-white ml-2">${(d.risk_score * 100).toFixed(1)}%</span>
          </div>
          <div class="mt-3 pt-2 border-t border-white/10">
            <a href="/diagnostics?district_id=${districtId}" class="text-[10px] font-black uppercase text-brand-primary hover:underline">
              Initiate Clinical Triage →
            </a>
          </div>
        </div>
      `, { sticky: true, className: 'glass-panel border-white/10 rounded-xl overflow-hidden shadow-2xl' });
    }
  };

  if (isLoading) {
    return (
      <div className="h-[calc(100vh-12rem)] flex items-center justify-center glass-panel rounded-3xl">
        <div className="flex flex-col items-center gap-4">
          <Activity className="w-12 h-12 text-brand-primary animate-spin" />
          <p className="text-slate-400 font-mono tracking-widest uppercase">Initializing Geospatial Overlays...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 flex flex-col h-[calc(100vh-12rem)]">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight flex items-center gap-3">
            <MapIcon className="text-brand-primary h-8 w-8" />
            Strategic Risk Matrix
          </h1>
          <p className="text-slate-400 mt-1">
            Geospatial intelligence and jurisdictional risk monitoring.
          </p>
        </div>
        
        <div className="flex gap-4">
          <div className="px-4 py-2 rounded-xl bg-rose-500/10 border border-rose-500/20">
            <p className="text-[10px] uppercase tracking-widest text-rose-500 font-bold">Critical Sectors</p>
            <p className="text-xl font-bold text-white">{stats.HIGH}</p>
          </div>
          <div className="px-4 py-2 rounded-xl bg-amber-500/10 border border-amber-500/20">
            <p className="text-[10px] uppercase tracking-widest text-amber-500 font-bold">Warning Tiers</p>
            <p className="text-xl font-bold text-white">{stats.MEDIUM}</p>
          </div>
        </div>
      </header>

      <div className="flex-1 relative glass-panel rounded-3xl overflow-hidden border-white/5 shadow-2xl">
        {/* Real Leaflet Map */}
        <MapContainer 
          center={[20.5937, 78.9629]} 
          zoom={5} 
          style={{ height: "100%", width: "100%", background: "#060608" }}
          zoomControl={false}
        >
          <TileLayer
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> contributors'
          />
          <ZoomControl position="bottomright" />
          
          <GeoJSON 
            data={indiaDistricts as any} 
            style={styleFeature}
            onEachFeature={onEachFeature}
          />
        </MapContainer>

        {/* Tactical Overlay Legend */}
        <div className="absolute top-6 right-6 z-[1000] p-4 glass-panel border-white/10 rounded-2xl w-64 space-y-4">
          <h3 className="text-xs font-black uppercase tracking-widest text-slate-400 border-b border-white/5 pb-2">
            Mission Overlays
          </h3>
          <div className="space-y-2">
            <div className="flex items-center justify-between pb-2 border-b border-white/5">
              <span className="text-xs text-slate-500">Risk Threshold</span>
              <span className="text-xs font-mono text-brand-primary">70%</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 rounded-full bg-rose-500 shadow-[0_0_8px_rgba(225,29,72,0.6)]" />
              <span className="text-xs text-slate-300">Level 4: Critical Risk</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 rounded-full bg-amber-500" />
              <span className="text-xs text-slate-300">Level 3: Sustained Threat</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 rounded-full bg-emerald-500" />
              <span className="text-xs text-slate-300">Level 1-2: Minimal Impact</span>
            </div>
          </div>
          
          <button className="w-full py-2 bg-brand-primary hover:bg-brand-secondary text-white text-[10px] font-black uppercase tracking-widest rounded-lg transition-all">
            Calibrate Projection Engine
          </button>
        </div>

        {/* Global Control Bar */}
        <div className="absolute bottom-6 left-6 z-[1000] flex gap-2">
           <button className="px-4 py-2 rounded-xl glass-panel border-brand-primary/30 text-brand-primary text-xs font-bold hover:bg-brand-primary/10 transition-all flex items-center gap-2">
             <ShieldAlert size={14}/> 
             Sector Alerts
           </button>
           <button className="px-4 py-2 rounded-xl glass-panel border-white/10 text-slate-400 text-xs font-bold hover:bg-white/5 transition-all">
             Heatmap Toggle
           </button>
        </div>
      </div>
    </div>
  );
};

export default StrategicMap;
