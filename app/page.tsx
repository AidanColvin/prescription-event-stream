"use client";
import React, { useState, useEffect } from "react";
import { Navigation } from "./nav";

const masterData = [
  { id: "1", patient: "Mary Smith", generic: "Zolpidem Tartrate", brand: "Ambien", schedule: "CIV", indication: "Insomnia", sig: "Take 1 tablet at bedtime.", qty: 30, refills: 2, sideEffects: "Drowsiness, dizziness, complex sleep behaviors.", storage: "Room temperature.", prescriber: "Dr. Sarah Jenkins" },
  { id: "2", patient: "Patricia Johnson", generic: "Lisinopril", brand: "Zestril", schedule: "Non-controlled", indication: "Hypertension", sig: "Take 1 tablet daily.", qty: 90, refills: 3, sideEffects: "Dry cough, dizziness.", storage: "Room temperature.", prescriber: "Dr. Robert Chen" },
  { id: "3", patient: "James Smith", generic: "Amphetamine Salts", brand: "Adderall", schedule: "CII", indication: "ADHD", sig: "Take 1 capsule every morning.", qty: 30, refills: 0, sideEffects: "Insomnia, elevated heart rate.", storage: "Secure locked location.", prescriber: "Dr. Sarah Jenkins" }
];

export default function PatientView() {
  const [filtered, setFiltered] = useState(masterData);
  const [selected, setSelected] = useState<typeof masterData[0] | null>(null);

  useEffect(() => {
    const searchInput = document.getElementById("search-input") as HTMLInputElement;
    const handleInput = (e: Event) => {
      const q = (e.target as HTMLInputElement).value.toLowerCase().trim();
      const results = masterData.filter(ev => 
        ev.patient.toLowerCase().includes(q) || 
        ev.generic.toLowerCase().includes(q) || 
        ev.brand.toLowerCase().includes(q) || 
        ev.schedule.toLowerCase().includes(q) || 
        ev.indication.toLowerCase().includes(q)
      );
      setFiltered(results);
    };
    
    if (searchInput) {
      searchInput.addEventListener("input", handleInput);
    }
    return () => {
      if (searchInput) {
        searchInput.removeEventListener("input", handleInput);
      }
    };
  }, []);

  return (
    <main className="min-h-screen bg-[#f5f5f7] text-[#1d1d1f] p-4 sm:p-8" style={{ fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif' }}>
      <div className="max-w-3xl mx-auto space-y-6">
        <Navigation active="patient" />
        <h1 className="text-4xl font-semibold tracking-tight text-center mb-8">Medicine Cabinet</h1>
        
        <input 
          id="search-input"
          type="text" 
          placeholder="Spotlight search: medication, brand, patient..." 
          className="w-full border border-[#d2d2d7] rounded-[16px] px-6 py-4 text-lg shadow-sm focus:outline-none focus:border-[#0071e3] transition-all" 
          autoComplete="off" 
        />
        
        <div className="grid grid-cols-3 gap-4 sm:gap-6 mb-8">
          <div className="bg-white rounded-[16px] p-4 sm:p-6 border border-[#d2d2d7] shadow-sm"><div className="text-2xl sm:text-3xl font-semibold text-[#0071e3]">{filtered.length}</div><div className="text-[10px] sm:text-xs font-semibold text-[#86868b] uppercase tracking-wider mt-1">Active Prescriptions</div></div>
          <div className="bg-white rounded-[16px] p-4 sm:p-6 border border-[#d2d2d7] shadow-sm"><div className="text-2xl sm:text-3xl font-semibold">{filtered.filter(e => e.refills > 0).length}</div><div className="text-[10px] sm:text-xs font-semibold text-[#86868b] uppercase tracking-wider mt-1">Refills Available</div></div>
          <div className="bg-white rounded-[16px] p-4 sm:p-6 border border-[#d2d2d7] shadow-sm"><div className="text-2xl sm:text-3xl font-semibold">{filtered.length ? Math.round(filtered.reduce((a, c) => a + c.qty, 0) / filtered.length) : 0}</div><div className="text-[10px] sm:text-xs font-semibold text-[#86868b] uppercase tracking-wider mt-1">Average Qty</div></div>
        </div>

        <div className="space-y-4">
          {filtered.length === 0 ? (
            <div className="text-center py-16 bg-white rounded-[16px] border border-[#d2d2d7]"><p className="text-[#86868b] text-lg font-medium">No matching medications or patients found.</p></div>
          ) : (
            filtered.map(ev => (
              <div key={ev.id} onClick={() => setSelected(ev)} className="bg-white rounded-[16px] p-5 sm:p-6 border border-[#d2d2d7] shadow-sm hover:shadow-md cursor-pointer flex flex-col sm:flex-row justify-between sm:items-center gap-4 transition-all">
                <div>
                  <p className="text-xs font-bold text-[#86868b] uppercase tracking-wider mb-1">{ev.patient}</p>
                  <h3 className="text-xl font-bold">{ev.generic} <span className="font-normal text-[#86868b]">/ {ev.brand}</span></h3>
                  <p className="font-medium mt-2 text-sm text-[#1d1d1f]">{ev.sig}</p>
                </div>
                <div className="sm:text-right">
                  <span className={`inline-flex items-center px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider ${ev.refills > 0 ? 'bg-[#e8f5e9] text-[#2e7d32]' : 'bg-[#ffebee] text-[#c62828]'}`}>
                    {ev.refills > 0 ? `Refill in 7 Days` : '0 Refills Left'}
                  </span>
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
            <h2 className="text-2xl font-bold tracking-tight mb-1">{selected.generic}</h2>
            <p className="text-[#0071e3] font-medium mb-6">{selected.brand}</p>
            <div className="space-y-5">
              <div><h4 className="text-xs font-bold text-[#86868b] uppercase tracking-wider mb-1">What It Treats</h4><p className="text-sm font-medium text-[#1d1d1f]">{selected.indication}</p></div>
              <div><h4 className="text-xs font-bold text-[#86868b] uppercase tracking-wider mb-1">Side Effects</h4><p className="text-sm text-[#1d1d1f]">{selected.sideEffects}</p></div>
              <div><h4 className="text-xs font-bold text-[#86868b] uppercase tracking-wider mb-1">Safe Storage</h4><p className="text-sm text-[#1d1d1f]">{selected.storage}</p></div>
              <div className="pt-4 border-t border-[#d2d2d7]"><p className="text-xs text-[#86868b]">Prescribed by {selected.prescriber}</p></div>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
