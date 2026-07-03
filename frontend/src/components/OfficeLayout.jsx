import React from "react";

import floorplanImage from "../assets/office-floorplan-no-fans.png";

const DEVICE_OVERLAY_POSITIONS = {
  "drawing-room-light-1": { left: 11.2, top: 12.0 },
  "drawing-room-fan-1": { left: 19.9, top: 14.0 },
  "drawing-room-light-2": { left: 28.9, top: 12.0 },
  "drawing-room-fan-2": { left: 20.0, top: 56.0 },
  "drawing-room-light-3": { left: 19.7, top: 69.0 },
  "work-room-1-light-1": { left: 43.2, top: 12.0 },
  "work-room-1-fan-1": { left: 51.6, top: 14.0 },
  "work-room-1-light-2": { left: 60.4, top: 12.0 },
  "work-room-1-fan-2": { left: 51.6, top: 50.5 },
  "work-room-1-light-3": { left: 51.4, top: 69.0 },
  "work-room-2-light-1": { left: 74.5, top: 12.0 },
  "work-room-2-fan-1": { left: 82.8, top: 14.0 },
  "work-room-2-light-2": { left: 91.6, top: 12.0 },
  "work-room-2-fan-2": { left: 82.8, top: 50.5 },
  "work-room-2-light-3": { left: 82.8, top: 69.0 },
};

function CeilingFan({ isOn }) {
  return (
    <span className={`ceiling-fan ${isOn ? "is-on" : "is-off"}`} aria-hidden="true">
      <span className="fan-rotor">
        <span className="fan-blade fan-blade-one" />
        <span className="fan-blade fan-blade-two" />
        <span className="fan-blade fan-blade-three" />
      </span>
      <span className="fan-cap" />
      <span className="fan-stem" />
    </span>
  );
}

function LightOverlay({ isOn }) {
  return <span className={`ceiling-light ${isOn ? "is-on" : "is-off"}`} aria-hidden="true" />;
}

function DeviceOverlay({ device, isPending, onToggleDevice }) {
  const position = DEVICE_OVERLAY_POSITIONS[device.id];
  if (!position) return null;

  const isOn = device.status === "ON";
  const nextStatus = isOn ? "OFF" : "ON";
  return (
    <button
      className={`live-device-overlay ${device.type} ${isOn ? "is-on" : "is-off"} ${isPending ? "is-pending" : ""}`}
      style={{ left: `${position.left}%`, top: `${position.top}%` }}
      title={`Click to toggle ${device.name} ${nextStatus}`}
      aria-label={`Click to toggle ${device.roomName} ${device.name} ${nextStatus}`}
      disabled={isPending}
      onClick={() => onToggleDevice(device.id)}
      type="button"
    >
      {device.type === "fan" ? <CeilingFan isOn={isOn} /> : <LightOverlay isOn={isOn} />}
    </button>
  );
}

function RoomWiseDevicesStrip() {
  return (
    <section className="room-wise-devices-strip" aria-label="Room wise devices">
      <h3>Room Wise Devices</h3>
      <div className="room-wise-device-boxes">
        <div className="room-wise-device-box drawing">
          <strong>Drawing Room</strong>
          <span>2 Fans</span>
          <span>3 Lights</span>
        </div>
        <div className="room-wise-device-box work-one">
          <strong>Work Room 1</strong>
          <span>2 Fans</span>
          <span>3 Lights</span>
        </div>
        <div className="room-wise-device-box work-two">
          <strong>Work Room 2</strong>
          <span>2 Fans</span>
          <span>3 Lights</span>
        </div>
      </div>
    </section>
  );
}

function DeviceSummary() {
  return (
    <section className="floorplan-summary-card">
      <h3>Devices Summary</h3>
      <ul>
        <li>3 Rooms</li>
        <li>2 Fans per room</li>
        <li>3 Lights per room</li>
        <li>Total Fans: 6</li>
        <li>Total Lights: 9</li>
        <li>Total Devices: 15</li>
      </ul>
    </section>
  );
}

function FloorplanLegend() {
  return (
    <section className="floorplan-summary-card floorplan-legend-card">
      <h3>Legend</h3>
      <div className="floorplan-legend-list">
        <div className="floorplan-legend-item">
          <span className="legend-fan-symbol" aria-hidden="true">
            <CeilingFan isOn={false} />
          </span>
          <span>Fan (2 per room)</span>
        </div>
        <div className="floorplan-legend-item">
          <span className="legend-light-symbol" aria-hidden="true">
            <LightOverlay isOn />
          </span>
          <span>Light (3 per room)</span>
        </div>
        <div className="floorplan-legend-item">
          <span className="legend-door-symbol" aria-hidden="true" />
          <span>Door</span>
        </div>
        <div className="floorplan-legend-item">
          <span className="legend-window-symbol" aria-hidden="true" />
          <span>Window</span>
        </div>
      </div>
    </section>
  );
}

export default function OfficeLayout({ rooms, onToggleDevice, pendingDeviceIds }) {
  const devices = rooms.flatMap((room) => room.devices);

  return (
    <section className="layout-board-shell">
      <div className="layout-heading">
        <h1>Office Layout (Top View)</h1>
        <p>All rooms have 2 Fans and 3 Lights</p>
      </div>

      <div className="floorplan-live-grid">
        <div className="floorplan-image-card">
          <div className="floorplan-image-wrap">
            <img className="floorplan-base-image" src={floorplanImage} alt="Official office floorplan top view" />
            <div className="floorplan-live-layer" aria-label="Live device overlay">
              {devices.map((device) => (
                <DeviceOverlay
                  key={device.id}
                  device={device}
                  isPending={pendingDeviceIds.has(device.id)}
                  onToggleDevice={onToggleDevice}
                />
              ))}
            </div>
          </div>
          <RoomWiseDevicesStrip />
        </div>

        <aside className="floorplan-side-info">
          <FloorplanLegend />
          <DeviceSummary />
          <section className="floorplan-summary-card">
            <h3>Live Overlay</h3>
            <p>Lights glow when ON. Fans spin when ON. Every marker is driven by backend state.</p>
          </section>
        </aside>
      </div>
    </section>
  );
}
