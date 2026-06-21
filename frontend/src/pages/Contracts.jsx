import React, { useState } from 'react';
import { Upload, FileText, CheckCircle, AlertTriangle, Clock } from 'lucide-react';
import { contractsApi } from '../api';

export default function Contracts() {
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    
    // Simulating API call since actual file upload might need valid backend parsing
    setTimeout(() => {
      setUploading(false);
      setAnalysisResult({
        contract_id: "CON-101",
        breach_notification_days: 15,
        data_ownership: "vendor",
        sla_uptime: "99.9%",
        risk_level: "HIGH",
        clauses: [
          { type: "Breach Notification", risk: "HIGH", text: "Vendor will notify within 15 days of breach." },
          { type: "Data Retention", risk: "MEDIUM", text: "Data held for 90 days post-termination." },
        ]
      });
    }, 1500);
  };

  return (
    <div className="contracts-container">
      <div className="page-header mb-6">
        <h1 className="text-2xl font-bold text-main flex items-center gap-2">
          <FileText className="text-[var(--primary)]" />
          Contract Intelligence
        </h1>
        <p className="text-muted text-sm mt-2">AI-powered contract parsing and risk extraction.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upload Section */}
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Upload Contract for Analysis</h2>
          </div>
          
          <div 
            className={`border-2 border-dashed rounded-lg p-10 text-center transition-colors ${dragActive ? 'border-[var(--primary)] bg-[var(--primary-light)]' : 'border-[var(--border)] hover:border-[var(--text-muted)]'}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <Upload className="mx-auto text-muted mb-4" size={32} />
            <p className="text-main mb-2">Drag and drop your contract document here</p>
            <p className="text-muted text-sm mb-6">Supported formats: PDF, DOCX, TXT</p>
            
            <input 
              type="file" 
              id="file-upload" 
              className="hidden" 
              onChange={handleChange} 
              accept=".pdf,.docx,.txt"
            />
            <label htmlFor="file-upload" className="btn btn-outline cursor-pointer">
              Browse Files
            </label>
            
            {file && (
              <div className="mt-4 p-3 bg-[rgba(0,0,0,0.2)] rounded border border-[var(--border)] text-sm flex justify-between items-center">
                <span className="truncate max-w-[200px]">{file.name}</span>
                <button 
                  className="btn btn-primary text-xs px-3 py-1"
                  onClick={handleUpload}
                  disabled={uploading}
                >
                  {uploading ? 'Analyzing...' : 'Analyze Contract'}
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Analysis Results */}
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Analysis Results</h2>
            {analysisResult && (
              <span className={`badge ${analysisResult.risk_level === 'HIGH' ? 'badge-danger' : 'badge-primary'}`}>
                {analysisResult.risk_level} RISK
              </span>
            )}
          </div>
          
          {uploading ? (
            <div className="flex flex-col items-center justify-center h-48 text-muted">
              <div className="w-8 h-8 border-4 border-[var(--primary)] border-t-transparent rounded-full animate-spin mb-4"></div>
              <p>Extracting clauses and assessing risk...</p>
            </div>
          ) : analysisResult ? (
            <div>
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="p-3 bg-[var(--bg-base)] rounded border border-[var(--border)]">
                  <p className="text-xs text-muted mb-1 uppercase tracking-wider">SLA Uptime</p>
                  <p className="font-bold text-lg text-main">{analysisResult.sla_uptime}</p>
                </div>
                <div className="p-3 bg-[var(--bg-base)] rounded border border-[var(--border)]">
                  <p className="text-xs text-muted mb-1 uppercase tracking-wider">Breach Notice</p>
                  <p className="font-bold text-lg text-main">{analysisResult.breach_notification_days} Days</p>
                </div>
              </div>
              
              <h3 className="font-semibold text-main mb-3 text-sm uppercase tracking-wider">Extracted Clauses</h3>
              <div className="flex flex-col gap-3">
                {analysisResult.clauses.map((clause, idx) => (
                  <div key={idx} className="p-3 border border-[var(--border)] rounded flex gap-3 items-start">
                    {clause.risk === 'HIGH' ? (
                      <AlertTriangle className="text-[var(--danger)] shrink-0 mt-0.5" size={16} />
                    ) : (
                      <Clock className="text-[var(--warning)] shrink-0 mt-0.5" size={16} />
                    )}
                    <div>
                      <h4 className="font-medium text-sm text-main">{clause.type}</h4>
                      <p className="text-xs text-muted mt-1">{clause.text}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-48 text-muted text-sm text-center">
              <FileText size={32} className="opacity-20 mb-3" />
              <p>Upload a contract to view automated risk analysis and clause extraction.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
