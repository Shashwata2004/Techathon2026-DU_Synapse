import React from "react";
import { Fan, Lightbulb } from "lucide-react";

function formatTime(value) {
  return new Intl.DateTimeFormat(undefined, {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  }).format(new Date(value));
}

export default function DeviceStatusPanel({ rooms }) {
  return (
    <section className="panel device-panel">
      <div className="panel-title">
        <h2>Device Status</h2>
      </div>
      {rooms.map((room) => (
        <div key={room.id} className="room-device-group">
          <div className="group-heading">
            <h3>{room.name}</h3>
            <span>{room.currentPower}W</span>
          </div>
          <div className="device-list">
            {room.devices.map((device) => {
              const Icon = device.type === "fan" ? Fan : Lightbulb;
              return (
                <div className="device-row" key={device.id}>
                  <Icon size={18} />
                  <span className="device-name">{device.name}</span>
                  <span className={`status-pill ${device.status.toLowerCase()}`}>{device.status}</span>
                  <span className="watts">{device.currentPower}W</span>
                  <span className="changed">{formatTime(device.lastChanged)}</span>
                </div>
              );
            })}
          </div>
        </div>
      ))}
    </section>
  );
}
