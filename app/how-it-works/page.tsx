import { Navigation } from "../nav";
export default function HowItWorks() {
  return (
    <main className="min-h-screen bg-[#f5f5f7] text-[#1d1d1f] p-8 font-sans">
      <div className="max-w-3xl mx-auto space-y-6">
        <Navigation active="how" />
        <h1 className="text-4xl font-semibold tracking-tight text-center mb-8">Architecture</h1>
        <div className="bg-white rounded-[24px] p-8 shadow-sm border border-[#d2d2d7] space-y-6 text-lg font-medium text-[#48484a]">
          <p>Built with radical focus. A serverless Node.js backend deployed on Vercel streaming immutable prescription events.</p>
          <p>U.S. Data Sources: FDA, DailyMed, AHFS, PDR.</p>
          <a href="https://github.com/AidanColvin/prescription-event-stream" className="inline-block mt-4 bg-[#1d1d1f] text-white px-6 py-3 rounded-full font-bold text-sm tracking-wide uppercase hover:bg-[#333] transition-colors">View Repository</a>
        </div>
      </div>
    </main>
  );
}
