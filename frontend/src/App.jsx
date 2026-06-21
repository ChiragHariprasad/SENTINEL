import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import AppLayout from './layouts/AppLayout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Vendors from './pages/Vendors';
import Risk from './pages/Risk';
import Contracts from './pages/Contracts';
import Compliance from './pages/Compliance';
import Copilot from './pages/Copilot';
import Monitoring from './pages/Monitoring';
import Graph from './pages/Graph';

// Placeholder for other routes
const Placeholder = ({ title }) => (
  <div className="flex flex-col items-center justify-center h-full text-center p-8">
    <h1 className="text-3xl font-bold text-main mb-4">{title}</h1>
    <div className="p-8 border border-[var(--border)] rounded-lg bg-[var(--bg-surface)] w-full max-w-md">
      <div className="w-16 h-16 rounded-full bg-[rgba(59,130,246,0.1)] flex items-center justify-center mx-auto mb-4">
        <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="var(--primary)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m18 16 4-4-4-4"/><path d="m6 8-4 4 4 4"/><path d="m14.5 4-5 16"/></svg>
      </div>
      <p className="text-muted">This module is currently under construction. Please check back later.</p>
    </div>
  </div>
);

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        
        <Route path="/" element={<AppLayout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="vendors" element={<Vendors />} />
          <Route path="risk" element={<Risk />} />
          <Route path="contracts" element={<Contracts />} />
          <Route path="compliance" element={<Compliance />} />
          <Route path="monitoring" element={<Monitoring />} />
          <Route path="graph" element={<Graph />} />
          <Route path="copilot" element={<Copilot />} />
          <Route path="admin" element={<Placeholder title="Administration" />} />
        </Route>
        
        {/* Fallback route */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
