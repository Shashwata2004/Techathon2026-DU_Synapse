import React from "react";
import { AlertTriangle, CheckCircle2 } from "lucide-react";

function formatTime(value) {
  return new Intl.DateTimeFormat(undefined, {
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

export default function AlertsPanel({ alerts }) {
  return (
    <section className="panel">
      <div className="panel-title">
        <h2>Active Alerts</h2>
        <span>{alerts.length}</span>
      </div>
      {alerts.length === 0 ? (
        <div className="empty-alerts">
          <CheckCircle2 size={24} />
          <p>All good. No active alerts right now.</p>
        </div>
      ) : (
        <div className="alert-list">
          {alerts.map((alert) => (
            <div key={alert.id} className="alert-row">
              <AlertTriangle size={20} />
              <div>
                <span>{formatTime(alert.createdAt)}</span>
                <p>{alert.message}</p>
                <small>{alert.affectedDevices.length} affected devices</small>
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
