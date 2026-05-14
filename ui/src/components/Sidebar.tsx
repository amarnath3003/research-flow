import { useEffect, useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { LayoutDashboard, Settings, Beaker, Database, FileText, FolderKanban, ChevronDown, Target, CheckCircle2, Loader2 } from 'lucide-react';
import { fetchGoalStatus } from '../api';
import { useProjects } from '../context/ProjectContext';

import ThemeToggle from './ThemeToggle';

const Sidebar = () => {
  const { projects, activeProject, setActive } = useProjects();
  const [goalStatus, setGoalStatus] = useState<Record<string, any>>({});
  const [showSelector, setShowSelector] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (!activeProject) return;
    const poll = setInterval(() => {
      fetchGoalStatus(activeProject.id).then(setGoalStatus).catch(() => {});
    }, 5000);
    fetchGoalStatus(activeProject.id).then(setGoalStatus).catch(() => {});
    return () => clearInterval(poll);
  }, [activeProject]);

  const completedGoals = Object.values(goalStatus).filter((s: any) => s?.complete).length;
  const totalGoals = Object.keys(goalStatus).length;
  const anyRunning = Object.values(goalStatus).some((s: any) => s?.running);
  const progressPct = totalGoals > 0 ? Math.round((completedGoals / totalGoals) * 100) : 0;

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
          <LayoutDashboard size={18} /><span>Overview</span>
        </NavLink>
        <NavLink to={`/${activeProject?.id ?? ''}/config`} className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <Settings size={18} /><span>Research Setup</span>
        </NavLink>
        <NavLink to={`/${activeProject?.id ?? ''}/research`} className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <Target size={18} /><span>Research</span>
        </NavLink>
        <NavLink to={`/${activeProject?.id ?? ''}/explorer`} className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <Database size={18} /><span>Explore</span>
        </NavLink>
        <NavLink to={`/${activeProject?.id ?? ''}/results`} className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <FileText size={18} /><span>Results</span>
        </NavLink>
      </nav>

      <div style={{ marginTop: 'auto', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        <ThemeToggle />
        <div className="card" style={{ padding: '1.25rem', marginBottom: 0, background: 'var(--bg-tertiary)', borderRadius: '4px' }}>
          <p style={{ fontSize: '0.7rem', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '0.75rem', letterSpacing: '0.05em' }}>
            Goal Status
          </p>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.5rem' }}>
            <div style={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: anyRunning ? 'var(--warning)' : 'var(--success)' }} />
            <span style={{ fontSize: '0.9rem', fontWeight: 700 }}>
              {anyRunning ? 'Running' : completedGoals === totalGoals && totalGoals > 0 ? 'All Complete' : 'Ready'}
            </span>
          </div>
          <div style={{ height: 4, background: 'rgba(0,0,0,0.05)', borderRadius: 2, overflow: 'hidden' }}>
            <div style={{ height: '100%', background: 'var(--accent-primary)', width: `${progressPct}%`, transition: 'width 0.5s ease' }} />
          </div>
          <p style={{ fontSize: '0.75rem', marginTop: '0.5rem', color: 'var(--text-muted)', textAlign: 'right' }}>
            {completedGoals}/{totalGoals} goals
          </p>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
