import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  Droplet, 
  Brain, 
  FileText, 
  ChevronRight, 
  AlertTriangle, 
  CheckCircle2,
  Stethoscope,
  Info,
  Download
} from 'lucide-react';
import { apiClient } from '../api/client';
import { toast } from 'sonner';
import { useSearchParams } from 'react-router-dom';

type DiseaseType = 'heart' | 'diabetes' | 'parkinsons';

const DiagnosticsCenter: React.FC = () => {
  const [searchParams] = useSearchParams();
  const districtIdFromUrl = searchParams.get('district_id');
  
  const [activeTab, setActiveTab] = useState<DiseaseType>('heart');
  const [selectedDistrict, setSelectedDistrict] = useState<string>(districtIdFromUrl || '');
  const [loading, setLoading] = useState(false);
  const [prediction, setPrediction] = useState<any>(null);

  // Predictive Intelligence State
  const [prefetchBlobUrl, setPrefetchBlobUrl] = useState<string | null>(null);

  // 🛸 ORACLE: Predictive Intelligence
  // Signal: User gets a High Risk diagnosis result.
  // Prediction: They will inevitably need to download the tactical report (a slow generation step).
  // Action: Prefetch the PDF in the background immediately.
  useEffect(() => {
    let isActive = true;
    let localBlobUrl: string | null = null;

    const prefetchReport = async () => {
      if (!prediction || !prediction.risk) return;

      try {
        const response = await apiClient.post(
          `/clinical/report`,
          [prediction],
          { responseType: 'blob' }
        );

        if (isActive) {
          localBlobUrl = window.URL.createObjectURL(new Blob([response.data]));
          setPrefetchBlobUrl(localBlobUrl);
        }
      } catch (e) {
        console.error('Oracle: Prefetch failed. Will gracefully degrade to on-demand generation.', e);
      }
    };

    if (prediction?.risk) {
      prefetchReport();
    }

    return () => {
      isActive = false;
      if (localBlobUrl) {
        window.URL.revokeObjectURL(localBlobUrl);
      }
    };
  }, [prediction]);

  const handleDiagnose = async (formData: any) => {
    setLoading(true);
    setPrediction(null);
    setPrefetchBlobUrl(null); // Reset prefetch state on new run
    try {
      const response = await apiClient.post(`/clinical/${activeTab}`, formData);
      setPrediction(response.data);
      if (response.data.risk) {
        toast.error(`High risk detected for ${activeTab.toUpperCase()}`, {
          description: response.data.advice
        });
      } else {
        toast.success(`Low risk for ${activeTab.toUpperCase()}`, {
          description: response.data.advice
        });
      }
    } catch (error) {
      console.error('Diagnosis failed:', error);
      toast.error('Diagnosis failed', {
        description: 'Please ensure all clinical metrics are filled correctly.'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadReport = async () => {
    if (!prediction) return;

    // 🛸 Oracle: Use pre-computed blob if available, otherwise fallback to normal generation
    if (prefetchBlobUrl) {
      const link = document.createElement('a');
      link.href = prefetchBlobUrl;
      link.setAttribute('download', `EpiSense_Tactical_Report_${activeTab.toUpperCase()}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success('Report downloaded (Instant)');
      return;
    }

    try {
      const response = await apiClient.post(
        `/clinical/report`,
        [prediction], // Send current prediction in a list
        { responseType: 'blob' }
      );
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `EpiSense_Tactical_Report_${activeTab.toUpperCase()}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();

      // Cleanup the one-time url
      window.URL.revokeObjectURL(url);

      toast.success('Report generated successfully');
    } catch (error) {
      console.error('Report generation failed:', error);
      toast.error('Failed to generate PDF report');
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <header>
        <h1 className="text-3xl font-bold text-white tracking-tight flex items-center gap-3">
          <Stethoscope className="text-emerald-500 h-8 w-8" />
          Tactical Diagnostics Center
        </h1>
        <p className="text-slate-400 mt-1">
          Individual-level clinical screening powered by mission-trained ML models.
        </p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Navigation Sidebar */}
        <div className="lg:col-span-3 space-y-2">
          <button
            onClick={() => setActiveTab('heart')}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all border ${
              activeTab === 'heart' 
              ? 'bg-emerald-500/10 border-emerald-500/50 text-white shadow-lg shadow-emerald-500/10' 
              : 'bg-slate-900/50 border-slate-800 text-slate-400 hover:bg-slate-800/50 hover:text-white'
            }`}
          >
            <Activity className={activeTab === 'heart' ? 'text-emerald-500' : ''} />
            <span className="font-medium">Heart Disease</span>
          </button>
          <button
            onClick={() => setActiveTab('diabetes')}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all border ${
              activeTab === 'diabetes' 
              ? 'bg-emerald-500/10 border-emerald-500/50 text-white shadow-lg shadow-emerald-500/10' 
              : 'bg-slate-900/50 border-slate-800 text-slate-400 hover:bg-slate-800/50 hover:text-white'
            }`}
          >
            <Droplet className={activeTab === 'diabetes' ? 'text-emerald-500' : ''} />
            <span className="font-medium">Diabetes</span>
          </button>
          <button
            onClick={() => setActiveTab('parkinsons')}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all border ${
              activeTab === 'parkinsons' 
              ? 'bg-emerald-500/10 border-emerald-500/50 text-white shadow-lg shadow-emerald-500/10' 
              : 'bg-slate-900/50 border-slate-800 text-slate-400 hover:bg-slate-800/50 hover:text-white'
            }`}
          >
            <Brain className={activeTab === 'parkinsons' ? 'text-emerald-500' : ''} />
            <span className="font-medium">Parkinson's</span>
          </button>

          <div className="mt-8 p-4 rounded-xl bg-slate-900/50 border border-slate-800/50">
            <h3 className="text-sm font-semibold text-slate-300 flex items-center gap-2 mb-2">
              <Info className="h-4 w-4 text-emerald-500" />
              Operational Protocol
            </h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              These screenings are for tactical prioritization and awareness. This system does not replace certified medical consultation. Use for pre-deployment screening only.
            </p>
          </div>
        </div>

        {/* Content Area */}
        <div className="lg:col-span-9 space-y-6">
          <div className="bg-slate-900/40 backdrop-blur-md border border-slate-800 p-6 rounded-2xl shadow-2xl relative overflow-hidden group">
            <div className="absolute top-0 right-0 w-64 h-64 bg-emerald-500/5 blur-3xl -z-10 group-hover:bg-emerald-500/10 transition-all"></div>
            
            <h2 className="text-xl font-semibold text-white mb-6 flex items-center gap-2">
              {activeTab === 'heart' && <><Activity className="text-emerald-500" /> Heart Risk Assessment</>}
              {activeTab === 'diabetes' && <><Droplet className="text-emerald-500" /> Metabolic Screening</>}
              {activeTab === 'parkinsons' && <><Brain className="text-emerald-500" /> Neuro-vocal Analysis</>}
            </h2>

            {activeTab === 'heart' && <HeartForm onSubmit={handleDiagnose} loading={loading} />}
            {activeTab === 'diabetes' && <DiabetesForm onSubmit={handleDiagnose} loading={loading} />}
            {activeTab === 'parkinsons' && <ParkinsonsForm onSubmit={handleDiagnose} loading={loading} />}
          </div>

          {prediction && (
            <div className={`p-6 rounded-2xl border animate-in zoom-in-95 duration-300 ${
              prediction.risk 
              ? 'bg-red-500/10 border-red-500/30' 
              : 'bg-emerald-500/10 border-emerald-500/30'
            }`}>
              <div className="flex items-start gap-4">
                {prediction.risk ? (
                  <AlertTriangle className="h-8 w-8 text-red-500 mt-1" />
                ) : (
                  <CheckCircle2 className="h-8 w-8 text-emerald-500 mt-1" />
                )}
                <div className="flex-1">
                  <h3 className={`text-xl font-bold ${prediction.risk ? 'text-red-400' : 'text-emerald-400'}`}>
                    {prediction.risk ? 'PROBABLE RISK DETECTED' : 'CLEAR SCREENING'}
                  </h3>
                  <p className="text-slate-300 mt-1 text-lg">
                    {prediction.advice}
                  </p>
                  <div className="mt-4 flex gap-3">
                    <button 
                      onClick={handleDownloadReport}
                      className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg transition-colors text-sm font-medium"
                    >
                      <Download className="h-4 w-4" />
                      Tactical Report
                    </button>
                    <button className="flex items-center gap-2 px-4 py-2 border border-slate-700 hover:bg-slate-800 text-slate-300 rounded-lg transition-colors text-sm">
                      <FileText className="h-4 w-4" />
                      View Metrics
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Form Components
const HeartForm = ({ onSubmit, loading }: { onSubmit: (data: any) => void, loading: boolean }) => {
  const [data, setData] = useState({
    age: 50, sex: 1, cp: 0, trestbps: 120, chol: 200, fbs: 0, 
    restecg: 0, thalach: 150, exang: 0, oldpeak: 0.0, slope: 1, ca: 0, thal: 2
  });

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <Input label="Age" type="number" value={data.age} onChange={(v) => setData({...data, age: parseInt(v)})} />
      <Select label="Sex" value={data.sex} options={[{v: 1, l: 'Male'}, {v: 0, l: 'Female'}]} onChange={(v) => setData({...data, sex: parseInt(v)})} />
      <Select label="Chest Pain (0-3)" value={data.cp} options={[0,1,2,3].map(i => ({v:i, l:`Type ${i}`}))} onChange={(v) => setData({...data, cp: parseInt(v)})} />
      <Input label="Resting BP" type="number" value={data.trestbps} onChange={(v) => setData({...data, trestbps: parseInt(v)})} />
      <Input label="Cholesterol" type="number" value={data.chol} onChange={(v) => setData({...data, chol: parseInt(v)})} />
      <Select label="Fasting Sugar > 120" value={data.fbs} options={[{v: 1, l: 'True'}, {v: 0, l: 'False'}]} onChange={(v) => setData({...data, fbs: parseInt(v)})} />
      <Input label="Max HR" type="number" value={data.thalach} onChange={(v) => setData({...data, thalach: parseInt(v)})} />
      <Input label="ST Depression" type="number" step="0.1" value={data.oldpeak} onChange={(v) => setData({...data, oldpeak: parseFloat(v)})} />
      <div className="col-span-full mt-4">
        <button 
          onClick={() => onSubmit(data)}
          disabled={loading}
          className="w-full py-3 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl shadow-lg shadow-emerald-600/20 transition-all flex items-center justify-center gap-2"
        >
          {loading ? 'Analyzing...' : <><Activity size={20}/> RUN MISSION DIAGNOSIS</>}
        </button>
      </div>
    </div>
  );
};

const DiabetesForm = ({ onSubmit, loading }: { onSubmit: (data: any) => void, loading: boolean }) => {
  const [data, setData] = useState({
    pregnancies: 0, glucose: 100, blood_pressure: 70, skin_thickness: 20, 
    insulin: 80, bmi: 25.0, dpf: 0.5, age: 30
  });

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <Input label="Pregnancies" type="number" value={data.pregnancies} onChange={(v) => setData({...data, pregnancies: parseInt(v)})} />
      <Input label="Glucose" type="number" value={data.glucose} onChange={(v) => setData({...data, glucose: parseInt(v)})} />
      <Input label="Blood Pressure" type="number" value={data.blood_pressure} onChange={(v) => setData({...data, blood_pressure: parseInt(v)})} />
      <Input label="Insulin" type="number" value={data.insulin} onChange={(v) => setData({...data, insulin: parseInt(v)})} />
      <Input label="BMI" type="number" step="0.1" value={data.bmi} onChange={(v) => setData({...data, bmi: parseFloat(v)})} />
      <Input label="Age" type="number" value={data.age} onChange={(v) => setData({...data, age: parseInt(v)})} />
      <div className="col-span-full mt-4">
        <button 
          onClick={() => onSubmit(data)}
          disabled={loading}
          className="w-full py-3 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl shadow-lg shadow-emerald-600/20 transition-all flex items-center justify-center gap-2"
        >
          {loading ? 'Analyzing...' : <><Droplet size={20}/> ANALYZE METABOLIC LOAD</>}
        </button>
      </div>
    </div>
  );
};

const ParkinsonsForm = ({ onSubmit, loading }: { onSubmit: (data: any) => void, loading: boolean }) => {
  const [vocalMetrics, setVocalMetrics] = useState<number[]>(new Array(22).fill(0));

  const handleRandomize = () => {
    setVocalMetrics(new Array(22).fill(0).map(() => Math.random() * 0.1));
  };

  return (
    <div className="space-y-6">
      <div className="p-4 rounded-xl bg-amber-500/5 border border-amber-500/20">
        <p className="text-amber-200 text-sm flex items-center gap-2">
          <Info size={16}/> Parkinson's diagnosis requires 22 specific MDVP vocal metrics.
        </p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <button 
          onClick={handleRandomize}
          className="px-4 py-2 border border-slate-700 text-slate-300 rounded-lg text-sm hover:bg-slate-800 transition-colors"
        >
          Load Tactical Sample Data
        </button>
      </div>

      <div className="bg-slate-800/30 p-4 rounded-xl border border-slate-700/50">
        <div className="flex flex-wrap gap-2">
          {vocalMetrics.map((v, i) => (
            <div key={i} className="flex flex-col gap-1 w-20">
              <span className="text-[10px] text-slate-500 font-mono">#{i+1}</span>
              <input 
                type="number" 
                step="0.0001"
                className="bg-slate-900 border border-slate-700 rounded px-1 py-0.5 text-xs text-white"
                value={v}
                onChange={(e) => {
                  const newM = [...vocalMetrics];
                  newM[i] = parseFloat(e.target.value);
                  setVocalMetrics(newM);
                }}
              />
            </div>
          ))}
        </div>
      </div>

      <button 
        onClick={() => onSubmit({ vocal_metrics: vocalMetrics })}
        disabled={loading}
        className="w-full py-3 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl shadow-lg shadow-emerald-600/20 transition-all flex items-center justify-center gap-2"
      >
        {loading ? 'Analyzing...' : <><Brain size={20}/> ANALYZE NEURO-SIGNALS</>}
      </button>
    </div>
  );
};

// UI Helpers
const Input = ({ label, type, value, onChange, step }: any) => (
  <div className="flex flex-col gap-1.5">
    <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{label}</label>
    <input 
      type={type} 
      step={step}
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="bg-slate-900/80 border border-slate-800 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500/50 transition-all"
    />
  </div>
);

const Select = ({ label, value, options, onChange }: any) => (
  <div className="flex flex-col gap-1.5">
    <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{label}</label>
    <select 
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="bg-slate-900/80 border border-slate-800 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-emerald-500/50 transition-all"
    >
      {options.map((o: any) => (
        <option key={typeof o === 'object' ? o.v : o} value={typeof o === 'object' ? o.v : o}>
          {typeof o === 'object' ? o.l : o}
        </option>
      ))}
    </select>
  </div>
);

export default DiagnosticsCenter;
