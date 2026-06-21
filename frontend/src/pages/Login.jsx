import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ShieldAlert, Lock, Mail } from 'lucide-react';
import './Login.css';

export default function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = (e) => {
    e.preventDefault();
    setIsLoading(true);
    // Simulate API call
    setTimeout(() => {
      setIsLoading(false);
      navigate('/dashboard');
    }, 1000);
  };

  return (
    <div className="login-container">
      <div className="login-glass-panel">
        <div className="login-header">
          <div className="login-logo">
            <ShieldAlert size={40} className="text-primary animate-pulse-glow rounded-full" style={{ borderRadius: '50%' }} />
          </div>
          <h1 className="login-title">SENTINEL</h1>
          <p className="login-subtitle">Security Evaluation & Networked Third-Party Intelligence Engine</p>
        </div>

        <form onSubmit={handleLogin} className="login-form">
          <div className="form-group relative-icon">
            <label className="form-label">Email Address</label>
            <div className="input-wrapper">
              <Mail size={18} className="input-icon" />
              <input 
                type="email" 
                className="form-input with-icon" 
                placeholder="analyst@company.com" 
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
          </div>

          <div className="form-group relative-icon">
            <label className="form-label">Password</label>
            <div className="input-wrapper">
              <Lock size={18} className="input-icon" />
              <input 
                type="password" 
                className="form-input with-icon" 
                placeholder="••••••••" 
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
          </div>

          <div className="login-actions flex justify-between items-center mb-6 text-sm">
            <label className="flex items-center gap-2 text-muted cursor-pointer">
              <input type="checkbox" className="accent-primary" />
              Remember me
            </label>
            <a href="#" className="text-primary hover:text-primary-hover">Forgot Password?</a>
          </div>

          <button 
            type="submit" 
            className="btn btn-primary w-full" 
            disabled={isLoading}
          >
            {isLoading ? 'Authenticating...' : 'Sign In'}
          </button>
        </form>

        <div className="login-footer text-center mt-6 text-xs text-muted">
          Protected by AES-256 Encryption & Zero-Trust Architecture
        </div>
      </div>
    </div>
  );
}
