"use client";

import React, { useState, useMemo } from "react";

const masterEvents = [
  { id: "1", patient: "Mary Smith", generic: "Zolpidem Tartrate", brand: "Ambien", schedule: "Schedule IV", indication: "Insomnia", adherence: 95, interactions: "None", contraindications: "None", regimen: "10 mg tablet at bedtime", otherMeds: "Atorvastatin 20mg", dea: "BJ8839201" },
  { id: "2", patient: "Patricia Johnson", generic: "Lisinopril", brand: "Zestril", schedule: "Non-controlled", indication: "Hypertension", adherence: 65, interactions: "NSAIDs may reduce antihypertensive effect", contraindications: "History of angioedema", regimen: "20 mg tablet daily", otherMeds: "Ibuprofen 400mg PRN", dea: "None" },
  { id: "3", patient: "James Smith", generic: "Amphetamine Salts", brand: "Adderall", schedule: "Schedule II", indication: "ADHD", adherence: 92, interactions: "Severe interaction with MAOIs", contraindications: "Glaucoma, severe anxiety", regimen: "20 mg capsule daily", otherMeds: "None", dea: "BJ8839201" }
];

export default function MDView() {
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
      <div className="max-w-4xl mx-auto space-y-8">
        <header className="text-center space-y-2">
          <h1 className="text-4xl font-semibold tracking-tight">Clinical Alert Feed</h1>
        </header>

        <input
          type="text"
          placeholder="Spotlight search: patient, medication, schedule, or condition..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full border border-[#d2d2d7] rounded-full px-6 py-4 text-lg shadow-sm focus:outline-none focus:border-[#0071e3] transition-all"
          autoComplete="off"
        />

        <div className="grid grid-cols-3 gap-6">
          <div className="bg-white border border-[#d2d2d7] rounded-[16px] p-6 shadow-sm">
            <div className="text-3xl font-semibold text-[#0071e3]">{filtered.length}</div>
            <div className="text-xs font-medium text-[#86868b] uppercase tracking-wider mt-1">Patients in View</div>
          </div>
          <div className="bg-white border border-[#d2d2d7] rounded-[16px] p-6 shadow-sm">
            <div className="text-3xl font-semibold text-[#c62828]">{filtered.filter(e => e.interactions !== "None").length}</div>
            <div className="text-xs font-medium text-[#86868b] uppercase tracking-wider mt-1">Interaction Alerts</div>
          </div>
          <div className="bg-white border border-[#d2d2d7] rounded-[16px] p-6 shadow-sm">
            <div className="text-3xl font-semibold text-[#856404]">{filtered.filter(e => e.adherence < 80).length}</div>
            <div className="text-xs font-medium text-[#86868b] uppercase tracking-wider mt-1">Low Adherence</div>
          </div>
        </div>

        <div className="space-y-4">
          {filtered.length === 0 ? (
            <div className="text-center py-16 bg-white rounded-[16px] border border-[#d2d2d7]">
              <p className="text-[#86868b] text-lg">No matching medications, patients, or schedules found.</p>
            </div>
          ) : (
            filtered.map(ev => {
              const isLowAdherence = ev.adherence < 80;
              const hasInteraction = ev.interactions !== "None";
              return (
                <div 
                  key={ev.id} 
                  onClick={() => setSelectedEvent(ev)}
                  className="bg-white rounded-[16px] p-6 border border-[#d2d2d7] shadow-sm hover:shadow-md transition-all cursor-pointer flex justify-between items-start"
                >
                  <div>
                    <h3 className="text-xl font-semibold text-[#1d1d1f] tracking-tight mb-1">{ev.patient}</h3>
                    <p className="text-sm text-[#86868b]">{ev.generic} <span className="font-medium text-[#1d1d1f]">/ {ev.brand}</span></p>
                    {hasInteraction && (
                      <div className="mt-4 p-3 bg-[#ffebee] border border-[#ffcdd2] rounded-lg inline-block">
                        <p className="text-[#c62828] text-sm font-semibold">Interaction Warning</p>
                        <p className="text-[#c62828] text-xs mt-1">{ev.interactions}</p>
                      </div>
                    )}
                  </div>
                  <div className="text-right">
                    <span className={`text-3xl font-bold tracking-tight ${isLowAdherence ? 'text-[#c62828]' : 'text-[#2e7d32]'}`}>
                      {ev.adherence}%
                    </span>
                    <p className="text-xs font-bold text-[#86868b] uppercase tracking-wider mt-1">Adherence</p>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>

      {selectedEvent && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/30 backdrop-blur-md transition-opacity" onClick={() => setSelectedEvent(null)}>
          <div className="bg-white rounded-[24px] p-8 max-w-lg w-full shadow-2xl relative" onClick={e => e.stopPropagation()}>
            <button onClick={() => setSelectedEvent(null)} className="absolute top-6 right-6 text-[#86868b] hover:text-[#1d1d1f] text-xl leading-none">&times;</button>
            <h2 className="text-2xl font-semibold tracking-tight mb-1">{selectedEvent.patient}</h2>
            <p className="text-[#0071e3] font-medium mb-6">Prescribed Regimen</p>
            
            <div className="space-y-5">
              <div className="p-4 bg-[#f5f5f7] rounded-xl border border-[#d2d2d7]">
                <h4 className="text-sm font-semibold text-[#1d1d1f]">{selectedEvent.generic} / {selectedEvent.brand}</h4>
                <p className="text-sm text-[#86868b] mt-1">{selectedEvent.regimen}</p>
              </div>
              <div>
                <h4 className="text-xs font-bold text-[#86868b] uppercase tracking-wider mb-1">Other Active Medications</h4>
                <p className="text-sm font-medium text-[#1d1d1f]">{selectedEvent.otherMeds}</p>
              </div>
              {selectedEvent.contraindications !== "None" && (
                <div>
                  <h4 className="text-xs font-bold text-[#c62828] uppercase tracking-wider mb-1">Contraindications</h4>
                  <p className="text-sm text-[#1d1d1f]">{selectedEvent.contraindications}</p>
                </div>
              )}
              <div className="pt-4 border-t border-[#d2d2d7] flex justify-between items-center">
                <p className="text-xs text-[#86868b]">DEA Authorization</p>
                <p className="text-xs font-mono font-medium text-[#1d1d1f]">{selectedEvent.dea}</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
