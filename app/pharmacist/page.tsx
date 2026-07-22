"use client";

import React, { useState } from "react";

/* Takes patient age and drug generic, returns warning if pediatric contraindication exists. */
const checkPediatric = (age: number, generic: string) => 
  (age < 18 && generic.includes("Zolpidem")) 
    ? `James Smith is ${age} years old. Ambien is not approved for children.` 
    : null;

/* Takes schedule, quantity, and refills, returns warning if limits are exceeded. */
const checkScheduleLimit = (schedule: string, qty: number, refills: number) => {
  if (schedule === "Schedule IV") {
    const totalDays = qty * (refills + 1);
    if (totalDays > 180) {
      return `Also: ${qty} tablets with ${refills} refills is ${totalDays} days. Schedule IV allows 5 fills in 6 months.`;
    }
  }
  return null;
};

/* Takes schedule and DEA number, returns warning if validity fails. */
const checkDea = (schedule: string, dea: string) => {
  const isControlled = schedule.includes("Schedule");
  if (isControlled && (!dea || dea === "None")) {
    return "Prescriber wrote a controlled substance without a valid DEA registration number on file.";
  }
  return null;
};

const queue = [
  {
    id: "1", patient: "James Smith", age: 11, generic: "Zolpidem Tartrate", brand: "Ambien", schedule: "Schedule IV", qty: 90, refills: 4, prescriber: "Dr. Sarah Jenkins", phone: "919-555-4811", dea: "BJ8839201",
    citations: [
      "R1 (Age Contraindication): Zolpidem Tartrate safety and efficacy in pediatric patients have not been established. DailyMed SPL 8.4.",
      "R2 (Schedule Limit): Schedule IV prescriptions may not be filled or refilled more than 6 months after the date of issue or be refilled more than 5 times. 21 CFR 1306.22."
    ]
  },
  {
    id: "2", patient: "Mary Smith", age: 51, generic: "Amphetamine Salts", brand: "Adderall", schedule: "Schedule II", qty: 30, refills: 0, prescriber: "Dr. Robert Chen, DO", phone: "919-832-0011", dea: "None",
    citations: [
      "R3 (DEA Validity): A prescription for a controlled substance may only be issued by a physician who is registered with the DEA. 21 CFR 1306.03."
    ]
  }
];

export default function PharmacistView() {
  const totalProcessed = 214;
  const [currentIndex, setCurrentIndex] = useState(0);

  const flagged = queue.map(rx => ({
    ...rx,
    warnings: [
      checkPediatric(rx.age, rx.generic),
      checkScheduleLimit(rx.schedule, rx.qty, rx.refills),
      checkDea(rx.schedule, rx.dea)
    ].filter(Boolean)
  })).filter(rx => rx.warnings.length > 0);

  const fineCount = totalProcessed - flagged.length;
  const currentAlert = flagged[currentIndex];
  const remaining = flagged.length - 1 - currentIndex;

  return (
    <main className="min-h-screen bg-[#f5f5f7] text-[#1d1d1f] p-8" style={{ fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", sans-serif' }}>
      <div className="max-w-xl mx-auto mt-12">
        <h1 className="text-3xl font-semibold tracking-tight text-center mb-2">Second Look</h1>
        <p className="text-center text-[#86868b] mb-12">
          <span className="font-medium text-[#1d1d1f]">{totalProcessed}</span> prescriptions read this morning.<br/>
          <span className="font-medium text-[#1d1d1f]">{fineCount}</span> are fine.
        </p>

        {currentAlert ? (
          <div className="bg-white border-2 border-[#1d1d1f] rounded-[16px] p-8 shadow-sm relative">
            <h2 className="text-2xl font-bold text-[#1d1d1f] mb-6">Do not fill.</h2>

            <div className="space-y-4 text-lg text-[#1d1d1f] mb-8 font-medium">
              {currentAlert.warnings.map((w, i) => (
                <p key={i}>{w}</p>
              ))}
              <p className="pt-2">
                {currentAlert.prescriber} wrote it.<br/>
                {currentAlert.phone}
              </p>
            </div>

            <button className="w-full bg-[#1d1d1f] text-white rounded-full py-4 font-semibold text-lg hover:bg-[#333] transition-colors mb-6">
              Call the prescriber
            </button>

            <details className="group cursor-pointer">
              <summary className="text-[#86868b] font-medium list-none flex items-center gap-2 outline-none">
                Why we stopped this <span className="group-open:rotate-90 transition-transform text-xs">▶</span>
              </summary>
              <div className="mt-4 p-4 bg-[#f5f5f7] rounded-xl text-sm text-[#48484a] space-y-3">
                {currentAlert.citations.map((c, i) => (
                  <p key={i}>{c}</p>
                ))}
              </div>
            </details>
          </div>
        ) : (
          <div className="text-center text-[#86868b] mt-24">
            <p className="text-xl font-medium">Queue Clear</p>
            <p>All flagged prescriptions have been reviewed.</p>
          </div>
        )}

        {remaining > 0 && (
          <div className="text-center mt-8">
            <button 
              onClick={() => setCurrentIndex(prev => prev + 1)}
              className="text-[#86868b] font-medium hover:text-[#1d1d1f] transition-colors flex items-center gap-2 mx-auto"
            >
              {remaining} more need a look <span>▾</span>
            </button>
          </div>
        )}
      </div>
    </main>
  );
}
