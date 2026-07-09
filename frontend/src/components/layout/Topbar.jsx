import { Bell, Wifi, WifiOff } from "lucide-react";
import useWebSocket from "../../hooks/useWebSocket";

function Topbar() {
  const { connected } = useWebSocket({}, true);

  return (
    <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-6 shadow-sm">
      <div>
        <h2 className="text-2xl font-bold text-slate-800">Sherlock AI</h2>
        <p className="text-sm text-slate-500">AI-Powered Candidate Identifier</p>
      </div>

      <div className="flex items-center gap-6">
        {/* Live WebSocket status */}
        <div
          className={`flex items-center gap-1.5 text-sm font-medium px-3 py-1 rounded-full transition-colors ${
            connected
              ? "bg-emerald-100 text-emerald-700"
              : "bg-slate-100 text-slate-500"
          }`}
          title={connected ? "WebSocket live — real-time updates active" : "WebSocket disconnected"}
        >
          {connected ? <Wifi size={15} /> : <WifiOff size={15} />}
          {connected ? "Live" : "Offline"}
        </div>

        <button className="relative" title="Notifications">
          <Bell className="text-slate-600" size={22} />
          <span className="absolute -top-1 -right-1 h-2 w-2 rounded-full bg-red-500" />
        </button>
      </div>
    </header>
  );
}

export default Topbar;