import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Plus, Trash2, Copy, Star, ArrowRight, Beaker } from 'lucide-react';
import { listProjects, createProject, deleteProject, setDefaultProject, duplicateProject } from '../api';
import { useProjects } from '../context/ProjectContext';

const ProjectsPage = () => {
  const { setActive, refreshProjects } = useProjects();
  const [projects, setProjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [newName, setNewName] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const navigate = useNavigate();

  const load = async () => {
    setLoading(true);
    try {
      const data = await listProjects();
      setProjects(data);
    } catch {}
    setLoading(false);
  };

  useEffect(() => { load(); }, []);

  const handleCreate = async () => {
    if (!newName.trim()) return;
    try {
      const p = await createProject(newName.trim(), newDesc.trim());
      setShowCreate(false);
      setNewName('');
      setNewDesc('');
      await load();
      setActive(p);
      navigate(`/${p.id}/dashboard`);
    } catch (e: any) { alert(e.message); }
  };

  const handleDelete = async (pid: string, name: string) => {
    if (!confirm(`Delete "${name}"? This will remove all data permanently.`)) return;
    try {
      await deleteProject(pid);
      await load();
      await refreshProjects();
    } catch (e: any) { alert(e.message); }
  };

  const handleSetDefault = async (pid: string) => {
    try {
      await setDefaultProject(pid);
      await load();
      await refreshProjects();
    } catch (e: any) { alert(e.message); }
  };

  const handleDuplicate = async (pid: string, name: string) => {
    try {
      await duplicateProject(pid, `${name} (Copy)`);
      await load();
    } catch (e: any) { alert(e.message); }
  };

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
      <header style={{ marginBottom: '2.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
        <div>
          <h1>Research Projects</h1>
          <p>Create and manage multiple research studies.</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowCreate(true)}>
          <Plus size={18} /> New Project
        </button>
      </header>

      {/* Create Modal */}
      {showCreate && (
        <div style={{ position: 'fixed', inset: 0, zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'rgba(0,0,0,0.6)' }}>
          <div className="card" style={{ width: '480px', maxWidth: '90vw' }}>
            <h3>Create New Project</h3>
            <div className="form-group">
              <label>Project Name</label>
              <input className="form-control" value={newName} onChange={(e) => setNewName(e.target.value)}
                placeholder="e.g. My Research Study" autoFocus />
            </div>
            <div className="form-group">
              <label>Description (optional)</label>
              <textarea className="form-control" rows={3} value={newDesc} onChange={(e) => setNewDesc(e.target.value)}
                placeholder="Brief description of your research topic..." />
            </div>
            <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end' }}>
              <button className="btn btn-outline" onClick={() => setShowCreate(false)}>Cancel</button>
              <button className="btn btn-primary" onClick={handleCreate} disabled={!newName.trim()}>Create Project</button>
            </div>
          </div>
        </div>
      )}

      {loading ? (
        <div className="card"><p>Loading projects...</p></div>
      ) : projects.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '4rem 2rem' }}>
          <Beaker size={48} color="var(--text-muted)" style={{ marginBottom: '1rem' }} />
          <h2>No Projects Yet</h2>
          <p>Create your first research project to get started.</p>
          <button className="btn btn-primary" onClick={() => setShowCreate(true)} style={{ marginTop: '1rem' }}>
            <Plus size={18} /> Create Project
          </button>
        </div>
      ) : (
        <div className="grid-2" style={{ gap: '1.5rem' }}>
          {projects.map((p) => (
            <div key={p.id} className="card" style={{ display: 'flex', flexDirection: 'column' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
                <h3 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  {p.name}
                  {p.isDefault && <Star size={16} color="var(--warning)" fill="var(--warning)" />}
                </h3>
                <span className={`badge ${p.status === 'completed' ? 'badge-success' : 'badge-warning'}`}>
                  {p.status}
                </span>
              </div>
              <p style={{ fontSize: '0.85rem', flex: 1, margin: 0 }}>{p.description || 'No description'}</p>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.75rem' }}>
                Created: {p.createdAt ? new Date(p.createdAt).toLocaleDateString() : '—'}
              </div>
              <div style={{ display: 'flex', gap: '0.5rem', marginTop: '1rem', flexWrap: 'wrap' }}>
                <button className="btn btn-primary" style={{ flex: 1, fontSize: '0.8rem' }}
                  onClick={() => { navigate(`/${p.id}/dashboard`); }}>
                  <ArrowRight size={16} /> Open
                </button>
                <button className="btn btn-outline" style={{ padding: '0.5rem' }} title="Duplicate"
                  onClick={() => handleDuplicate(p.id, p.name)}>
                  <Copy size={16} />
                </button>
                <button className="btn btn-outline" style={{ padding: '0.5rem' }} title="Set as Default"
                  onClick={() => handleSetDefault(p.id)} disabled={p.isDefault}>
                  <Star size={16} />
                </button>
                <button className="btn btn-outline" style={{ padding: '0.5rem', color: 'var(--error)', borderColor: 'transparent' }}
                  title="Delete" onClick={() => handleDelete(p.id, p.name)} disabled={p.isDefault}>
                  <Trash2 size={16} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </motion.div>
  );
};

export default ProjectsPage;
