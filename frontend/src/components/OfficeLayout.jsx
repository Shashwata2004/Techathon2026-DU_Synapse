import React from "react";
import { Fan, Lightbulb } from "lucide-react";

const DEVICE_POSITIONS = {
  "drawing-room": {
    "light-1": "drawing-light-left",
    "fan-1": "drawing-fan-top",
    "light-2": "drawing-light-right",
    "fan-2": "drawing-fan-bottom",
    "light-3": "drawing-light-bottom",
  },
  "work-room-1": {
    "light-1": "work1-light-left",
    "fan-1": "work1-fan-top",
    "light-2": "work1-light-right",
    "fan-2": "work1-fan-bottom",
    "light-3": "work1-light-bottom",
  },
  "work-room-2": {
    "light-1": "work2-light-left",
    "fan-1": "work2-fan-top",
    "light-2": "work2-light-right",
    "fan-2": "work2-fan-bottom",
    "light-3": "work2-light-bottom",
  },
};

function getDeviceNumber(device) {
  return device.id.split("-").at(-1);
}

function DeviceMarker({ device, className }) {
  const isOn = device.status === "ON";
  const markerClassName = `layout-device ${device.type} ${isOn ? "is-on" : "is-off"} ${className}`;
  const Icon = device.type === "fan" ? Fan : Lightbulb;

  return (
    <div className={markerClassName} title={`${device.roomName} ${device.name}: ${device.status}`}>
      <Icon size={device.type === "fan" ? 34 : 26} strokeWidth={device.type === "fan" ? 2.4 : 2.2} />
    </div>
  );
}

function RoomDevices({ room }) {
  return room.devices.map((device) => {
    const key = `${device.type}-${getDeviceNumber(device)}`;
    return <DeviceMarker key={device.id} device={device} className={DEVICE_POSITIONS[room.id][key]} />;
  });
}

function Desk({ className = "" }) {
  return (
    <div className={`desk ${className}`}>
      <span className="monitor" />
      <span className="keyboard" />
      <span className="chair" />
      <span className="plant-pot" />
    </div>
  );
}

function Plant({ className = "" }) {
  return <span className={`layout-plant ${className}`} aria-hidden="true" />;
}

function Door({ className = "" }) {
  return <span className={`layout-door ${className}`} aria-hidden="true" />;
}

function Window({ className = "" }) {
  return <span className={`layout-window ${className}`} aria-hidden="true" />;
}

function LegendItem({ type, label }) {
  return (
    <div className="legend-item">
      <span className={`legend-symbol ${type}`}>
        {type === "fan" ? <Fan size={28} /> : type === "light" ? <Lightbulb size={22} /> : null}
      </span>
      <span>{label}</span>
    </div>
  );
}

export default function OfficeLayout({ rooms }) {
  const roomsById = Object.fromEntries(rooms.map((room) => [room.id, room]));

  return (
    <section className="layout-board-shell">
      <div className="layout-heading">
        <h1>Office Layout (Top View)</h1>
        <p>All rooms have 2 Fans and 3 Lights</p>
      </div>

      <div className="layout-stage">
        <div className="layout-plan-area">
          <div className="floorplan">
            <Window className="window-top drawing-window" />
            <Window className="window-top work1-window" />
            <Window className="window-top work2-window" />
            <Window className="window-left" />
            <Window className="window-right" />
            <Window className="window-corridor-right" />

            <div className={`layout-room drawing-room ${roomsById["drawing-room"].activeAlerts.length ? "has-alert" : ""}`}>
              <Plant className="plant-drawing-top" />
              <Plant className="plant-drawing-bottom" />
              <div className="sofa" />
              <div className="armchair" />
              <div className="rug" />
              <div className="coffee-table" />
              <h2>Drawing Room</h2>
              <strong>{roomsById["drawing-room"].currentPower}W</strong>
              <RoomDevices room={roomsById["drawing-room"]} />
            </div>

            <div className={`layout-room work-room work-room-1 ${roomsById["work-room-1"].activeAlerts.length ? "has-alert" : ""}`}>
              <h2>Work Room 1</h2>
              <strong>{roomsById["work-room-1"].currentPower}W</strong>
              <Desk className="desk-a" />
              <Desk className="desk-b" />
              <Desk className="desk-c" />
              <RoomDevices room={roomsById["work-room-1"]} />
            </div>

            <div className={`layout-room work-room work-room-2 ${roomsById["work-room-2"].activeAlerts.length ? "has-alert" : ""}`}>
              <h2>Work Room 2</h2>
              <strong>{roomsById["work-room-2"].currentPower}W</strong>
              <Desk className="desk-a" />
              <Desk className="desk-b" />
              <Desk className="desk-c" />
              <RoomDevices room={roomsById["work-room-2"]} />
            </div>

            <div className="corridor">
              <Plant className="plant-corridor-left" />
              <Plant className="plant-corridor-right" />
              <div className="water-cooler" />
              <div className="entry-arrow">Entry</div>
            </div>

            <Door className="door-drawing" />
            <Door className="door-work1" />
            <Door className="door-work2" />
            <Door className="door-entry" />
          </div>

          <div className="room-wise-strip">
            <h3>Room Wise Devices</h3>
            <div>
              {rooms.map((room) => (
                <span key={room.id}>
                  <strong>{room.name}</strong>
                  2 Fans
                  <br />3 Lights
                </span>
              ))}
            </div>
          </div>
        </div>

        <aside className="layout-info">
          <section className="layout-info-card">
            <h3>Legend</h3>
            <LegendItem type="fan" label="Fan (2 per room)" />
            <LegendItem type="light" label="Light (3 per room)" />
            <LegendItem type="door" label="Door" />
            <LegendItem type="window" label="Window" />
          </section>

          <section className="layout-info-card">
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

          <section className="layout-info-card">
            <h3>Room Usage</h3>
            <ul>
              <li>Drawing Room - Waiting area</li>
              <li>Work Room 1 - Employees</li>
              <li>Work Room 2 - Employees</li>
            </ul>
          </section>
        </aside>
      </div>
    </section>
  );
}
