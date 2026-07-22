import Link from "next/link";
export function Navigation({ active }: { active: string }) {
  const links = [
    { id: "patient", label: "Medicine Cabinet", href: "/" },
    { id: "pharmacist", label: "Pharmacist Queue", href: "/pharmacist" },
    { id: "md", label: "Clinical Alerts", href: "/md" },
    { id: "how", label: "How It Works", href: "/how-it-works" }
  ];
  return (
    <nav className="flex flex-wrap justify-center gap-2 mb-8 bg-white/80 backdrop-blur-xl p-2 rounded-[24px] border border-[#d2d2d7] shadow-sm max-w-fit mx-auto">
      {links.map(l => (
        <Link key={l.id} href={l.href} className={`px-5 py-2 text-sm font-medium rounded-full transition-colors ${active === l.id ? 'bg-[#1d1d1f] text-white' : 'text-[#86868b] hover:text-[#1d1d1f]'}`}>
          {l.label}
        </Link>
      ))}
    </nav>
  );
}
