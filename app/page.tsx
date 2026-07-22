"use client";

import React, { useState, useMemo } from "react";

const masterEvents = [
  { id: "1", patient: "Mary Smith", generic: "Zolpidem Tartrate", brand: "Ambien", schedule: "Schedule IV", indication: "Insomnia", offLabel: "Restless leg syndrome", sig: "Take 1 tablet at bedtime.", qty: 30, refills: 2, sideEffects: "Drowsiness, dizziness, complex sleep behaviors.", storage: "Store at room temperature away from light and moisture.", prescriber: "Dr. Sarah Jenkins, MD" },
  { id: "2", patient: "Patricia Johnson", generic: "Lisinopril", brand: "Zestril", schedule: "Non-controlled", indication: "Hypertension", offLabel: "Heart failure management", sig: "Take 1 tablet daily.", qty: 90, refills: 3, sideEffects: "Persistent dry cough, dizziness, elevated potassium.", storage: "Store at room temperature.", prescriber: "Dr. Robert Chen, DO" },
  { id: "3", patient: "James Smith", generic: "Amphetamine Salts", brand: "Adderall", schedule: "Schedule II", indication: "ADHD", offLabel: "Narcolepsy", sig: "Take 1 capsule daily in the morning.", qty: 30, refills: 0, sideEffects: "Insomnia, decreased appetite, elevated heart rate.", storage: "Store in a secure, locked location.", prescriber: "Dr. Sarah Jenkins, MD" }
];

export default function PatientView() {
  const [search, setSearch] = useState("");
  const [selectedEvent, setSelectedEvent] = useState<typeof masterEvents[0] | null>(null);

  const filtered = useMemo(() => {
    const q = search.toLowerCase().trim();
    return masterEvents.filter(ev => 
      ev.patient.toLowerCase().includes(q) || 
      ev.generic.toLowerCase().includes(q) || 
      ev.brand.toLowerCase().includes(q) || 
      ev.schedule.toLowerCase().includes(q) || 
      ev.indication.toLowerCase().includes(q)
    );
  }, [search]);

  return (
    <main className="min-h-screen bg-[#f5f5f7] text-[#1d1d1f] p-8" style={{ fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", sans-serif' }}>
      <div className="max-w-3xl mx-auto space-y-8">
        <header className="text-center space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-[#e8f5e9] text-[#2e7d32] rounded-full text-xs font-medium tracking-wide uppercase">
            <span className="w-2 h-2 rounded-full bg-[#34c759] animate-pulse" /> Live Stream
          </div>
          <h1 className="text-4xl font-semibold tracking-tight">Medicine Cabinet</h1>
        </header>

        <input
          type="text"
          placeholder="Spotlight search: medication, brand, patient, or condition..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full border border-[#d2d2d7] rounded-full px-6 py-4 text-lg shadow-sm focus:outline-none focus:border-[#0071e3] transition-all"
          autoComplete="off"
        />

        <div className="grid grid-cols-3 gap-6">
          <div className="bg-white border border-[#d2d2d7] rounded-[16px] p-6 shadow-sm">
            <div className="text-3xl font-semibold text-[#0071e3]">{filtered.length}</div>
            <div className="text-xs font-medium text-[#86868b] uppercase tracking-wider mt-1">Active Prescriptions</div>
          </div>
          <div className="bg-white border border-[#d2d2d7] rounded-[16px] p-6 shadow-sm">
            <div className="text-3xl font-semibold">{filtered.filter(e => e.refills > 0).length}</div>
            <div className="text-xs font-medium text-[#86868b] uppercase tracking-wider mt-1">Refills Available</div>
          </div>
          <div className="bg-white border border-[#d2d2d7] rounded-[16px] p-6 shadow-sm">
            <div className="text-3xl font-semibold">
              {filtered.length > 0 ? Math.round(filtered.reduce((acc, curr) => acc + curr.qty, 0) / filtered.length) : 0}
            </div>
            <div className="text-xs font-medium text-[#86868b] uppercase tracking-wider mt-1">Average Qty</div>
          </div>
        </div>

        <div className="space-y-4">
          {filtered.length === 0 ? (
            <div className="text-center py-16 bg-white rounded-[16px] border border-[#d2d2d7]">
              <p className="text-[#86868b] text-lg">No matching medications, patients, or schedules found.</p>
            </div>
          ) : (
            filtered.map(ev => (
              <div 
                key={ev.id} 
                onClick={() => setSelectedEvent(ev)}
                className="bg-white rounded-[16px] p-6 border border-[#d2d2d7] shadow-sm hover:shadow-md transition-all cursor-pointer flex justify-between items-center"
              >
                <div>
                  <h3 className="text-xl font-semibold text-[#1d1d1f] tracking-tight">
                    {ev.generic} <span className="text-[#86868b] font-normal">/ {ev.brand}</span>
                  </h3>
                  <p className="text-[#1d1d1f] font-medium mt-2 text-sm">{ev.sig}</p>
                </div>
                <div className="text-right">
                  <span className={`inline-flex items-center px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider ${ev.refills > 0 ? 'bg-[#e8f5e9] text-[#2e7d32]' : 'bg-[#ffebee] text-[#c62828]'}`}>
                    {ev.refills > 0 ? `Refill in ${Math.floor(Math.random() * 14 + 1)} Days` : '0 Refills Left'}
                  </span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {selectedEvent && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/30 backdrop-blur-md transition-opacity" onClick={() => setSelectedEvent(null)}>
          <div className="bg-white rounded-[24px] p-8 max-w-lg w-full shadow-2xl relative" onClick={e => e.stopPropagation()}>
            <button onClick={() => setSelectedEvent(null)} className="absolute top-6 right-6 text-[#86868b] hover:text-[#1d1d1f] text-xl leading-none">&times;</button>
            <h2 className="text-2xl font-semibold tracking-tight mb-1">{selectedEvent.generic}</h2>
            <p className="text-[#0071e3] font-medium mb-6">{selectedEvent.brand}</p>
            
            <div className="space-y-5">
              <div>
                <h4 className="text-xs font-bold text-[#86868b] uppercase tracking-wider mb-1">What It Treats</h4>
                <p className="text-sm font-medium text-[#1d1d1f]">{selectedEvent.indication}</p>
              </div>
              <div>
                <h4 className="text-xs font-bold text-[#86868b] uppercase tracking-wider mb-1">Side Effects</h4>
                <p className="text-sm text-[#1d1d1f]">{selectedEvent.sideEffects}</p>
              </div>
              <div>
                <h4 className="text-xs font-bold text-[#86868b] uppercase tracking-wider mb-1">Safe Storage</h4>
                <p className="text-sm text-[#1d1d1f]">{selectedEvent.storage}</p>
              </div>
              <div className="pt-4 border-t border-[#d2d2d7]">
                <p className="text-xs text-[#86868b]">Prescribed by {selectedEvent.prescriber}</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
