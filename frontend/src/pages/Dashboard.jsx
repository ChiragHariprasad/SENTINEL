import React from 'react';
import { 
  Building2, 
  AlertTriangle, 
  ShieldAlert, 
  FileWarning, 
  CheckCircle,
  TrendingUp,
  ArrowRight
} from 'lucide-react';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend
} from 'recharts';
import './Dashboard.css';

// Mock Data
const riskTrendData = [
  { name: 'Jan', risk: 65 },
  { name: 'Feb', risk: 68 },
  { name: 'Mar', risk: 62 },
  { name: 'Apr', risk: 75 },
  { name: 'May', risk: 80 },
  { name: 'Jun', risk: 78 },
  { name: 'Jul', risk: 89 },
];

const riskDistributionData = [
  { name: 'Low Risk', value: 150, color: '#10b981' },
  { name: 'Medium Risk', value: 85, color: '#f59e0b' },
  { name: 'High Risk', value: 15, color: '#ef4444' },
];

const criticalVendors = [
  { id: 'VEN-001', name: 'Acme Cloud Services', score: 92, status: 'Critical' },
  { id: 'VEN-042', name: 'Global Payment Gateway', score: 88, status: 'High' },
  { id: 'VEN-105', name: 'Enterprise HR Solutions', score: 85, status: 'High' },
];

const KpiCard = ({ title, value, icon: Icon, trend, trendUp, colorClass }) => (
  <div className="card kpi-card">
    <div className="kpi-header">
      <div className="kpi-title">{title}</div>
      <div className={`kpi-icon-wrapper ${colorClass}`}>
        <Icon size={20} />
      </div>
    </div>
    <div className="kpi-body">
      <div className="kpi-value">{value}</div>
      {trend && (
        <div className={`kpi-trend ${trendUp ? 'text-danger' : 'text-success'}`}>
          <TrendingUp size={16} className={!trendUp ? 'rotate-180' : ''} />
          <span>{trend}</span>
        </div>
      )}
    </div>
  </div>
);

export default function Dashboard() {
  return (
    <div className="dashboard-container">
      <div className="page-header mb-6">
        <h1 className="text-2xl font-bold text-main">Executive Risk Dashboard</h1>
        <p className="text-muted text-sm mt-2">Portfolio-wide vendor risk visibility and real-time intelligence.</p>
      </div>

      {/* KPI Row */}
      <div className="kpi-grid mb-6">
        <KpiCard title="Total Vendors" value="250" icon={Building2} trend="+12 this month" trendUp={false} colorClass="bg-primary-light text-primary" />
        <KpiCard title="Critical Risk Vendors" value="15" icon={AlertTriangle} trend="+3 this week" trendUp={true} colorClass="bg-danger-light text-danger" />
        <KpiCard title="Open Anomalies" value="8" icon={ShieldAlert} trend="-2 since yesterday" trendUp={false} colorClass="bg-warning-light text-warning" />
        <KpiCard title="Expiring Certs (30d)" value="12" icon={FileWarning} trend="+5 this month" trendUp={true} colorClass="bg-accent-light text-accent" />
      </div>

      {/* Charts Row */}
      <div className="charts-grid mb-6">
        <div className="card chart-card">
          <div className="card-header">
            <h2 className="card-title">Risk Trend Over Time</h2>
          </div>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={riskTrendData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorRisk" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                <XAxis dataKey="name" stroke="#94a3b8" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                <YAxis stroke="#94a3b8" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                <RechartsTooltip 
                  contentStyle={{ backgroundColor: '#151c2c', borderColor: '#334155', borderRadius: '0.5rem' }}
                  itemStyle={{ color: '#f8fafc' }}
                />
                <Area type="monotone" dataKey="risk" stroke="#ef4444" fillOpacity={1} fill="url(#colorRisk)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card chart-card">
          <div className="card-header">
            <h2 className="card-title">Risk Distribution</h2>
          </div>
          <div className="chart-container flex items-center justify-center">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={riskDistributionData}
                  cx="50%"
                  cy="50%"
                  innerRadius={80}
                  outerRadius={110}
                  paddingAngle={5}
                  dataKey="value"
                  stroke="none"
                >
                  {riskDistributionData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <RechartsTooltip 
                  contentStyle={{ backgroundColor: '#151c2c', borderColor: '#334155', borderRadius: '0.5rem' }}
                  itemStyle={{ color: '#f8fafc' }}
                />
                <Legend verticalAlign="bottom" height={36} wrapperStyle={{ fontSize: '14px', color: '#f8fafc' }}/>
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Actionable Row */}
      <div className="actionable-grid">
        <div className="card table-card">
          <div className="card-header">
            <h2 className="card-title flex items-center gap-2">
              <AlertTriangle size={18} className="text-danger" />
              Critical Vendors Requiring Action
            </h2>
            <button className="btn btn-ghost text-xs">View All</button>
          </div>
          <div className="table-responsive">
            <table className="sentinel-table">
              <thead>
                <tr>
                  <th>Vendor Name</th>
                  <th>Risk Score</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {criticalVendors.map(vendor => (
                  <tr key={vendor.id}>
                    <td className="font-medium">{vendor.name}</td>
                    <td>
                      <span className={`text-lg font-bold ${vendor.score >= 90 ? 'text-danger' : 'text-warning'}`}>
                        {vendor.score}
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${vendor.status === 'Critical' ? 'badge-danger' : 'badge-warning'}`}>
                        {vendor.status}
                      </span>
                    </td>
                    <td>
                      <button className="btn btn-outline text-xs">Investigate <ArrowRight size={14}/></button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
