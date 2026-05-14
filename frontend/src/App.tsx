import React from 'react';
import { CalculatorSection } from './components/CalculatorSection';
import { Toaster } from 'sonner';

export default function App() {
  return (
    <main className="bg-[#050505] min-h-screen text-white font-sans selection:bg-[#FF5656] selection:text-white overflow-hidden">
      <Toaster position="top-center" richColors />
      
      {/* NAVIGATION PLACEHOLDER */}
      <nav className="max-w-7xl mx-auto px-8 py-10 flex justify-between items-center opacity-80">
        <span className="text-xl font-bold tracking-tighter">WEBFLUIN <span className="text-[#FF5656]">STUDIO</span></span>
        <div className="flex gap-10 text-xs uppercase tracking-widest font-medium">
          <a href="#" className="hover:text-[#FF5656] transition-colors">Process</a>
          <a href="#" className="hover:text-[#FF5656] transition-colors">Portfolio</a>
          <a href="#" className="hover:text-[#FF5656] transition-colors">Contact</a>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-8 py-20 text-center">
         <h1 className="text-6xl md:text-8xl font-black uppercase tracking-tighter leading-[0.9] mb-8">
           We Build <br/> <span className="text-[#FF5656]">Bold</span> Brands.
         </h1>
         <p className="text-[#666] max-w-xl mx-auto text-sm md:text-base leading-relaxed">
           Elite design and development for startups that aren't afraid to stand out. 
           Transparent pricing. High-speed delivery. Zero headache.
         </p>
      </div>

      <CalculatorSection />

      <footer className="py-20 text-center border-t border-white/5 opacity-40">
        <p className="text-[10px] uppercase tracking-widest font-mono">&copy; 2025 Webfluin Studio -- Tactical Deployment</p>
      </footer>
    </main>
  );
}
