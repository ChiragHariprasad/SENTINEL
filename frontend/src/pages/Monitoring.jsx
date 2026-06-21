import React from 'react';
import { Activity, Bell, Filter } from 'lucide-react';

const mockAlerts = [
  { id: 'ALT-101', vendor: 'Acme Cloud Services', type: 'Abnormal Access Pattern', severity: 'CRITICAL', time: '10 mins ago' },
  { id: 'ALT-102', vendor: 'Global Payment Gateway', type: 'Failed Compliance Check', severity: 'HIGH', time: '2 hours ago' },
  { id: 'ALT-103', vendor: 'Enterprise HR Solutions', type: 'SLA Breach (Uptime)', severity: 'MEDIUM', time: '1 day ago' },
];

export default function Monitoring() {
  return (
    <div className="monitoring-container">
      <div className="page-header mb-6 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-main flex items-center gap-2">
            <Bell className="text-[var(--warning)]" />
            Alerts & Monitoring
          </h1>
          <p className="text-muted text-sm mt-2">Real-time alerts and anomaly detections across the vendor ecosystem.</p>
        </div>
        <button className="btn btn-outline">
          <Filter size={18} /> Filter Alerts
        </button>
      </div>

      <div className="card">
        <div className="card-header flex justify-between items-center border-b border-[var(--border)] pb-4">
          <h2 className="card-title">Active Alerts</h2>
          <span className="badge badge-warning">{mockAlerts.length} Open</span>
        </div>
        <div className="divide-y divide-[var(--border)]">
          {mockAlerts.map(alert => (
            <div key={alert.id} className="p-4 flex items-center justify-between hover:bg-[var(--bg-surface-hover)] transition-colors">
              <div className="flex items-start gap-4">
                <div className={`p-2 rounded-full ${alert.severity === 'CRITICAL' ? 'bg-[rgba(239,68,68,0.2)] text-[var(--danger)]' : alert.severity === 'HIGH' ? 'bg-[rgba(245,158,11,0.2)] text-[var(--warning)]' : 'bg-[rgba(59,130,246,0.2)] text-[var(--primary)]'}`}>
                  <Activity size={20} />
                </div>
                <div>
                  <h3 className="font-semibold text-main">{alert.type}</h3>
                  <p className="text-sm text-muted mt-1">Vendor: <span className="font-medium text-main">{alert.vendor}</span></p>
                  <p className="text-xs text-muted mt-1 flex items-center gap-1"><span className="opacity-70">Detected {alert.time}</span></p>
                </div>
              </div>
              <div className="flex flex-col items-end gap-2">
                <span className={`badge ${alert.severity === 'CRITICAL' ? 'badge-danger' : alert.severity === 'HIGH' ? 'badge-warning' : 'badge-primary'}`}>
                  {alert.severity}
                </span>
                <button className="btn btn-ghost text-xs">Acknowledge</button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
