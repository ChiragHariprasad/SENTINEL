import React from 'react';
import { Network, Search, Maximize2 } from 'lucide-react';

export default function Graph() {
  return (
    <div className="graph-container h-[calc(100vh-140px)] flex flex-col">
      <div className="page-header mb-4 shrink-0 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-main flex items-center gap-2">
            <Network className="text-[var(--accent)]" />
            Knowledge Graph
          </h1>
          <p className="text-muted text-sm mt-1">Interactive visualization of vendor relationships and data flow.</p>
        </div>
        <div className="flex gap-2">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted" size={16} />
            <input type="text" className="form-input py-1.5 pl-9 text-sm" placeholder="Search nodes..." />
          </div>
          <button className="btn btn-outline p-2"><Maximize2 size={16} /></button>
        </div>
      </div>

      <div className="card flex-1 p-0 overflow-hidden relative bg-[#0f141e] flex items-center justify-center border border-[var(--border)]">
        {/* Mock representation of a graph */}
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0MCIgaGVpZ2h0PSI0MCI+CgkJPGNpcmNsZSBjeD0iMjAiIGN5PSIyMCIgcj0iMSIgZmlsbD0icmdiYSgyNTUsIDI1NSwgMjU1LCAwLjA1KSIvPgoJPC9zdmc+')] opacity-50"></div>
        
        <div className="z-10 text-center flex flex-col items-center">
          <div className="w-20 h-20 rounded-full border-2 border-[var(--accent)] flex items-center justify-center bg-[var(--bg-surface)] text-[var(--accent)] mb-4 animate-pulse-glow shadow-[0_0_20px_rgba(139,92,246,0.3)]">
            <Network size={32} />
          </div>
          <h2 className="text-xl font-bold text-main mb-2">Graph Visualization Server Connected</h2>
          <p className="text-muted text-sm max-w-md">The interactive node-link diagram is currently loading telemetry data. In production, this uses D3.js or react-force-graph to render the 4th-party ecosystem.</p>
        </div>

        {/* Mock Node Connections purely for aesthetic in the placeholder */}
        <svg className="absolute inset-0 w-full h-full pointer-events-none opacity-20" xmlns="http://www.w3.org/2000/svg">
          <line x1="50%" y1="50%" x2="20%" y2="30%" stroke="var(--accent)" strokeWidth="1" />
          <line x1="50%" y1="50%" x2="80%" y2="40%" stroke="var(--primary)" strokeWidth="1" />
          <line x1="50%" y1="50%" x2="70%" y2="80%" stroke="var(--success)" strokeWidth="1" />
          <line x1="50%" y1="50%" x2="30%" y2="70%" stroke="var(--danger)" strokeWidth="1" />
          
          <circle cx="20%" cy="30%" r="6" fill="var(--bg-surface)" stroke="var(--accent)" strokeWidth="2" />
          <circle cx="80%" cy="40%" r="8" fill="var(--bg-surface)" stroke="var(--primary)" strokeWidth="2" />
          <circle cx="70%" cy="80%" r="5" fill="var(--bg-surface)" stroke="var(--success)" strokeWidth="2" />
          <circle cx="30%" cy="70%" r="7" fill="var(--bg-surface)" stroke="var(--danger)" strokeWidth="2" />
        </svg>
      </div>
    </div>
  );
}
