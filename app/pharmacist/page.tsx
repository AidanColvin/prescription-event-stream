"use client";

import React, { useState, useEffect } from "react";

const masterEvents = [
  { id: "1", patient: "Mary Smith", generic: "Zolpidem Tartrate", brand: "Ambien", schedule: "Schedule IV", indication: "Insomnia", sig: "Take 1 tablet at bedtime.", qty: 30, refills: 2 },
  { id: "2", patient: "Patricia Johnson", generic: "Lisinopril", brand: "Zestril", schedule: "Non-controlled", indication: "Hypertension", sig: "Take 1 tablet daily.", qty: 90, refills: 3 },
  { id: "3", patient: "James Smith", generic: "Amphetamine Salts", brand: "Adderall", schedule: "Schedule II", indication: "ADHD", sig: "Take 1 capsule daily.", qty: 30, refills: 0 }
];

/* Renders the Pharmacist compliance queue with explicit Spotlight style live universal search. */
export default function PharmacistView() {
  const [filtered, setFiltered] = useState(masterEvents);
  const [stats, setStats] = useState({ total: masterEvents.length, flags: 1, avg: 50 });

  useEffect(() => {
    const searchInput = document.getElementById("search-input") as HTMLInputElement;
    
    const handleInput = (e: Event) => {
      const q = (e.target as HTMLInputElement).value.toLowerCase().trim();
      
      const newFiltered = masterEvents.filter(ev => 
        ev.patient.toLowerCase().includes(q) || 
        ev.generic.toLowerCase().includes(q) || 
        ev.brand.toLowerCase().includes(q) || 
        ev.schedule.toLowerCase().includes(q) || 
        ev.indication.toLowerCase().includes(q)
      );
      
      setFiltered(newFiltered);
      setStats({
        total: newFiltered.length,
        flags: newFiltered.filter(e => e.qty > 60).length,
        avg: newFiltered.length > 0 ? Math.round(newFiltered.reduce((sum, e) => sum + e.qty, 0) / newFiltered.length) : 0
      });
    };

    if (searchInput) searchInput.addEventListener("input", handleInput);
    return () => { if (searchInput) searchInput.removeEventListener("input", handleInput); };
  }, []);

  return (
    <main className="min-h-screen bg-[#f5f5f7] text-[#1d1d1f] p-8 font-sans">
      <div className="max-w-5xl mx-auto space-y-8">
        <header className="text-center space-y-2">
          <h1 className="text-4xl font-semibold tracking-tight">Pharmacist Compliance Queue</h1>
        </header>

        <input
          type="text"
          id="search-input"
          placeholder="Spotlight search: medication, brand, patient, schedule, or condition..."
          className="w-full border border-[#d2d2d7] rounded-full px-6 py-4 text-lg shadow-sm focus:outline-none focus:border-[#0071e3] transition-all"
          autoComplete="off"
        />

        <div className="grid grid-cols-3 gap-6">
          <div className="bg-white border border-[#d2d2d7] rounded-[16px] p-6 shadow-sm">
            <div className="text-3xl font-semibold text-[#0071e3]">{stats.total}</div>
            <div className="text-xs font-medium text-[#86868b] uppercase tracking-wider mt-1">Active Events</div>
          </div>
          <div className="bg-white border border-[#d2d2d7] rounded-[16px] p-6 shadow-sm">
            <div className="text-3xl font-semibold">{stats.flags}</div>
            <div className="text-xs font-medium text-[#86868b] uppercase tracking-wider mt-1">Compliance Flags</div>
          </div>
          <div className="bg-white border border-[#d2d2d7] rounded-[16px] p-6 shadow-sm">
            <div className="text-3xl font-semibold">{stats.avg}</div>
            <div className="text-xs font-medium text-[#86868b] uppercase tracking-wider mt-1">Average Qty</div>
          </div>
        </div>

        <div className="bg-white border border-[#d2d2d7] rounded-[16px] shadow-sm overflow-hidden">
          <table className="w-full text-left text-sm">
            <thead className="bg-[#fafafa] border-b border-[#d2d2d7]">
              <tr>
                <th className="p-4 font-medium text-[#86868b]">Patient Profile</th>
                <th className="p-4 font-medium text-[#86868b]">Medication (Generic / Brand)</th>
                <th className="p-4 font-medium text-[#86868b]">DEA Schedule</th>
                <th className="p-4 font-medium text-[#86868b]">Quantity & Refills</th>
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
                    <td className="p-4">
                      <span className={`px-2 py-1 rounded-md text-xs font-semibold ${ev.schedule.includes('II') ? 'bg-[#ffebee] text-[#c62828]' : 'bg-[#f1f1f2] text-[#48484a]'}`}>
                        {ev.schedule}
                      </span>
                    </td>
                    <td className="p-4">Qty: {ev.qty} <span className="text-[#86868b] block mt-1">Refills: {ev.refills}</span></td>
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
