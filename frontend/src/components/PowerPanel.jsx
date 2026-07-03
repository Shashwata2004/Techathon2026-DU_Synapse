import React from "react";
import { Activity, Gauge, Zap } from "lucide-react";

export default function PowerPanel({ state }) {
  const maxRoomWatts = Math.max(...Object.values(state.roomWisePower), 1);
  return (
    <section className="panel">
      <div className="panel-title">
        <h2>Power</h2>
      </div>
      <div className="metric-grid">
        <div className="metric">
          <Zap size={20} />
          <span>Total Current</span>
          <strong>{state.totalCurrentWatts}W</strong>
        </div>
        <div className="metric">
          <Gauge size={20} />
          <span>Estimated Today</span>
          <strong>{state.estimatedKwhToday.toFixed(3)} kWh</strong>
        </div>
        <div className="metric">
          <Activity size={20} />
          <span>Active Devices</span>
          <strong>
            {state.activeDeviceCount}/{state.totalDeviceCount}
          </strong>
        </div>
      </div>
      <div className="room-power-list">
        {Object.entries(state.roomWisePower).map(([room, watts]) => (
          <div className="power-row" key={room}>
            <div>
              <span>{room}</span>
              <strong>{watts}W</strong>
            </div>
            <div className="meter">
              <span style={{ width: `${Math.round((watts / maxRoomWatts) * 100)}%` }} />
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
