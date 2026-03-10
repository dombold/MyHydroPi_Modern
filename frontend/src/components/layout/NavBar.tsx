import { NavLink } from "react-router-dom";

const links = [
  { to: "/", label: "Dashboard" },
  { to: "/timers", label: "Timers" },
  { to: "/graphs", label: "Graphs" },
  { to: "/dosage", label: "Dosage" },
  { to: "/settings", label: "Settings" },
];

export default function NavBar() {
  return (
    <header className="relative z-20 border-b border-hydropi-800/30 shadow-[0_2px_12px_rgba(3,60,115,0.15)]"
      style={{ background: "linear-gradient(135deg, #033C73 0%, #074d8f 60%, #1271c2 100%)" }}>
      <div className="max-w-6xl mx-auto px-4 flex items-center gap-5 h-16">
        {/* Logo */}
        <NavLink to="/" className="flex items-center shrink-0 select-none">
          <img
            src="/hydropi-logo.png"
            alt="HydroPi"
            className="h-10 w-auto object-contain drop-shadow-sm"
          />
        </NavLink>

        {/* Divider */}
        <div className="h-6 w-px bg-white/20" />

        {/* Nav links */}
        <nav className="flex gap-1 flex-wrap">
          {links.map(({ to, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/"}
              className={({ isActive }) =>
                [
                  "px-3 py-1.5 rounded-md text-sm font-medium",
                  "transition-[background-color,color,opacity] duration-150",
                  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/60",
                  isActive
                    ? "bg-white/20 text-white shadow-[inset_0_1px_0_rgba(255,255,255,0.15)]"
                    : "text-white/75 hover:text-white hover:bg-white/10 active:bg-white/20",
                ].join(" ")
              }
            >
              {label}
            </NavLink>
          ))}
        </nav>
      </div>
    </header>
  );
}
