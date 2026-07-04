import React from "react";
import { ClipboardList, Lightbulb, Power, TrendingUp } from "lucide-react";

function formatRoomList(rooms) {
  if (!rooms.length) return "No active room";
  if (rooms.length === 1) return rooms[0];
  if (rooms.length === 2) return `${rooms[0]} and ${rooms[1]}`;
  return `${rooms.slice(0, -1).join(", ")}, and ${rooms[rooms.length - 1]}`;
}

function getTopRooms(state) {
  const entries = Object.entries(state.roomWisePower || {});
  if (!entries.length) return { rooms: [], watts: 0 };
  const watts = Math.max(...entries.map(([, value]) => value));
  if (watts <= 0) return { rooms: [], watts: 0 };
  return {
    rooms: entries.filter(([, value]) => value === watts).map(([room]) => room),
    watts,
  };
}

function countActiveTypes(devices) {
  return devices.reduce(
    (counts, device) => {
      if (device.status === "ON") {
        if (device.type === "fan") counts.fans += 1;
        if (device.type === "light") counts.lights += 1;
      }
      return counts;
    },
    { fans: 0, lights: 0 },
  );
}

function getRoomCount(state) {
  if (state.rooms?.length) return state.rooms.length;
  return Object.keys(state.roomWisePower || {}).length;
}

function getDevicesForRooms(state, roomNames) {
  if (!roomNames.length) return [];

  const topRoomNames = new Set(roomNames);
  const rooms = state.rooms || [];
  return rooms
    .filter((room) => topRoomNames.has(room.name) || topRoomNames.has(room.id))
    .flatMap((room) => room.devices || []);
}

function formatTopConsumer(top, roomCount) {
  if (!top.rooms.length) return "Office is idle. Current usage: 0W.";
  if (top.rooms.length === roomCount && roomCount > 1) {
    return `All ${roomCount} rooms are tied for highest usage at ${top.watts}W.`;
  }
  if (top.rooms.length > 1) {
    return `${formatRoomList(top.rooms)} are tied for highest usage at ${top.watts}W.`;
  }
  return `${top.rooms[0]} is currently highest at ${top.watts}W.`;
}

function formatTime(value) {
  return new Intl.DateTimeFormat(undefined, {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  }).format(new Date(value));
}

export function SimulatorToggle({ simulatorStatus, isPending, onToggle }) {
  const enabled = simulatorStatus?.enabled;
  const interval = simulatorStatus?.intervalSeconds;
  return (
    <button className={`simulator-toggle ${enabled ? "on" : "off"}`} type="button" onClick={onToggle} disabled={isPending}>
      <Power size={16} />
      <span>Simulator {enabled ? "ON" : "OFF"}</span>
      <strong>{enabled ? `every ${interval}s` : "manual mode"}</strong>
    </button>
  );
}

export function TopConsumerInsight({ state }) {
  const top = getTopRooms(state);
  const roomCount = getRoomCount(state);
  const devices = getDevicesForRooms(state, top.rooms);
  const counts = countActiveTypes(devices);

  return (
    <section className="panel insight-panel">
      <div className="panel-title">
        <h2>Top Consumer</h2>
        <TrendingUp size={20} />
      </div>
      {top.rooms.length ? (
        <>
          <p>{formatTopConsumer(top, roomCount)}</p>
          <small>
            Top room load mix: {counts.fans} fans and {counts.lights} lights ON.
          </small>
        </>
      ) : (
        <p>Office is idle. Current usage: 0W.</p>
      )}
    </section>
  );
}

export function EnergyRecommendationPanel({ state }) {
  const top = getTopRooms(state);
  const devices = state.devices || state.rooms.flatMap((room) => room.devices);
  const counts = countActiveTypes(devices);
  let recommendation = "Office is already efficient. All devices are OFF.";

  if (state.activeAlerts.length) {
    const rooms = [...new Set(state.activeAlerts.map((alert) => alert.roomId.replaceAll("-", " ")))];
    recommendation = `Fix alert rooms first: ${rooms.join(", ")}. Check devices that are still ON.`;
  } else if (top.watts >= 120) {
    recommendation = `${formatRoomList(top.rooms)} ${top.rooms.length > 1 ? "are" : "is"} drawing ${top.watts}W. Check whether those fans and lights are still needed.`;
  } else if (counts.lights >= 4) {
    recommendation = `${counts.lights} lights are ON. Turn off unused lights in empty rooms.`;
  } else if (state.activeDeviceCount > 0) {
    recommendation = "Usage is moderate. Keep watching rooms with active fans before closing time.";
  }

  return (
    <section className="panel recommendation-panel">
      <div className="panel-title">
        <h2>Recommendation</h2>
        <Lightbulb size={20} />
      </div>
      <p>{recommendation}</p>
    </section>
  );
}

export function ActivityFeed({ events = [] }) {
  return (
    <section className="panel activity-panel">
      <div className="panel-title">
        <h2>Recent Activity</h2>
        <ClipboardList size={20} />
      </div>
      {events.length === 0 ? (
        <p className="panel-empty">No recent device changes yet.</p>
      ) : (
        <div className="activity-list">
          {events.slice(0, 8).map((event) => (
            <div className="activity-row" key={event.id}>
              <span>{formatTime(event.timestamp)}</span>
              <p>{event.message}</p>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
