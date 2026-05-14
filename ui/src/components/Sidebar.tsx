import { useEffect, useState } from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Settings, PlayCircle, FileText, Database, Beaker } from 'lucide-react';
import { fetchStatus } from '../api';

const Sidebar = () => {
  const [status, setStatus] = useState<any>({ running: false, progress: 0 });

  useEffect(() => {
    const poll = setInterval(() => {
      fetchStatus().then(setStatus).catch(() => {});
    }, 3000);
    return () => clearInterval(poll);
  }, []);

  return (
    <div className="sidebar">
      <div className="logo">
        <Beaker size={28} color="var(--accent-primary)" />
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
            <div style={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: status.running ? 'var(--warning)' : 'var(--success)' }} />
            <span style={{ fontSize: '0.9rem', fontWeight: 600 }}>{status.running ? 'Running' : 'Ready'}</span>
          </div>
          <div style={{ fontSize: '0.75rem', marginTop: '0.5rem', color: 'var(--text-muted)' }}>
            {status.progress}% complete
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
