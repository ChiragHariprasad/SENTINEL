import React, { useState, useEffect } from 'react';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer,
  BarChart, Bar, Legend
} from 'recharts';
import { riskApi } from '../api';
import { AlertTriangle, Activity, Target } from 'lucide-react';

const mockRiskData = [
  { name: 'Jan', compliance: 85, security: 65, financial: 90 },
  { name: 'Feb', compliance: 88, security: 68, financial: 92 },
  { name: 'Mar', compliance: 82, security: 62, financial: 85 },
  { name: 'Apr', compliance: 89, security: 75, financial: 88 },
  { name: 'May', compliance: 92, security: 80, financial: 91 },
  { name: 'Jun', compliance: 95, security: 78, financial: 95 },
];

const riskFactors = [
  { factor: 'Data Privacy', score: 92, status: 'Critical' },
  { factor: 'Access Control', score: 85, status: 'High' },
  { factor: 'Incident Response', score: 70, status: 'Medium' },
  { factor: 'Compliance (SOC2)', score: 40, status: 'Low' },
];

export default function Risk() {
  const [loading, setLoading] = useState(false);

  return (
    <div className="risk-container">
      <div className="page-header mb-6 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-main flex items-center gap-2">
            <Activity className="text-[var(--primary)]" />
            Risk Intelligence
          </h1>
          <p className="text-muted text-sm mt-2">Deep-dive analytics into vendor risk vectors and historical trends.</p>
        </div>
        <button className="btn btn-primary" onClick={() => {}}>
          <Target size={18} /> Run Risk Assessment
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <div className="card lg:col-span-2">
          <div className="card-header">
            <h2 className="card-title">Risk Vector Trends</h2>
          </div>
          <div style={{ width: '100%', height: 300 }}>
            <ResponsiveContainer>
              <AreaChart data={mockRiskData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorSecurity" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="var(--danger)" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="var(--danger)" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorCompliance" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="var(--primary)" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="var(--primary)" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                <XAxis dataKey="name" stroke="var(--text-muted)" tick={{ fontSize: 12 }} />
                <YAxis stroke="var(--text-muted)" tick={{ fontSize: 12 }} />
                <RechartsTooltip contentStyle={{ backgroundColor: 'var(--bg-surface)', borderColor: 'var(--border)', borderRadius: '0.5rem' }} />
                <Area type="monotone" dataKey="security" stroke="var(--danger)" fillOpacity={1} fill="url(#colorSecurity)" />
                <Area type="monotone" dataKey="compliance" stroke="var(--primary)" fillOpacity={1} fill="url(#colorCompliance)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Top Risk Factors</h2>
          </div>
          <div className="flex flex-col gap-4">
            {riskFactors.map((rf, idx) => (
              <div key={idx} className="flex flex-col gap-1">
                <div className="flex justify-between text-sm">
                  <span className="text-main">{rf.factor}</span>
                  <span className="font-bold text-main">{rf.score}/100</span>
                </div>
                <div className="w-full bg-[rgba(0,0,0,0.2)] rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full ${rf.score >= 80 ? 'bg-[var(--danger)]' : rf.score >= 60 ? 'bg-[var(--warning)]' : 'bg-[var(--success)]'}`} 
                    style={{ width: `${rf.score}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
      
      <div className="card">
        <div className="card-header flex justify-between items-center">
          <h2 className="card-title">Anomaly Detection Engine</h2>
          <span className="badge badge-primary animate-pulse-glow">Active Monitoring</span>
        </div>
        <div className="p-4 border border-[var(--border)] rounded bg-[rgba(239,68,68,0.05)] flex items-start gap-4">
          <AlertTriangle className="text-[var(--danger)] mt-1 shrink-0" />
          <div>
            <h3 className="font-bold text-main">Elevated Risk Detected: Acme Cloud Services</h3>
            <p className="text-sm text-muted mt-1">Anomaly detected in recent access logs. High volume of data exfiltration identified from non-standard IP ranges.</p>
            <div className="mt-3 flex gap-2">
              <button className="btn btn-outline text-xs">View Investigation</button>
              <button className="btn btn-danger bg-[var(--danger)] text-white text-xs px-3 py-1 rounded">Isolate Vendor</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
