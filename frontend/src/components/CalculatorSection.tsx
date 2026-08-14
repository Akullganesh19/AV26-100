import { useState, useMemo } from 'react';
import { Check } from 'lucide-react';
import { toast } from 'sonner';

// STYLES FOR THE SLIDER (MANUAL SHADCN-LIKE SLIDER)
const Slider = ({ value, min, max, step, onChange }: any) => {
  return (
    <div className="relative w-full h-6 flex items-center group">
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        aria-label="Number of pages"
        onChange={(e) => onChange(parseInt(e.target.value))}
        className="w-full h-1.5 bg-[#1E1E1E] rounded-lg appearance-none cursor-pointer accent-[#FF5656]"
      />
    </div>
  );
};

export const CalculatorSection = () => {
  const [serviceType, setServiceType] = useState<'design' | 'development' | 'both'>('both');
  const [pages, setPages] = useState(5);
  const [needContent, setNeedContent] = useState(false);
  const [needSEO, setNeedSEO] = useState(false);
  const [timeline, setTimeline] = useState<'regular' | 'fast' | 'rush'>('regular');

  const pricing = useMemo(() => {
    // Base prices by service
    const config = {
      design: { base: 399, perPage: 100 },
      development: { base: 199, perPage: 100 },
      both: { base: 499, perPage: 200 }
    };

    const { base, perPage } = config[serviceType];
    
    // Calculate Webfluin Price
    let total = Math.max(base, base + (pages - 1) * perPage);
    if (needContent) total += pages * 50;
    if (needSEO) total += pages * 50;
    if (timeline === 'rush') total += pages * 100;
    if (timeline === 'fast') total += pages * 25;

    // Calculate Agency Cost
    const agencyPerPage = (serviceType === 'both' ? 1000 : 400);
    const agencyTotal = 8000 + (pages - 1) * agencyPerPage;

    // Calculate Freelancer Cost
    const freelancerPerPage = (serviceType === 'both' ? 500 : 200);
    const freelancerTotal = 3000 + (pages - 1) * freelancerPerPage;

    return {
      webfluin: total,
      agency: agencyTotal,
      freelancer: freelancerTotal
    };
  }, [serviceType, pages, needContent, needSEO, timeline]);

  return (
    <section id="calculator-section" className="bg-[#050505] py-16 md:py-28 px-4 md:px-16 text-white font-sans">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-16">
          <p className="text-xs font-mono uppercase tracking-[0.3em] text-[#666] mb-4">
            Try project estimation calculator
          </p>
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-normal leading-tight">
            Get premium website within your budget
          </h2>
        </div>

        {/* Calculator Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 rounded-2xl overflow-hidden border border-[#1E1E1E]">
          
          {/* LEFT COLUMN - FORM */}
          <div className="bg-[#0D0D0D] p-8 lg:p-12 flex flex-col gap-10 divide-y divide-[#1E1E1E]">
            
            {/* Service Type */}
            <div className="space-y-6">
              <h3 className="text-lg font-medium opacity-80">What kind of service do you need?</h3>
              <div className="flex flex-wrap gap-4" role="radiogroup" aria-label="Service Type">
                {[
                  { id: 'design', label: 'Only Design' },
                  { id: 'development', label: 'Only Development' },
                  { id: 'both', label: 'Design + Development' }
                ].map((opt) => (
                  <button
                    key={opt.id}
                    role="radio"
                    aria-checked={serviceType === opt.id}
                    onClick={() => setServiceType(opt.id as any)}
                    className="flex items-center gap-3 group cursor-pointer focus-visible:ring-2 focus-visible:ring-[#FF5656] focus-visible:outline-none rounded-md"
                  >
                    <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center transition-colors ${serviceType === opt.id ? 'border-[#FF5656]' : 'border-[#333]'}`}>
                      {serviceType === opt.id && <div className="w-2 h-2 rounded-full bg-[#FF5656]" />}
                    </div>
                    <span className={`text-sm transition-colors ${serviceType === opt.id ? 'text-white' : 'text-[#666]'}`}>
                      {opt.label}
                    </span>
                  </button>
                ))}
              </div>
            </div>

            {/* Pages Slider */}
            <div className="pt-10 space-y-6">
              <div className="flex justify-between items-end">
                <h3 className="text-lg font-medium opacity-80">Number of Pages</h3>
                <span className="text-2xl font-bold text-[#FF5656]">{pages}</span>
              </div>
              <div className="space-y-2">
                <Slider value={pages} min={1} max={30} step={1} onChange={setPages} />
                <div className="flex justify-between text-[10px] uppercase font-mono text-[#444] tracking-widest pt-1">
                  <span>1 Page</span>
                  <span>30 Pages</span>
                </div>
              </div>
            </div>

            {/* Add-ons */}
            <div className="pt-10 space-y-6">
              <h3 className="text-lg font-medium opacity-80">Add-ons</h3>
              <div className="grid gap-4">
                {[
                  { id: 'content', label: 'I will need help with content', price: '+$50/page', state: needContent, set: setNeedContent },
                  { id: 'seo', label: 'I want to optimize my website for SEO', price: '+$50/page', state: needSEO, set: setNeedSEO }
                ].map((addon) => (
                  <label key={addon.id} className="flex items-center justify-between group cursor-pointer">
                    <div className="flex items-center gap-3">
                      <input 
                        type="checkbox" 
                        className="sr-only peer"
                        checked={addon.state} 
                        onChange={() => addon.set(!addon.state)} 
                      />
                      <div className={`w-5 h-5 border-2 rounded flex items-center justify-center transition-all peer-focus-visible:ring-2 peer-focus-visible:ring-[#FF5656] peer-focus-visible:outline-none ${addon.state ? 'bg-[#FF5656] border-[#FF5656]' : 'border-[#333]'}`}>
                        {addon.state && <Check size={14} strokeWidth={4} className="text-white" />}
                      </div>
                      <span className={`text-sm transition-colors ${addon.state ? 'text-white' : 'text-[#666]'}`}>{addon.label}</span>
                    </div>
                    <span className="text-xs font-bold text-[#FF5656]">{addon.price}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Timeline */}
            <div className="pt-10 space-y-6">
              <h3 className="text-lg font-medium opacity-80">How fast do you need this?</h3>
              <div className="grid gap-4" role="radiogroup" aria-label="Timeline">
                {[
                  { id: 'rush', label: 'Within 7 Days', price: '+$100/page' },
                  { id: 'fast', label: 'Within 14 Days', price: '+$25/page' },
                  { id: 'regular', label: 'Regular Speed', price: 'No extra cost' }
                ].map((opt) => (
                  <button
                    key={opt.id}
                    role="radio"
                    aria-checked={timeline === opt.id}
                    onClick={() => setTimeline(opt.id as any)}
                    className="flex items-center justify-between group cursor-pointer w-full text-left focus-visible:ring-2 focus-visible:ring-[#FF5656] focus-visible:outline-none rounded-md"
                  >
                    <div className="flex items-center gap-3">
                      <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center transition-colors ${timeline === opt.id ? 'border-[#FF5656]' : 'border-[#333]'}`}>
                        {timeline === opt.id && <div className="w-2 h-2 rounded-full bg-[#FF5656]" />}
                      </div>
                      <span className={`text-sm transition-colors ${timeline === opt.id ? 'text-white' : 'text-[#666]'}`}>
                        {opt.label}
                      </span>
                    </div>
                    <span className={`text-xs font-bold ${opt.id === 'regular' ? 'text-[#444]' : 'text-[#FF5656]'}`}>{opt.price}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* RIGHT COLUMN - RESULTS */}
          <div className="bg-[#050505] p-8 lg:p-12 border-l lg:border-l-0 lg:border-t-0 border-[#1E1E1E] flex flex-col justify-between min-h-[717px]">
            <div className="space-y-2 mb-10">
              <h3 className="text-2xl font-bold">Estimated Cost</h3>
              <p className="text-sm text-[#666] leading-relaxed">
                Prices are estimated based on your requirements. The final cost may vary after detailed discussion.
              </p>
            </div>

            <div className="flex flex-col gap-4">
              {/* Agency Card */}
              <div className="bg-[#111] rounded-2xl p-6 border border-white/5 space-y-2">
                <p className="text-[10px] uppercase tracking-widest text-[#666] font-medium">Typical Agency charges minimum</p>
                <h4 className="text-4xl font-bold">${pricing.agency.toLocaleString()}</h4>
                <p className="text-[10px] text-[#FF5656] font-medium">+ Too much extra time & additional cost</p>
              </div>

              {/* Freelancer Card */}
              <div className="bg-[#111] rounded-2xl p-6 border border-white/5 space-y-2">
                <p className="text-[10px] uppercase tracking-widest text-[#666] font-medium">Regular Freelancer charges minimum</p>
                <h4 className="text-4xl font-bold">${pricing.freelancer.toLocaleString()}</h4>
                <p className="text-[10px] text-[#FF5656] font-medium">+ Too much headache & back-and-forth</p>
              </div>

              {/* Webfluin Card */}
              <div className="bg-gradient-to-r from-[#FF5656] to-[#FF8C56] text-white rounded-2xl p-8 space-y-2 shadow-[0_0_40px_rgba(255,86,86,0.2)]">
                <p className="text-[10px] uppercase tracking-widest opacity-80 font-bold">With Webfluin Studio</p>
                <h4 className="text-5xl font-extrabold tracking-tighter">${pricing.webfluin.toLocaleString()}</h4>
                <p className="text-[10px] font-bold">Save your money, time & headache</p>
              </div>
            </div>

            <button 
              onClick={() => toast.success("Consultation Request Sent. Transmission Received.")}
              className="w-full mt-10 py-4 bg-white text-black font-bold rounded-xl hover:scale-[1.02] active:scale-[0.98] transition-all"
            >
              Book Your Free Consultation
            </button>
          </div>
        </div>
      </div>
    </section>
  );
};
