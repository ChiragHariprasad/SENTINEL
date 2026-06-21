import React from 'react';
import { Bell, Search, User, LogOut } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import './Header.css';

export default function Header() {
  const navigate = useNavigate();

  const handleLogout = () => {
    // Basic logout simulation for now
    navigate('/login');
  };

  return (
    <header className="header">
      <div className="header-search">
        <Search size={18} className="search-icon" />
        <input 
          type="text" 
          placeholder="Search vendors, contracts, or risks..." 
          className="search-input"
        />
      </div>
      
      <div className="header-actions">
        <button className="icon-btn animate-pulse-glow" aria-label="Notifications">
          <Bell size={20} />
          <span className="badge-indicator"></span>
        </button>
        
        <div className="user-profile">
          <div className="avatar">
            <User size={20} />
          </div>
          <div className="user-info">
            <span className="user-name">Admin User</span>
            <span className="user-role">Administrator</span>
          </div>
        </div>

        <button className="icon-btn logout-btn" onClick={handleLogout} aria-label="Logout">
          <LogOut size={20} />
        </button>
      </div>
    </header>
  );
}
