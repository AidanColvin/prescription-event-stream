"use client";
import React, { useState, useEffect } from "react";
import { Navigation } from "../nav";

const masterAlerts = [
  { id: "1", patient: "James Smith", generic: "Zolpidem Tartrate", brand: "Ambien", schedule: "CIV", indication: "Insomnia", adherence: 95, interactions: "Severe: Avoid concurrent CNS depressants.", regimen: "10mg tablet at bedtime" },
  { id: "2", patient: "Mary Smith", generic: "Lisinopril", brand: "Zestril", schedule: "Non-controlled", indication: "Hypertension", adherence: 65, interactions: "None", regimen: "20mg tablet daily" }
];

export default function MDView() {
  const [filtered, setFiltered] = useState(masterAlerts);
  const [selected, setSelected] = useState<typeof masterAlerts[0] | null>(null);

  useEffect(() => {
    const searchInput = document.getElementById("search-input") as HTMLInputElement;
    const handleInput = (e: Event) => {
      const q = (e.target as HTMLInputElement).value.toLowerCase().trim();
      const results = masterAlerts.filter(ev => 
        ev.patient.toLowerCase().includes(q) || 
        ev.generic.toLowerCase().includes(q) || 
        ev.brand.toLowerCase().includes(q) || 
        ev.indication.toLowerCase().includes(q) ||
        ev.schedule.toLowerCase().includes(q)
      );
      setFiltered(results);
    };

    if (searchInput) searchInput.addEventListener("input", handleInput);
    return () => { if (searchInput) searchInput.removeEventListener("input", handleInput); };
  }, []);

  return (
    <main className="min-h-screen bg-[#f5f5f7] text-[#1d1d1f] p-4 sm:p-8" style={{ fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif' }}>
      <div className="max-w-3xl mx-auto space-y-6">
        <Navigation active="md" />
        <h1 className="text-4xl font-semibold tracking-tight text-center mb-8">Clinical Alerts</h1>
        
        <input 
          id="search-input"
          type="text" 
          placeholder="Spotlight search: patient, medication, or condition..." 
          className="w-full border border-[#d2d2d7] rounded-[16px] px-6 py-4 text-lg shadow-sm focus:outline-none focus:border-[#0071e3] transition-all" 
          autoComplete="off" 
        />

        <div className="grid grid-cols-2 gap-4 sm:gap-6 mb-8">
          <div className="bg-white rounded-[16px] p-4 sm:p-6 border border-[#d2d2d7] shadow-sm"><div className="text-2xl sm:text-3xl font-semibold">{filtered.length}</div><div className="text-[10px] sm:text-xs font-bold text-[#86868b] uppercase tracking-wider mt-1">Patients in View</div></div>
          <div className="bg-white rounded-[16px] p-4 sm:p-6 border border-[#c62828] shadow-sm"><div className="text-2xl sm:text-3xl font-semibold text-[#c62828]">{filtered.filter(e => e.interactions !== "None" || e.adherence < 80).length}</div><div className="text-[10px] sm:text-xs font-bold text-[#86868b] uppercase tracking-wider mt-1">Critical Warnings</div></div>
        </div>

        <div className="space-y-4">
          {filtered.length === 0 ? (
            <div className="text-center py-16 bg-white rounded-[16px] border border-[#d2d2d7]"><p className="text-[#86868b] text-lg font-medium">No matching records found.</p></div>
          ) : (
            filtered.map(ev => (
              <div key={ev.id} onClick={() => setSelected(ev)} className="bg-white rounded-[16px] p-5 sm:p-6 border border-[#d2d2d7] shadow-sm hover:shadow-md cursor-pointer flex flex-col sm:flex-row justify-between sm:items-start gap-4 transition-all">
                <div>
                  <h3 className="text-xl font-bold tracking-tight mb-1">{ev.patient}</h3>
                  <p className="text-sm font-medium text-[#86868b] mb-3">{ev.generic} <span className="font-normal">/ {ev.brand}</span></p>
                  {ev.interactions !== "None" && <p className="text-xs font-bold text-[#c62828] uppercase tracking-wider">⚠️ Drug Interaction</p>}
                </div>
                <div className="sm:text-right">
                  <span className={`text-2xl sm:text-3xl font-bold tracking-tight ${ev.adherence < 80 ? 'text-[#c62828]' : 'text-[#2e7d32]'}`}>{ev.adherence}%</span>
                  <p className="text-[10px] sm:text-xs font-bold text-[#86868b] uppercase tracking-wider mt-1">Adherence</p>
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
            <h2 className="text-2xl font-bold tracking-tight mb-4">{selected.patient}</h2>
            <div className="space-y-5">
              <div className="p-4 bg-[#f5f5f7] rounded-[12px] border border-[#d2d2d7]">
                <h4 className="text-sm font-bold text-[#1d1d1f]">{selected.generic} / {selected.brand}</h4>
                <p className="text-sm font-medium text-[#86868b] mt-1">{selected.regimen}</p>
              </div>
              {selected.interactions !== "None" && (
                <div><h4 className="text-xs font-bold text-[#c62828] uppercase tracking-wider mb-1">Interaction Alert</h4><p className="text-sm font-medium text-[#1d1d1f]">{selected.interactions}</p></div>
              )}
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
