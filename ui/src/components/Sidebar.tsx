import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Settings, 
  PlayCircle, 
  Search, 
  FileText, 
  Database,
  Beaker
} from 'lucide-react';

const Sidebar = () => {
  return (
    <div className="sidebar">
      <div className="logo">
        <Beaker size={28} color="#6366f1" />
        <span>ResearchFlow</span>
      </div>
      
      <nav>
        <NavLink to="/" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <LayoutDashboard size={20} />
          <span>Dashboard</span>
        </NavLink>
        
        <NavLink to="/config" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <Settings size={20} />
          <span>Configuration</span>
        </NavLink>
        
        <NavLink to="/workflow" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <PlayCircle size={20} />
          <span>Workflow</span>
        </NavLink>
        
        <NavLink to="/explorer" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <Database size={20} />
          <span>Data Explorer</span>
        </NavLink>
        
        <NavLink to="/results" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <FileText size={20} />
          <span>Final Results</span>
        </NavLink>
      </nav>
      
      <div style={{ marginTop: 'auto' }}>
        <div className="card" style={{ padding: '1rem', marginBottom: 0, background: 'var(--bg-tertiary)' }}>
          <p style={{ fontSize: '0.8rem', marginBottom: '0.5rem' }}>Pipeline Status</p>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <div style={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: 'var(--success)' }}></div>
            <span style={{ fontSize: '0.9rem', fontWeight: 600 }}>Ready</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
