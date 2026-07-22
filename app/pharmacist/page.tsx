"use client";
import React, { useState, useEffect } from "react";
import { Navigation } from "../nav";

const masterQueue = [
  { id: "1", patient: "James Smith", generic: "Zolpidem Tartrate", brand: "Ambien", schedule: "Schedule IV", qty: 90, refills: 4, prescriber: "Dr. Jenkins", dea: "BJ8839201", indication: "Insomnia", warnings: ["Pediatric Contraindication: Not approved for children."] },
  { id: "2", patient: "Mary Smith", generic: "Amphetamine Salts", brand: "Adderall", schedule: "Schedule II", qty: 30, refills: 0, prescriber: "Dr. Chen", dea: "None", indication: "ADHD", warnings: ["Invalid DEA: Prescriber DEA required for controlled substances."] },
  { id: "3", patient: "Patricia Johnson", generic: "Lisinopril", brand: "Zestril", schedule: "Non-controlled", qty: 30, refills: 3, prescriber: "Dr. Jenkins", dea: "BJ8839201", indication: "Hypertension", warnings: [] }
];

export default function PharmacistView() {
  const [filtered, setFiltered] = useState(masterQueue);
  const [selected, setSelected] = useState<any>(null);

  useEffect(() => {
    const searchInput = document.getElementById("search-input") as HTMLInputElement;
    const handleInput = (e: Event) => {
      const q = (e.target as HTMLInputElement).value.toLowerCase().trim();
      const results = masterQueue.filter(ev => 
        ev.patient.toLowerCase().includes(q) || 
        ev.generic.toLowerCase().includes(q) || 
        ev.brand.toLowerCase().includes(q) || 
        ev.schedule.toLowerCase().includes(q) ||
        ev.indication.toLowerCase().includes(q)
      );
      setFiltered(results);
    };

    if (searchInput) searchInput.addEventListener("input", handleInput);
    return () => { if (searchInput) searchInput.removeEventListener("input", handleInput); };
  }, []);

  const totalFlagged = filtered.filter(e => e.warnings.length > 0).length;

  return (
    <main className="min-h-screen bg-[#f5f5f7] text-[#1d1d1f] p-4 sm:p-8" style={{ fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif' }}>
      <div className="max-w-3xl mx-auto space-y-6">
        <Navigation active="pharmacist" />
        <h1 className="text-4xl font-semibold tracking-tight text-center mb-8">Second Look Triage</h1>
        
        <input 
          id="search-input"
          type="text" 
          placeholder="Spotlight search: patient, medication, or schedule..." 
          className="w-full border border-[#d2d2d7] rounded-[16px] px-6 py-4 text-lg shadow-sm focus:outline-none focus:border-[#0071e3] transition-all" 
          autoComplete="off" 
        />

        <div className="grid grid-cols-2 gap-4 sm:gap-6 mb-8">
          <div className="bg-white rounded-[16px] p-4 sm:p-6 border border-[#d2d2d7] shadow-sm"><div className="text-2xl sm:text-3xl font-semibold">{filtered.length}</div><div className="text-[10px] sm:text-xs font-bold text-[#86868b] uppercase tracking-wider mt-1">Total Queue</div></div>
          <div className="bg-white rounded-[16px] p-4 sm:p-6 border border-[#c62828] shadow-sm"><div className="text-2xl sm:text-3xl font-semibold text-[#c62828]">{totalFlagged}</div><div className="text-[10px] sm:text-xs font-bold text-[#86868b] uppercase tracking-wider mt-1">Intervention Required</div></div>
        </div>

        <div className="space-y-4">
          {filtered.length === 0 ? (
            <div className="text-center py-16 bg-white rounded-[16px] border border-[#d2d2d7]"><p className="text-[#86868b] text-lg font-medium">No matching records found.</p></div>
          ) : (
            filtered.map(ev => (
              <div key={ev.id} onClick={() => setSelected(ev)} className={`bg-white rounded-[16px] p-5 sm:p-6 border shadow-sm hover:shadow-md cursor-pointer flex flex-col sm:flex-row justify-between sm:items-center gap-4 transition-all ${ev.warnings.length > 0 ? 'border-[#c62828]' : 'border-[#d2d2d7]'}`}>
                <div>
                  <p className="text-xs font-bold text-[#86868b] uppercase tracking-wider mb-1">{ev.patient}</p>
                  <h3 className="text-xl font-bold">{ev.generic} <span className="font-normal text-[#86868b]">/ {ev.brand}</span></h3>
                </div>
                <div className="flex flex-wrap gap-2">
                  <span className={`px-3 py-1.5 rounded-full text-[10px] sm:text-xs font-bold uppercase tracking-wider ${ev.schedule.includes('II') ? 'bg-[#ffebee] text-[#c62828]' : 'bg-[#f1f1f2] text-[#48484a]'}`}>{ev.schedule}</span>
                  {ev.warnings.length > 0 && <span className="px-3 py-1.5 rounded-full text-[10px] sm:text-xs font-bold uppercase tracking-wider bg-[#c62828] text-white">Review Required</span>}
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {selected && (
        <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-4 bg-black/40 backdrop-blur-md transition-opacity" onClick={() => setSelected(null)}>
          <div className="bg-white rounded-[24px] p-8 max-w-md w-full shadow-2xl relative mb-safe" onClick={e => e.stopPropagation()}>
            <button onClick={() => setSelected(null)} className="absolute top-6 right-6 text-[#86868b] hover:text-[#1d1d1f] text-xl">&times;</button>
            <h2 className="text-2xl font-bold tracking-tight mb-6">{selected.warnings.length > 0 ? 'Do Not Fill.' : 'Clear to Dispense.'}</h2>
            {selected.warnings.length > 0 ? (
              <div className="space-y-3 mb-6">
                {selected.warnings.map((w: string, i: number) => <p key={i} className="text-sm font-medium text-[#c62828] leading-relaxed">{w}</p>)}
              </div>
            ) : (
              <p className="text-sm font-medium text-[#2e7d32] mb-6">No automated safety flags detected.</p>
            )}
            <div className="pt-4 border-t border-[#d2d2d7]">
              <p className="text-xs font-medium text-[#86868b]">Prescriber: {selected.prescriber} <br/> DEA: <span className="font-mono">{selected.dea}</span></p>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
