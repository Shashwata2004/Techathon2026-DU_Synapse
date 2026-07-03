import React from "react";

export default function RoomCard({ room }) {
  return (
    <div className="room-card">
      <h3>{room.name}</h3>
      <div>
        <span>{room.fansOn} fans ON</span>
        <span>{room.lightsOn} lights ON</span>
      </div>
      <strong>{room.currentPower}W</strong>
    </div>
  );
}
