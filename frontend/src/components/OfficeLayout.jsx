import React from "react";
import { Fan, Lightbulb } from "lucide-react";

function DeviceMarker({ device }) {
  const isOn = device.status === "ON";
  const className = `device-marker ${device.type} ${isOn ? "is-on" : "is-off"}`;
  const Icon = device.type === "fan" ? Fan : Lightbulb;
  return (
    <div className={className} title={`${device.name}: ${device.status}`}>
      <Icon size={device.type === "fan" ? 30 : 24} />
    </div>
  );
}

export default function OfficeLayout({ rooms }) {
  return (
    <section className="office-shell">
      <div className="office-header">
        <div>
          <h1>Smart Office Monitor</h1>
          <p>Live electricity view for 3 rooms, 15 devices</p>
        </div>
      </div>
      <div className="office-layout" aria-label="Office layout">
        {rooms.map((room) => (
          <div key={room.id} className={`room-zone ${room.activeAlerts.length ? "has-alert" : ""}`}>
            <div className="room-title">
              <span>{room.name}</span>
              <strong>{room.currentPower}W</strong>
            </div>
            <div className="room-devices">
              {room.devices.map((device) => (
                <DeviceMarker key={device.id} device={device} />
              ))}
            </div>
            <div className="furniture-grid" aria-hidden="true">
              <span />
              <span />
              <span />
              <span />
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
