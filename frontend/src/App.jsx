import React from "react";
import { RotateCcw, Siren, Wifi, WifiOff, Zap } from "lucide-react";
import { postDemo } from "./api/client";
import AlertsPanel from "./components/AlertsPanel";
import DeviceStatusPanel from "./components/DeviceStatusPanel";
import OfficeLayout from "./components/OfficeLayout";
import PowerPanel from "./components/PowerPanel";
import RoomCard from "./components/RoomCard";
import { useLiveState } from "./hooks/useLiveState";

function connectionLabel(connection) {
  if (connection === "connected") return "Live connected";
  if (connection === "polling") return "Polling fallback active";
  if (connection === "offline") return "Backend offline";
  return "Reconnecting";
}

export default function App() {
  const { state, connection, setState } = useLiveState();

  async function runDemoAction(path) {
    const nextState = await postDemo(path);
    setState(nextState);
  }

  if (!state) {
    return (
      <main className="loading-screen">
        <div className="loading-mark" />
        <p>Connecting to backend...</p>
      </main>
    );
  }

  return (
    <main className="app-shell">
      <div className="topbar">
        <div className={`connection ${connection}`}>
          {connection === "connected" ? <Wifi size={18} /> : <WifiOff size={18} />}
          <span>{connectionLabel(connection)}</span>
        </div>
        <div className="last-updated">Updated {new Date(state.lastUpdated).toLocaleTimeString()}</div>
      </div>

      <div className="dashboard-grid">
        <OfficeLayout rooms={state.rooms} />
        <aside className="side-stack">
          <PowerPanel state={state} />
          <AlertsPanel alerts={state.activeAlerts} />
          <section className="panel demo-panel">
            <div className="panel-title">
              <h2>Demo Controls</h2>
            </div>
            <div className="demo-actions">
              <button onClick={() => runDemoAction("/api/demo/set-room-all-on/work-room-2")}>
                <Zap size={16} />
                Work Room 2 ON
              </button>
              <button onClick={() => runDemoAction("/api/demo/trigger-after-hours-alert")}>
                <Siren size={16} />
                Trigger Alert
              </button>
              <button onClick={() => runDemoAction("/api/demo/reset")}>
                <RotateCcw size={16} />
                Reset
              </button>
            </div>
          </section>
        </aside>
      </div>

      <section className="room-summary">
        {state.rooms.map((room) => (
          <RoomCard room={room} key={room.id} />
        ))}
      </section>

      <DeviceStatusPanel rooms={state.rooms} />
    </main>
  );
}
