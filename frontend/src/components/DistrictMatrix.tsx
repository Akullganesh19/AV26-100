import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Search, Download, AlertTriangle, CheckCircle2, ChevronRight } from 'lucide-react';
import { apiClient } from '../api/client';
import { Link } from 'react-router-dom';

const DistrictMatrix: React.FC = () => {
  const [search, setSearch] = useState('');

  const { data: districts, isLoading } = useQuery({
    queryKey: ['district-matrix'],
    queryFn: async () => {
      const response = await apiClient.get('/districts/');
      return response.data;
    }
  });

  const filteredDistricts = React.useMemo(() => {
    if (!districts) return [];
    return districts.filter((d: any) =>
      d.name.toLowerCase().includes(search.toLowerCase()) ||
      d.state.toLowerCase().includes(search.toLowerCase())
    ).sort((a: any, b: any) => b.risk_score - a.risk_score);
  }, [districts, search]);

  const handleExportCSV = () => {
    if (!filteredDistricts.length) return;
    const headers = ['District,State,Risk Score,Tier,Last Updated'];
    const rows = filteredDistricts.map((d: any) =>
      `${d.name},${d.state},${d.risk_score},${d.risk_tier},${d.last_updated}`
    );
    const csvContent = "data:text/csv;charset=utf-8," + [headers, ...rows].join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `episense_jurisdiction_export_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (isLoading) {
    return (
      <div className="glass-panel p-6 rounded-2xl h-[400px] flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-primary"></div>
      </div>
    );
  }

  return (
    <div className="glass-panel rounded-2xl overflow-hidden flex flex-col">
      {/* Toolbar */}
      <div className="p-4 border-b border-white/5 flex flex-col sm:flex-row gap-4 justify-between items-center bg-black/20">
        <div className="relative w-full sm:w-72">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          <input
            type="text"
            placeholder="Search districts or states..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-white/5 border border-white/10 rounded-xl py-2 pl-9 pr-4 text-sm text-white focus:outline-none focus:border-brand-primary/50 transition-colors"
          />
        </div>
        <button
          onClick={handleExportCSV}
          disabled={!filteredDistricts.length}
          className="flex items-center gap-2 px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl text-sm font-medium transition-all disabled:opacity-50"
        >
          <Download className="w-4 h-4" />
          Export Report
        </button>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm text-slate-300">
          <thead className="text-xs uppercase bg-black/40 text-slate-500 font-bold tracking-wider">
            <tr>
              <th className="px-6 py-4">Jurisdiction</th>
              <th className="px-6 py-4">State/Region</th>
              <th className="px-6 py-4">Risk Index</th>
              <th className="px-6 py-4">Status</th>
              <th className="px-6 py-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {filteredDistricts.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-6 py-12 text-center text-slate-500">
                  No jurisdictions match your parameters.
                </td>
              </tr>
            ) : (
              filteredDistricts.map((district: any) => (
                <tr key={district.id} className="hover:bg-white/[0.02] transition-colors group">
                  <td className="px-6 py-4 font-medium text-white">{district.name}</td>
                  <td className="px-6 py-4">{district.state}</td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-1.5 bg-white/10 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full ${
                            district.risk_tier === 'CRITICAL' ? 'bg-rose-500' :
                            district.risk_tier === 'HIGH' ? 'bg-amber-500' :
                            district.risk_tier === 'MEDIUM' ? 'bg-brand-primary' :
                            'bg-emerald-500'
                          }`}
                          style={{ width: `${Math.min(100, Math.max(0, district.risk_score))}%` }}
                        />
                      </div>
                      <span className="font-mono text-xs">{Number(district.risk_score).toFixed(1)}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    {district.risk_tier === 'CRITICAL' || district.risk_tier === 'HIGH' ? (
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-rose-500/10 text-rose-400 text-xs font-semibold border border-rose-500/20">
                        <AlertTriangle className="w-3.5 h-3.5" />
                        {district.risk_tier}
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-emerald-500/10 text-emerald-400 text-xs font-semibold border border-emerald-500/20">
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        {district.risk_tier}
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <Link
                      to={`/district/${district.id}`}
                      className="inline-flex items-center gap-1 text-slate-400 hover:text-brand-primary transition-colors text-xs font-semibold group-hover:translate-x-1 duration-200"
                    >
                      View Intelligence
                      <ChevronRight className="w-3.5 h-3.5" />
                    </Link>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default DistrictMatrix;
