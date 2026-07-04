import React, { useState } from "react";
import { AlertTriangle, CheckCircle2 } from "lucide-react";

function formatTime(value) {
  return new Intl.DateTimeFormat(undefined, {
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

export default function AlertsPanel({ alerts }) {
  const [acknowledgedIds, setAcknowledgedIds] = useState(() => new Set());

  function acknowledge(alertId) {
    setAcknowledgedIds((current) => new Set(current).add(alertId));
  }

  return (
    <section className="panel">
      <div className="panel-title">
        <h2>Active Alerts</h2>
        <span>{alerts.length}</span>
      </div>
      {alerts.length === 0 ? (
        <div className="empty-alerts">
          <CheckCircle2 size={24} />
          <p>No active alerts. Office is operating normally.</p>
        </div>
      ) : (
        <div className="alert-list">
          {alerts.map((alert) => {
            const acknowledged = acknowledgedIds.has(alert.id);
            return (
              <div key={alert.id} className={`alert-row ${acknowledged ? "is-acknowledged" : ""}`}>
                <AlertTriangle size={20} />
                <div>
                  <div className="alert-meta">
                    <span>{formatTime(alert.createdAt)}</span>
                    <strong>{alert.severity}</strong>
                  </div>
                  <p>{alert.message}</p>
                  <small>
                    Room: {alert.roomId} · {alert.affectedDevices.length} affected devices
                  </small>
                  {alert.affectedDevices.length ? <small>{alert.affectedDevices.join(", ")}</small> : null}
                </div>
                <button type="button" onClick={() => acknowledge(alert.id)} disabled={acknowledged}>
                  {acknowledged ? "Seen" : "Acknowledge"}
                </button>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}
