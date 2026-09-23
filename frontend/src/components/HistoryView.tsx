import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Clock, CheckCircle2, AlertTriangle, FileText } from 'lucide-react';
import { toast } from 'sonner';

interface HistoryEntry {
  id: string;
  endpoint: string;
  risk_score: number;
  status: string;
  timestamp: string;
}

const HistoryView: React.FC = () => {
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await axios.get(`${import.meta.env.VITE_API_URL}/clinical/history`, {
           headers: {
             Authorization: `Bearer ${localStorage.getItem('token')}`
           }
        });
        setHistory(response.data);
      } catch (error) {
        toast.error('Failed to load screening history');
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, []);

  if (loading) {
    return <div className="text-slate-400 p-8 text-center">Loading history...</div>;
  }

  if (history.length === 0) {
    return (
      <div className="text-slate-400 p-8 text-center bg-slate-900/30 rounded-xl border border-slate-800">
        <Clock className="w-12 h-12 mx-auto mb-3 opacity-20" />
        <p>No previous screenings found.</p>
        <p className="text-sm mt-1">Your tactical diagnostics history will appear here.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {history.map((entry) => (
        <div key={entry.id} className="p-4 rounded-xl bg-slate-900/50 border border-slate-800 flex items-center justify-between group hover:border-slate-700 transition-colors">
          <div className="flex items-center gap-4">
            <div className={`p-2 rounded-lg ${entry.risk_score > 0.7 ? 'bg-red-500/10 text-red-500' : 'bg-emerald-500/10 text-emerald-500'}`}>
              {entry.risk_score > 0.7 ? <AlertTriangle size={20} /> : <CheckCircle2 size={20} />}
            </div>
            <div>
              <h4 className="font-semibold text-slate-200 capitalize">
                {entry.endpoint.replace('clinical/', '')} Screening
              </h4>
              <p className="text-xs text-slate-500 flex items-center gap-1 mt-1">
                <Clock size={12} />
                {new Date(entry.timestamp).toLocaleString()}
              </p>
            </div>
          </div>

          <div className="text-right">
            <div className="text-lg font-bold text-white">
              {(entry.risk_score * 100).toFixed(1)}% <span className="text-xs text-slate-500 font-normal">RISK</span>
            </div>
            <div className="text-[10px] uppercase tracking-wider text-slate-500 mt-1">
              {entry.status}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default HistoryView;
