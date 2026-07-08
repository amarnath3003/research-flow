/* eslint-disable @typescript-eslint/no-explicit-any, react-hooks/set-state-in-effect */
import { useEffect, useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  Beaker,
  BookOpenText,
  ChevronDown,
  Compass,
  FileText,
  FolderKanban,
  LayoutDashboard,
  Settings2,
  Sparkles,
} from 'lucide-react';
import { fetchWorkspace } from '../api';
import { useProjects } from '../context/ProjectContext';
import ThemeToggle from './ThemeToggle';

const Sidebar = () => {
  const { projects, activeProject, setActive } = useProjects();
  const [showSelector, setShowSelector] = useState(false);
  const [workspace, setWorkspace] = useState<any>(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (!activeProject) {
      setWorkspace(null);
      return;
    }

    fetchWorkspace(activeProject.id).then(setWorkspace).catch(() => {});
    const interval = setInterval(() => {
      fetchWorkspace(activeProject.id).then(setWorkspace).catch(() => {});
    }, 5000);

    return () => clearInterval(interval);
  }, [activeProject]);

  const goals = workspace?.goals ?? [];
  const completedGoals = goals.filter((goal: any) => goal.status?.complete).length;
  const runningGoal = goals.find((goal: any) => goal.status?.running);
  const progress = goals.length > 0 ? Math.round((completedGoals / goals.length) * 100) : 0;

  return (
    <aside className="sidebar">
      <div className="logo" style={{ cursor: 'pointer' }} onClick={() => navigate('/projects')}>
        <Beaker size={28} color="var(--accent-primary)" />
        <div>
          <div>ResearchFlow</div>
          <div className="muted" style={{ fontSize: '0.78rem' }}>Field mapping workspace</div>
        </div>
      </div>

      <div className="project-selector">
        <button className="btn btn-outline selector-button" onClick={() => setShowSelector((value) => !value)}>
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <FolderKanban size={16} />
            <span>{activeProject?.name ?? 'Select project'}</span>
          </span>
          <ChevronDown size={16} />
        </button>

        {showSelector && (
          <div className="selector-menu">
            {projects.map((project) => (
              <button
                key={project.id}
                className={`selector-option ${project.id === activeProject?.id ? 'active' : ''}`}
                onClick={() => {
                  setActive(project);
                  setShowSelector(false);
                  navigate(`/${project.id}/dashboard`);
                }}
              >
                <span>{project.name}</span>
                <span className={`badge ${project.isDefault ? 'badge-success' : 'badge-neutral'}`}>
                  {project.isDefault ? 'Default' : project.status}
                </span>
              </button>
            ))}
            <button className="selector-option" onClick={() => navigate('/projects')}>
              <span>Manage projects</span>
            </button>
          </div>
        )}
      </div>

      {activeProject && (
        <nav className="nav-list">
          <NavLink to={`/${activeProject.id}/dashboard`} className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
            <LayoutDashboard size={18} />
            <span>Overview</span>
          </NavLink>
          <NavLink to={`/${activeProject.id}/config`} className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
            <Settings2 size={18} />
            <span>Setup</span>
          </NavLink>
          <NavLink to={`/${activeProject.id}/research`} className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
            <Sparkles size={18} />
            <span>Research Lab</span>
          </NavLink>
          <NavLink to={`/${activeProject.id}/explorer`} className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
            <Compass size={18} />
            <span>Evidence Explorer</span>
          </NavLink>
          <NavLink to={`/${activeProject.id}/results`} className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
            <FileText size={18} />
            <span>Report Room</span>
          </NavLink>
        </nav>
      )}

      <div className="card spotlight" style={{ marginTop: 'auto' }}>
        <div className="section-head" style={{ marginBottom: '0.8rem' }}>
          <div>
            <p className="eyebrow">Project Pulse</p>
            <h3>{runningGoal ? 'Analysis running' : workspace?.readiness?.configured ? 'Ready to run' : 'Needs setup'}</h3>
          </div>
          <BookOpenText size={20} color="var(--accent-secondary)" />
        </div>

        <div className="stack" style={{ gap: '0.8rem' }}>
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.45rem' }}>
              <span className="muted">Goals completed</span>
              <strong>{completedGoals}/{goals.length || 0}</strong>
            </div>
            <div className="progress-bar">
              <span style={{ width: `${progress}%` }} />
            </div>
          </div>

          <div className="inline-list">
            <span className={`badge ${workspace?.readiness?.configured ? 'badge-success' : 'badge-warning'}`}>
              {workspace?.readiness?.configured ? 'Configured' : 'Missing setup'}
            </span>
            <span className="badge badge-neutral">
              {workspace?.stats?.papersFetched ?? 0} papers
            </span>
            <span className="badge badge-neutral">
              {workspace?.stats?.uniqueTopics ?? 0} topics
            </span>
          </div>

          {runningGoal && (
            <div className="muted" style={{ fontSize: '0.84rem' }}>
              Current run: {runningGoal.name}
            </div>
          )}
        </div>
      </div>

      <ThemeToggle />
    </aside>
  );
};

export default Sidebar;
