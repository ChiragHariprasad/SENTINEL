import React, { useState, useEffect } from 'react';
import { ShieldCheck, Plus, CheckCircle, AlertTriangle, FileWarning } from 'lucide-react';
import { complianceApi } from '../api';

const mockCertifications = [
  { id: 'CERT-001', vendor: 'Acme Cloud Services', type: 'SOC 2 Type II', status: 'Active', expiry: '2026-12-31' },
  { id: 'CERT-002', vendor: 'Global Payment Gateway', type: 'PCI-DSS', status: 'Expiring Soon', expiry: '2026-07-15' },
  { id: 'CERT-003', vendor: 'Enterprise HR Solutions', type: 'ISO 27001', status: 'Expired', expiry: '2026-05-10' },
  { id: 'CERT-004', vendor: 'Apex Analytics', type: 'GDPR Compliance', status: 'Active', expiry: '2027-01-20' },
];

export default function Compliance() {
  const [certs, setCerts] = useState(mockCertifications);

  const getStatusIcon = (status) => {
    switch (status) {
      case 'Active': return <CheckCircle className="text-[var(--success)]" size={16} />;
      case 'Expiring Soon': return <AlertTriangle className="text-[var(--warning)]" size={16} />;
      case 'Expired': return <FileWarning className="text-[var(--danger)]" size={16} />;
      default: return null;
    }
  };

  return (
    <div className="compliance-container">
      <div className="page-header mb-6 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-main flex items-center gap-2">
            <ShieldCheck className="text-[var(--primary)]" />
            Compliance & Certifications
          </h1>
          <p className="text-muted text-sm mt-2">Track and manage vendor compliance documentation.</p>
        </div>
        <button className="btn btn-primary">
          <Plus size={18} /> Add Certification
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <div className="card bg-[var(--bg-surface)] border-l-4 border-l-[var(--success)]">
          <div className="text-sm text-muted uppercase tracking-wider mb-1">Active Certifications</div>
          <div className="text-3xl font-bold text-main">124</div>
        </div>
        <div className="card bg-[var(--bg-surface)] border-l-4 border-l-[var(--warning)]">
          <div className="text-sm text-muted uppercase tracking-wider mb-1">Expiring in 60 Days</div>
          <div className="text-3xl font-bold text-[var(--warning)]">12</div>
        </div>
        <div className="card bg-[var(--bg-surface)] border-l-4 border-l-[var(--danger)]">
          <div className="text-sm text-muted uppercase tracking-wider mb-1">Expired / Non-Compliant</div>
          <div className="text-3xl font-bold text-[var(--danger)]">3</div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Certification Registry</h2>
          <div className="flex gap-2">
            <select className="form-input py-1 text-sm bg-[var(--bg-base)]">
              <option>All Statuses</option>
              <option>Expiring Soon</option>
              <option>Expired</option>
            </select>
          </div>
        </div>

        <div className="table-responsive">
          <table className="sentinel-table w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-[var(--border)] text-muted text-sm uppercase tracking-wider">
                <th className="p-4 font-semibold">Vendor</th>
                <th className="p-4 font-semibold">Certification Type</th>
                <th className="p-4 font-semibold">Expiry Date</th>
                <th className="p-4 font-semibold">Status</th>
              </tr>
            </thead>
            <tbody>
              {certs.map(cert => (
                <tr key={cert.id} className="border-b border-[var(--border)] hover:bg-[var(--bg-surface-hover)] transition-colors">
                  <td className="p-4 font-medium text-main">{cert.vendor}</td>
                  <td className="p-4 text-muted">{cert.type}</td>
                  <td className="p-4 font-mono text-sm">{cert.expiry}</td>
                  <td className="p-4">
                    <div className="flex items-center gap-2">
                      {getStatusIcon(cert.status)}
                      <span className={
                        cert.status === 'Active' ? 'text-[var(--success)]' : 
                        cert.status === 'Expired' ? 'text-[var(--danger)] font-bold' : 
                        'text-[var(--warning)]'
                      }>{cert.status}</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
