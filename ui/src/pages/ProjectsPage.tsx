/* eslint-disable @typescript-eslint/no-explicit-any, react-hooks/set-state-in-effect */
import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, Copy, Plus, Star, Trash2 } from 'lucide-react';
import { createProject, deleteProject, duplicateProject, listProjects, setDefaultProject } from '../api';
import { useProjects } from '../context/ProjectContext';
import { useNavigate } from 'react-router-dom';

const ProjectsPage = () => {
  const { activeProject, refreshProjects, setActive } = useProjects();
  const [projects, setProjects] = useState<any[]>([]);
  const [showCreate, setShowCreate] = useState(false);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const refresh = async () => {
    setLoading(true);
    try {
      const response = await listProjects();
      setProjects(response);
    } catch (reason: any) {
      setError(reason.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refresh();
  }, []);

  const handleCreate = async () => {
    if (!name.trim()) return;

    const project = await createProject(name.trim(), description.trim());
    await refresh();
    await refreshProjects();
    setActive(project);
    setShowCreate(false);
    setName('');
    setDescription('');
    navigate(`/${project.id}/dashboard`);
  };

  return (
    <motion.div className="page" initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }}>
      <section className="card hero-card" style={{ marginBottom: '1rem' }}>
        <p className="eyebrow">Project Portfolio</p>
        <h1>Each research question deserves its own clean workspace.</h1>
        <p className="lede" style={{ maxWidth: '54rem', marginTop: '0.9rem' }}>
          Keep corpora, configuration, topic decisions, and reports separated by project. That makes reruns safer and the narrative trail easier to defend later.
        </p>
        <div style={{ marginTop: '1.2rem' }}>
          <button className="btn btn-primary" onClick={() => setShowCreate(true)}>
            <Plus size={16} />
            New project
          </button>
        </div>
      </section>

      {loading ? (
        <section className="card">Loading projects…</section>
      ) : (
        <section className="grid-2">
          {projects.map((project) => (
            <div key={project.id} className="card goal-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', gap: '0.75rem' }}>
                <div>
                  <h2 style={{ fontSize: '1.3rem' }}>{project.name}</h2>
                  <p className="muted" style={{ marginTop: '0.35rem' }}>
                    {project.description || 'No description yet.'}
                  </p>
                </div>
                <div className="inline-list">
                  {project.isDefault && (
                    <span className="badge badge-success">
                      <Star size={12} />
                      Default
                    </span>
                  )}
                  <span className={`badge ${project.status === 'completed' ? 'badge-success' : project.status === 'running' ? 'badge-warning' : 'badge-neutral'}`}>
                    {project.status}
                  </span>
                </div>
              </div>

              <div className="muted">Created {project.createdAt ? new Date(project.createdAt).toLocaleDateString() : 'recently'}</div>

              <div className="inline-list">
                <button className="btn btn-primary" onClick={() => navigate(`/${project.id}/dashboard`)}>
                  <ArrowRight size={16} />
                  Open
                </button>
                <button className="btn btn-outline" onClick={() => duplicateProject(project.id, `${project.name} copy`).then(refresh).then(refreshProjects)}>
                  <Copy size={16} />
                  Duplicate
                </button>
                <button className="btn btn-outline" onClick={() => setDefaultProject(project.id).then(refresh).then(refreshProjects)} disabled={project.isDefault}>
                  <Star size={16} />
                  Default
                </button>
                <button
                  className="btn btn-outline"
                  onClick={() => {
                    if (window.confirm(`Delete "${project.name}" permanently?`)) {
                      deleteProject(project.id).then(refresh).then(refreshProjects).then(() => {
                        if (activeProject?.id === project.id) {
                          navigate('/projects');
                        }
                      });
                    }
                  }}
                >
                  <Trash2 size={16} />
                  Delete
                </button>
              </div>
            </div>
          ))}
        </section>
      )}

      {!loading && projects.length === 0 && (
        <section className="card">
          <div className="empty-state">
            <h2>No projects yet</h2>
            <p className="muted">Create the first project to start building a literature map.</p>
          </div>
        </section>
      )}

      {error && <section className="card" style={{ color: 'var(--error)', marginTop: '1rem' }}>{error}</section>}

      {showCreate && (
        <div className="modal-backdrop">
          <div className="card modal-card">
            <div className="section-head">
              <div>
                <p className="eyebrow">Create Project</p>
                <h2>Start a new research workspace</h2>
              </div>
            </div>

            <div className="form-group">
              <label>Project name</label>
              <input className="form-control" value={name} onChange={(event) => setName(event.target.value)} autoFocus />
            </div>

            <div className="form-group">
              <label>Description</label>
              <textarea className="form-control" rows={4} value={description} onChange={(event) => setDescription(event.target.value)} />
            </div>

            <div className="inline-list">
              <button className="btn btn-outline" onClick={() => setShowCreate(false)}>Cancel</button>
              <button className="btn btn-primary" onClick={handleCreate} disabled={!name.trim()}>
                Create
              </button>
            </div>
          </div>
        </div>
      )}
    </motion.div>
  );
};

export default ProjectsPage;
