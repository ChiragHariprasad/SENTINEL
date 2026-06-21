import React, { useState, useEffect } from 'react';
import { Building2, Search, Plus, MoreVertical, Filter, ArrowRight } from 'lucide-react';
import { vendorsApi } from '../api';

export default function Vendors() {
  const [vendors, setVendors] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Mock data for initial render or fallback
    const mockVendors = [
      { id: 'VEN-001', name: 'Acme Cloud Services', type: 'Cloud Provider', risk_tier: 'RED', score: 92 },
      { id: 'VEN-042', name: 'Global Payment Gateway', type: 'Financial Services', risk_tier: 'YELLOW', score: 65 },
      { id: 'VEN-105', name: 'Enterprise HR Solutions', type: 'SaaS', risk_tier: 'GREEN', score: 25 },
      { id: 'VEN-112', name: 'Apex Analytics', type: 'Data Broker', risk_tier: 'RED', score: 88 },
      { id: 'VEN-204', name: 'Nexus Supply Chain', type: 'Logistics', risk_tier: 'GREEN', score: 15 }
    ];

    vendorsApi.getVendors()
      .then(res => {
        if (res.data && res.data.items && res.data.items.length > 0) {
          setVendors(res.data.items);
        } else {
          setVendors(mockVendors);
        }
      })
      .catch(err => {
        console.error("Failed to fetch vendors", err);
        setVendors(mockVendors); // Fallback to mock data
      })
      .finally(() => setLoading(false));
  }, []);

  const getRiskBadgeClass = (tier) => {
    switch (tier) {
      case 'RED': return 'badge-danger';
      case 'YELLOW': return 'badge-warning';
      case 'GREEN': return 'badge-success';
      default: return 'badge-primary';
    }
  };

  return (
    <div className="vendors-container">
      <div className="page-header mb-6 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-main">Vendor Registry</h1>
          <p className="text-muted text-sm mt-2">Manage and monitor your third-party ecosystem.</p>
        </div>
        <button className="btn btn-primary">
          <Plus size={18} /> Add Vendor
        </button>
      </div>

      <div className="card mb-6">
        <div className="flex gap-4 items-center mb-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted" size={18} />
            <input type="text" className="form-input pl-10 w-full" placeholder="Search vendors by name or ID..." />
          </div>
          <button className="btn btn-outline">
            <Filter size={18} /> Filter
          </button>
        </div>

        <div className="table-responsive">
          <table className="sentinel-table w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-[var(--border)] text-muted text-sm uppercase tracking-wider">
                <th className="p-4 font-semibold">Vendor Name</th>
                <th className="p-4 font-semibold">Type</th>
                <th className="p-4 font-semibold">Risk Tier</th>
                <th className="p-4 font-semibold">Risk Score</th>
                <th className="p-4 font-semibold">Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="5" className="p-4 text-center text-muted">Loading vendors...</td>
                </tr>
              ) : vendors.map(vendor => (
                <tr key={vendor.id} className="border-b border-[var(--border)] hover:bg-[var(--bg-surface-hover)] transition-colors">
                  <td className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-[var(--primary-light)] text-[var(--primary)] flex items-center justify-center font-bold">
                        {vendor.name.charAt(0)}
                      </div>
                      <div>
                        <div className="font-medium text-main">{vendor.name}</div>
                        <div className="text-xs text-muted">{vendor.id}</div>
                      </div>
                    </div>
                  </td>
                  <td className="p-4 text-sm text-muted">{vendor.type}</td>
                  <td className="p-4">
                    <span className={`badge ${getRiskBadgeClass(vendor.risk_tier)}`}>
                      {vendor.risk_tier}
                    </span>
                  </td>
                  <td className="p-4">
                    <span className={`font-bold ${vendor.score >= 80 ? 'text-[var(--danger)]' : vendor.score >= 50 ? 'text-[var(--warning)]' : 'text-[var(--success)]'}`}>
                      {vendor.score}
                    </span>
                  </td>
                  <td className="p-4">
                    <button className="btn btn-ghost p-2">
                      <MoreVertical size={18} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="p-4 border-t border-[var(--border)] flex justify-between items-center text-sm text-muted">
          <div>Showing 1 to {vendors.length} of {vendors.length} entries</div>
          <div className="flex gap-2">
            <button className="btn btn-outline text-xs px-3 py-1">Previous</button>
            <button className="btn btn-primary text-xs px-3 py-1">Next</button>
          </div>
        </div>
      </div>
    </div>
  );
}
