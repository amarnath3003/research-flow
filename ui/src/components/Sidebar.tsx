import { useEffect, useState } from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Settings, PlayCircle, FileText, Database, Beaker } from 'lucide-react';
import { fetchStatus } from '../api';

const Sidebar = () => {
  const [status, setStatus] = useState<any>({ running: false, progress: 0 });
  const [connected, setConnected] = useState<boolean>(true);

  useEffect(() => {
    const check = () => {
      fetchStatus()
        .then(data => {
          setStatus(data);
          setConnected(true);
        })
        .catch(() => {
          setConnected(false);
        });
    };
    check();
    const poll = setInterval(check, 3000);
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
        <div className="card" style={{ padding: '1.25rem', marginBottom: 0, background: 'var(--bg-tertiary)', border: !connected ? '1px solid var(--error)' : '1px solid var(--border-color)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)' }}>System</span>
            <div style={{ 
              width: 10, height: 10, borderRadius: '50%', 
              backgroundColor: !connected ? 'var(--error)' : status.running ? 'var(--warning)' : 'var(--success)',
              boxShadow: connected ? '0 0 10px var(--success)' : 'none'
            }} className={status.running ? 'pulse' : ''} />
          </div>
          
          <div style={{ marginBottom: '0.5rem' }}>
            <p style={{ margin: 0, fontSize: '0.9rem', fontWeight: 600 }}>
              {!connected ? 'Backend Offline' : status.running ? 'Pipeline Active' : 'Backend Ready'}
            </p>
            <p style={{ margin: 0, fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              {!connected ? 'Check server.py' : status.currentStage || 'Idle'}
            </p>
          </div>

          {connected && (
            <div style={{ marginTop: '0.75rem' }}>
              <div style={{ height: 4, background: 'rgba(255,255,255,0.1)', borderRadius: 2, overflow: 'hidden' }}>
                <div style={{ height: '100%', background: 'var(--accent-primary)', width: `${status.progress}%`, transition: 'width 0.5s ease' }} />
              </div>
              <p style={{ margin: '0.35rem 0 0 0', fontSize: '0.7rem', color: 'var(--text-muted)', textAlign: 'right' }}>
                {status.progress}% complete
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
