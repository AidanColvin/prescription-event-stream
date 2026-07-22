"use client";

import React, { useState, useMemo } from "react";

const masterEvents = [
  { id: "1", rxId: "RX-98231", patient: "Mary Smith", generic: "Zolpidem Tartrate", brand: "Ambien", schedule: "Schedule IV", indication: "Insomnia", compliance: "Standard", qty: 30, refills: 2, subPermitted: "Yes", source: "Drugs@FDA" },
  { id: "2", rxId: "RX-11234", patient: "Patricia Johnson", generic: "Lisinopril", brand: "Zestril", schedule: "Non-controlled", indication: "Hypertension", compliance: "Standard", qty: 90, refills: 3, subPermitted: "Yes", source: "DailyMed" },
  { id: "3", rxId: "RX-55421", patient: "James Smith", generic: "Amphetamine Salts", brand: "Adderall", schedule: "Schedule II", indication: "ADHD", compliance: "Review Required", qty: 90, refills: 0, subPermitted: "No", source: "AHFS" }
];

export default function PharmacistView() {
  const [search, setSearch] = useState("");
  const [selectedEvent, setSelectedEvent] = useState<typeof masterEvents[0] | null>(null);

  const filtered = useMemo(() => {
    const q = search.toLowerCase().trim();
    return masterEvents.filter(ev => 
      ev.patient.toLowerCase().includes(q) || 
      ev.generic.toLowerCase().includes(q) || 
      ev.brand.toLowerCase().includes(q) || 
      ev.schedule.toLowerCase().includes(q) || 
      ev.rxId.toLowerCase().includes(q) ||
      ev.indication.toLowerCase().includes(q)
    );
  }, [search]);

  return (
    <main className="min-h-screen bg-[#f5f5f7] text-[#1d1d1f] p-8" style={{ fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", sans-serif' }}>
      <div className="max-w-4xl mx-auto space-y-8">
        <header className="text-center space-y-2">
          <h1 className="text-4xl font-semibold tracking-tight">Triage Queue</h1>
        </header>

        <input
          type="text"
          placeholder="Spotlight search: medication, patient, schedule, or Rx ID..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full border border-[#d2d2d7] rounded-full px-6 py-4 text-lg shadow-sm focus:outline-none focus:border-[#0071e3] transition-all"
          autoComplete="off"
        />

        <div className="grid grid-cols-3 gap-6">
          <div className="bg-white border border-[#d2d2d7] rounded-[16px] p-6 shadow-sm">
            <div className="text-3xl font-semibold text-[#0071e3]">{filtered.length}</div>
            <div className="text-xs font-medium text-[#86868b] uppercase tracking-wider mt-1">Pending Orders</div>
          </div>
          <div className="bg-white border border-[#d2d2d7] rounded-[16px] p-6 shadow-sm">
            <div className="text-3xl font-semibold text-[#c62828]">{filtered.filter(e => e.compliance === "Review Required").length}</div>
            <div className="text-xs font-medium text-[#86868b] uppercase tracking-wider mt-1">Reviews Required</div>
          </div>
          <div className="bg-white border border-[#d2d2d7] rounded-[16px] p-6 shadow-sm">
            <div className="text-3xl font-semibold">{filtered.filter(e => e.schedule.includes('II')).length}</div>
            <div className="text-xs font-medium text-[#86868b] uppercase tracking-wider mt-1">C-II Orders</div>
          </div>
        </div>

        <div className="space-y-4">
          {filtered.length === 0 ? (
            <div className="text-center py-16 bg-white rounded-[16px] border border-[#d2d2d7]">
              <p className="text-[#86868b] text-lg">No matching medications, patients, or schedules found.</p>
            </div>
          ) : (
            filtered.map(ev => {
              const isReview = ev.compliance === 'Review Required';
              return (
                <div 
                  key={ev.id} 
                  onClick={() => setSelectedEvent(ev)}
                  className={`bg-white rounded-[16px] p-6 border shadow-sm hover:shadow-md transition-all cursor-pointer flex justify-between items-center ${isReview ? 'border-[#c62828] bg-[#fffcfc]' : 'border-[#d2d2d7]'}`}
                >
                  <div>
                    <p className="text-sm font-medium text-[#86868b] mb-1">{ev.patient}</p>
                    <h3 className="text-xl font-semibold text-[#1d1d1f] tracking-tight">
                      {ev.generic} <span className="text-[#86868b] font-normal">/ {ev.brand}</span>
                    </h3>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className={`px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider ${ev.schedule.includes('II') ? 'bg-[#fff9e6] text-[#856404] border border-[#ffe066]' : 'bg-[#f1f1f2] text-[#48484a]'}`}>
                      {ev.schedule}
                    </span>
                    {isReview && <span className="w-3 h-3 rounded-full bg-[#c62828] animate-pulse" />}
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
            <h2 className="text-2xl font-semibold tracking-tight mb-1">{selectedEvent.generic}</h2>
            <p className="text-[#86868b] font-medium mb-6">Patient: <span className="text-[#1d1d1f]">{selectedEvent.patient}</span></p>
            
            <div className="grid grid-cols-2 gap-6 mb-6">
              <div>
                <h4 className="text-xs font-bold text-[#86868b] uppercase tracking-wider mb-1">Rx ID</h4>
                <p className="text-sm font-mono text-[#1d1d1f]">{selectedEvent.rxId}</p>
              </div>
              <div>
                <h4 className="text-xs font-bold text-[#86868b] uppercase tracking-wider mb-1">Quantity</h4>
                <p className="text-sm font-medium text-[#1d1d1f]">{selectedEvent.qty} (Refills: {selectedEvent.refills})</p>
              </div>
              <div>
                <h4 className="text-xs font-bold text-[#86868b] uppercase tracking-wider mb-1">Substitution</h4>
                <p className="text-sm text-[#1d1d1f]">{selectedEvent.subPermitted === 'Yes' ? 'Permitted' : 'Dispense as Written'}</p>
              </div>
              <div>
                <h4 className="text-xs font-bold text-[#86868b] uppercase tracking-wider mb-1">Source</h4>
                <p className="text-sm text-[#0071e3] cursor-pointer hover:underline">{selectedEvent.source}</p>
              </div>
            </div>

            <div className="flex gap-3">
              <button className="flex-1 bg-[#0071e3] text-white py-3 rounded-full text-sm font-medium hover:bg-[#0077ed] transition-colors">Verify Dispense</button>
              {selectedEvent.compliance === 'Review Required' && (
                <button className="flex-1 bg-[#ffebee] text-[#c62828] py-3 rounded-full text-sm font-medium hover:bg-[#ffcdd2] transition-colors">Request Clarification</button>
              )}
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
