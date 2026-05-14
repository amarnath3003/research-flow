import { useEffect, useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { LayoutDashboard, Settings, PlayCircle, Database, FileText, Beaker, FolderKanban, ChevronDown } from 'lucide-react';
import { fetchStatus } from '../api';
import { useProjects } from '../context/ProjectContext';

const Sidebar = () => {
  const { projects, activeProject, setActive } = useProjects();
  const [status, setStatus] = useState<any>({ running: false, progress: 0 });
  const [showSelector, setShowSelector] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (!activeProject) return;
    const poll = setInterval(() => {
      fetchStatus(activeProject.id).then(setStatus).catch(() => {});
    }, 4000);
    fetchStatus(activeProject.id).then(setStatus).catch(() => {});
    return () => clearInterval(poll);
  }, [activeProject]);

  return (
    <div className="sidebar">
      <div className="logo" style={{ cursor: 'pointer' }} onClick={() => navigate('/projects')}>
        <Beaker size={28} color="var(--accent-primary)" />
        <span>ResearchFlow</span>
      </div>

      {/* Project Selector */}
      <div style={{ position: 'relative', marginBottom: '2rem' }}>
        <div
          onClick={() => setShowSelector(!showSelector)}
          style={{
            display: 'flex', alignItems: 'center', gap: '0.6rem', cursor: 'pointer',
            padding: '0.75rem 1rem', borderRadius: '4px', background: 'var(--bg-secondary)',
            border: '1px solid var(--border-color)', fontSize: '0.9rem',
            boxShadow: 'var(--card-shadow)',
          }}
        >
          <FolderKanban size={16} color="var(--accent-primary)" />
          <span style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', fontWeight: 500 }}>
            {activeProject?.name ?? 'Select Project'}
          </span>
          <ChevronDown size={14} color="var(--text-muted)" />
        </div>
        {showSelector && (
          <>
            <div style={{ position: 'fixed', inset: 0, zIndex: 98 }} onClick={() => setShowSelector(false)} />
            <div style={{
              position: 'absolute', top: '100%', left: 0, right: 0, zIndex: 99,
              background: 'var(--bg-secondary)', border: '1px solid var(--border-color)',
              borderRadius: '4px', marginTop: '4px', overflow: 'hidden',
              boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
            }}>
              {projects.map((p) => (
                <div
                  key={p.id}
                  onClick={() => { setActive(p); setShowSelector(false); }}
                  style={{
                    padding: '0.75rem 1rem', cursor: 'pointer', fontSize: '0.85rem',
                    background: p.id === activeProject?.id ? 'var(--bg-tertiary)' : 'transparent',
                    color: p.id === activeProject?.id ? 'var(--accent-primary)' : 'var(--text-primary)',
                    borderBottom: '1px solid var(--border-color)',
                    fontWeight: p.id === activeProject?.id ? 600 : 400,
                  }}
                >
                  {p.name} {p.isDefault ? '★' : ''}
                </div>
              ))}
              <div
                onClick={() => { setShowSelector(false); navigate('/projects'); }}
                style={{ padding: '0.75rem 1rem', cursor: 'pointer', fontSize: '0.8rem', color: 'var(--accent-primary)', textAlign: 'center', fontWeight: 600, background: 'var(--bg-tertiary)' }}
              >
                + Manage Projects
              </div>
            </div>
          </>
        )}
      </div>

      <nav>
        <NavLink to={`/${activeProject?.id ?? ''}/dashboard`} className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <LayoutDashboard size={18} /><span>Dashboard</span>
        </NavLink>
        <NavLink to={`/${activeProject?.id ?? ''}/config`} className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <Settings size={18} /><span>Configuration</span>
        </NavLink>
        <NavLink to={`/${activeProject?.id ?? ''}/workflow`} className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <PlayCircle size={18} /><span>Workflow</span>
        </NavLink>
        <NavLink to={`/${activeProject?.id ?? ''}/explorer`} className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <Database size={18} /><span>Data Explorer</span>
        </NavLink>
        <NavLink to={`/${activeProject?.id ?? ''}/results`} className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <FileText size={18} /><span>Final Results</span>
        </NavLink>
      </nav>

      <div style={{ marginTop: 'auto' }}>
        <div className="card" style={{ padding: '1.25rem', marginBottom: 0, background: 'var(--bg-tertiary)', borderRadius: '4px' }}>
          <p style={{ fontSize: '0.7rem', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '0.75rem', letterSpacing: '0.05em' }}>
            Pipeline Status
          </p>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.5rem' }}>
            <div style={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: status.running ? 'var(--warning)' : 'var(--success)' }} />
            <span style={{ fontSize: '0.9rem', fontWeight: 700 }}>{status.running ? 'Running' : 'Ready'}</span>
          </div>
          <div style={{ height: 4, background: 'rgba(0,0,0,0.05)', borderRadius: 2, overflow: 'hidden' }}>
            <div style={{ height: '100%', background: 'var(--accent-primary)', width: `${status.progress ?? 0}%`, transition: 'width 0.5s ease' }} />
          </div>
          <p style={{ fontSize: '0.75rem', marginTop: '0.5rem', color: 'var(--text-muted)', textAlign: 'right' }}>
            {status.progress ?? 0}% complete
          </p>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
