import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Users, 
  ShieldAlert, 
  FileText, 
  CheckCircle, 
  Activity, 
  Share2, 
  Bot, 
  Settings 
} from 'lucide-react';
import './Sidebar.css';

const navItems = [
  { icon: LayoutDashboard, label: 'Dashboard', path: '/dashboard' },
  { icon: Users, label: 'Vendor Registry', path: '/vendors' },
  { icon: ShieldAlert, label: 'Risk Intelligence', path: '/risk' },
  { icon: FileText, label: 'Contracts', path: '/contracts' },
  { icon: CheckCircle, label: 'Compliance', path: '/compliance' },
  { icon: Activity, label: 'Monitoring', path: '/monitoring' },
  { icon: Share2, label: 'Knowledge Graph', path: '/graph' },
  { icon: Bot, label: 'AI Copilot', path: '/copilot' },
  { icon: Settings, label: 'Administration', path: '/admin' },
];

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <div className="logo-icon">
          <ShieldAlert size={24} className="text-primary" />
        </div>
        <span className="logo-text">SENTINEL</span>
      </div>
      
      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <NavLink 
            key={item.path} 
            to={item.path} 
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            <item.icon size={20} />
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
