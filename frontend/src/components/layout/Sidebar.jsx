import { NavLink, useNavigate } from "react-router-dom";
import {
  LayoutDashboard,
  Play,
  Radio,
  History,
  FileText,
  Activity,
  Users,
  BrainCircuit,
  Mic,
  Video,
  ClipboardList,
  ChevronRight,
} from "lucide-react";

const PRIMARY_NAV = [
  { to: "/new-interview", icon: Play,           label: "New Interview",   accent: "bg-blue-600 hover:bg-blue-700 text-white" },
];

const LIVE_NAV = [
  { to: "/",             icon: LayoutDashboard, label: "Dashboard" },
  { to: "/history",      icon: History,         label: "History" },
];

const ANALYSIS_NAV = [
  { to: "/participants", icon: Users,            label: "Participants" },
  { to: "/confidence",   icon: Activity,         label: "Confidence" },
  { to: "/reasoning",    icon: BrainCircuit,     label: "AI Reasoning" },
  { to: "/evidence",     icon: ClipboardList,    label: "Evidence" },
  { to: "/report",       icon: FileText,         label: "Final Report" },
];

const OFFLINE_NAV = [
  { to: "/audio",  icon: Mic,   label: "Audio Upload" },
  { to: "/video",  icon: Video, label: "Video Upload" },
];

function NavSection({ title, items }) {
  return (
    <div className="mb-4">
      <p className="px-3 mb-1 text-[10px] font-bold uppercase tracking-widest text-slate-500">
        {title}
      </p>
      {items.map(({ to, icon: Icon, label, accent }) => (
        <NavLink
          key={to}
          to={to}
          end={to === "/"}
          className={({ isActive }) =>
            accent
              ? `flex items-center gap-3 w-full px-3 py-2.5 rounded-lg mb-1 transition-colors text-sm font-semibold ${
                  isActive ? "bg-blue-700 text-white" : accent
                }`
              : `flex items-center gap-3 w-full px-3 py-2 rounded-lg mb-0.5 transition-colors text-sm font-medium ${
                  isActive
                    ? "bg-blue-600 text-white"
                    : "text-slate-300 hover:bg-slate-800 hover:text-white"
                }`
          }
        >
          <Icon size={16} />
          {label}
        </NavLink>
      ))}
    </div>
  );
}

function Sidebar() {
  return (
    <aside className="w-60 bg-slate-900 text-white flex flex-col flex-shrink-0">
      {/* Logo */}
      <div className="px-5 py-5 border-b border-slate-700">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center">
            <Radio size={16} className="text-white" />
          </div>
          <div>
            <h1 className="text-base font-bold text-white leading-tight">Sherlock AI</h1>
            <p className="text-[10px] text-slate-400">Candidate Identifier</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-3 overflow-y-auto space-y-1">
        <NavSection title="Interview" items={PRIMARY_NAV} />
        <NavSection title="Sessions" items={LIVE_NAV} />
        <NavSection title="Analysis" items={ANALYSIS_NAV} />
        <NavSection title="Offline" items={OFFLINE_NAV} />
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-slate-700 text-[11px] text-slate-500">
        Sherlock AI v1.1 · Session Mode
      </div>
    </aside>
  );
}

export default Sidebar;