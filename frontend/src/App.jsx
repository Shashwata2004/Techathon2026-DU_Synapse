import React, { useState } from "react";
import { Wifi, WifiOff } from "lucide-react";
import { postDemo } from "./api/client";
import AlertsPanel from "./components/AlertsPanel";
import {
  ActivityFeed,
  EnergyRecommendationPanel,
  SimulatorToggle,
  TopConsumerInsight,
} from "./components/DashboardInsights";
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
  const [pendingDeviceIds, setPendingDeviceIds] = useState(() => new Set());
  const [toggleError, setToggleError] = useState("");
  const [simulatorPending, setSimulatorPending] = useState(false);

  async function toggleDevice(deviceId) {
    if (pendingDeviceIds.has(deviceId)) return;

    setToggleError("");
    setPendingDeviceIds((current) => new Set(current).add(deviceId));

    try {
      const nextState = await postDemo(`/api/demo/toggle/${encodeURIComponent(deviceId)}`);
      setState(nextState);
    } catch {
      setToggleError("Could not toggle that device. Check the backend connection.");
    } finally {
      setPendingDeviceIds((current) => {
        const next = new Set(current);
        next.delete(deviceId);
        return next;
      });
    }
  }

  async function toggleSimulator() {
    if (simulatorPending) return;

    setToggleError("");
    setSimulatorPending(true);
    try {
      const nextState = await postDemo("/api/demo/simulator/toggle");
      setState(nextState);
    } catch {
      setToggleError("Could not change simulator mode. Check the backend connection.");
    } finally {
      setSimulatorPending(false);
    }
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
        <SimulatorToggle
          simulatorStatus={state.simulatorStatus}
          isPending={simulatorPending}
          onToggle={toggleSimulator}
        />
        {toggleError ? (
          <div className="toggle-error" role="status">
            {toggleError}
          </div>
        ) : null}
        <div className="last-updated">Updated {new Date(state.lastUpdated).toLocaleTimeString()}</div>
      </div>

      <div className="dashboard-grid">
        <OfficeLayout rooms={state.rooms} onToggleDevice={toggleDevice} pendingDeviceIds={pendingDeviceIds} />
        <aside className="side-stack">
          <PowerPanel state={state} />
          <TopConsumerInsight state={state} />
          <EnergyRecommendationPanel state={state} />
          <AlertsPanel alerts={state.activeAlerts} />
        </aside>
      </div>

      <ActivityFeed events={state.events} />

      <section className="room-summary">
        {state.rooms.map((room) => (
          <RoomCard room={room} key={room.id} />
        ))}
      </section>

      <DeviceStatusPanel rooms={state.rooms} />
    </main>
  );
}
