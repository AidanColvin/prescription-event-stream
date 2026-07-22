"use client";

import React, { useState, useMemo } from "react";

const mockEvents = [
  { id: "1", patient: "Mary Smith", generic: "Zolpidem Tartrate", brand: "Ambien", schedule: "Schedule IV", indication: "Insomnia", sig: "Take 1 tablet at bedtime.", qty: 30, refills: 2 },
  { id: "2", patient: "Patricia Johnson", generic: "Lisinopril", brand: "Zestril", schedule: "Non-controlled", indication: "Hypertension", sig: "Take 1 tablet daily.", qty: 90, refills: 3 }
];

/** Renders the Patient portal with Spotlight-style live universal search. */
export default function PatientView() {
  const [search, setSearch] = useState("");

  const filtered = useMemo(() => {
    const q = search.toLowerCase();
    return mockEvents.filter(ev => 
      ev.patient.toLowerCase().includes(q) || 
      ev.generic.toLowerCase().includes(q) || 
      ev.brand.toLowerCase().includes(q) || 
      ev.schedule.toLowerCase().includes(q) || 
      ev.indication.toLowerCase().includes(q)
    );
  }, [search]);

  return (
    <main className="min-h-screen bg-[#f5f5f7] text-[#1d1d1f] p-8 font-sans">
      <div className="max-w-5xl mx-auto space-y-8">
        <header className="text-center space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-[#e8f5e9] text-[#2e7d32] rounded-full text-xs font-medium">
            <span className="w-2 h-2 rounded-full bg-[#34c759] animate-pulse" /> Live Stream
          </div>
          <h1 className="text-4xl font-semibold tracking-tight">Patient Portal</h1>
        </header>

        <input
          type="text"
          placeholder="Spotlight search: medication, brand, patient, schedule, or condition..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full border border-[#d2d2d7] rounded-full px-6 py-4 text-lg shadow-sm focus:outline-none focus:border-[#0071e3] transition-all"
        />

        <div className="grid grid-cols-3 gap-6">
          <div className="bg-white border border-[#d2d2d7] rounded-[16px] p-6 shadow-sm">
            <div className="text-3xl font-semibold text-[#0071e3]">{filtered.length}</div>
            <div className="text-xs font-medium text-[#86868b] uppercase tracking-wider mt-1">Active Events</div>
          </div>
          <div className="bg-white border border-[#d2d2d7] rounded-[16px] p-6 shadow-sm">
            <div className="text-3xl font-semibold">{filtered.filter(e => e.qty > 60).length}</div>
            <div className="text-xs font-medium text-[#86868b] uppercase tracking-wider mt-1">Compliance Flags</div>
          </div>
          <div className="bg-white border border-[#d2d2d7] rounded-[16px] p-6 shadow-sm">
            <div className="text-3xl font-semibold">
              {filtered.length > 0 ? Math.round(filtered.reduce((acc, curr) => acc + curr.qty, 0) / filtered.length) : 0}
            </div>
            <div className="text-xs font-medium text-[#86868b] uppercase tracking-wider mt-1">Average Qty</div>
          </div>
        </div>

        <div className="bg-white border border-[#d2d2d7] rounded-[16px] shadow-sm overflow-hidden">
          <table className="w-full text-left text-sm">
            <thead className="bg-[#fafafa] border-b border-[#d2d2d7]">
              <tr>
                <th className="p-4 font-medium text-[#86868b]">Patient Profile</th>
                <th className="p-4 font-medium text-[#86868b]">Medication (Generic / Brand)</th>
                <th className="p-4 font-medium text-[#86868b]">What It Treats</th>
                <th className="p-4 font-medium text-[#86868b]">Directions & Refills</th>
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={4} className="p-12 text-center text-[#86868b]">No matching medications, patients, or schedules found.</td>
                </tr>
              ) : (
                filtered.map(ev => (
                  <tr key={ev.id} className="border-b border-[#d2d2d7] last:border-0">
                    <td className="p-4 font-medium">{ev.patient}</td>
                    <td className="p-4">
                      <span className="font-semibold">{ev.generic}</span> / <span className="text-[#0071e3]">{ev.brand}</span>
                    </td>
                    <td className="p-4">{ev.indication}</td>
                    <td className="p-4">
                      {ev.sig}<br/>
                      <span className="text-xs text-[#86868b] mt-1 block">{ev.refills} refills remaining</span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </main>
  );
}
