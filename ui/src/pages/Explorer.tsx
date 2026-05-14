import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Search, Filter, Globe, Layers, TrendingUp, Users, GitBranch, Target, CheckCircle2 } from 'lucide-react';
import { fetchTopics, fetchGoalStatus, listGoals } from '../api';
import { useProjects } from '../context/ProjectContext';

const GOAL_ICONS: Record<string, any> = {
  Globe, Layers, TrendingUp, Users, GitBranch, Search: Target,
};

const Explorer = () => {
  const { activeProject } = useProjects();
  const [topics, setTopics] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [goals, setGoals] = useState<any[]>([]);
  const [goalStatus, setGoalStatus] = useState<Record<string, any>>({});

  useEffect(() => {
    if (!activeProject) return;
    setLoading(true);
    Promise.all([
      fetchTopics(activeProject.id),
      listGoals(activeProject.id),
      fetchGoalStatus(activeProject.id),
    ])
      .then(([t, g, gs]) => { setTopics(t); setGoals(g); setGoalStatus(gs); setLoading(false); })
      .catch(() => setLoading(false));
  }, [activeProject]);

  const filtered = topics.filter((t) =>
    !search || t.label?.toLowerCase().includes(search.toLowerCase()) || String(t.id).includes(search)
  );

  if (!activeProject) return <div className="card"><p>Select a project first.</p></div>;

  const completedGoals = goals.filter((g) => goalStatus[g.id]?.complete);

  return (
    <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.5 }}>
      <header style={{ marginBottom: '2rem' }}>
        <h1>{activeProject.name} — Explore</h1>
        <p>Browse research data organized by goal.</p>
      </header>

      {/* Goal completion badges */}
      {completedGoals.length > 0 && (
        <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
          {completedGoals.map((g) => {
            const Icon = GOAL_ICONS[g.icon] || Target;
            return (
              <div key={g.id} style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', padding: '0.4rem 0.8rem', borderRadius: '6px', background: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.2)', fontSize: '0.8rem' }}>
                <CheckCircle2 size={12} color="var(--success)" />
                <Icon size={12} />
                <span>{g.name}</span>
              </div>
            );
          })}
        </div>
      )}

      {/* Search */}
      <div className="card" style={{ padding: '1rem', marginBottom: '2rem', display: 'flex', gap: '1rem', alignItems: 'center' }}>
        <div style={{ position: 'relative', flex: 1 }}>
          <Search size={18} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
          <input type="text" className="form-control" placeholder="Search topics..." style={{ paddingLeft: '2.75rem' }}
            value={search} onChange={(e) => setSearch(e.target.value)} />
        </div>
        <button className="btn btn-outline" onClick={() => setSearch('')}><Filter size={18} /> Clear</button>
      </div>

      {loading ? (
        <div className="card">Loading topics...</div>
      ) : filtered.length === 0 ? (
        <div className="card">
          <p style={{ color: 'var(--text-muted)' }}>
            {topics.length === 0
              ? 'No topics found. Run a research goal like "Discover Research Topics" or "Map Research Landscape" first.'
              : 'No results match your search.'}
          </p>
        </div>
      ) : (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr style={{ background: 'var(--bg-tertiary)', borderBottom: '1px solid var(--border-color)' }}>
                <th style={{ padding: '1rem 1.5rem', fontWeight: 600 }}>ID</th>
                <th style={{ padding: '1rem 1.5rem', fontWeight: 600 }}>Label</th>
                <th style={{ padding: '1rem 1.5rem', fontWeight: 600 }}>Papers</th>
                <th style={{ padding: '1rem 1.5rem', fontWeight: 600 }}>Status</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((topic) => (
                <tr key={topic.id} style={{ borderBottom: '1px solid var(--border-color)' }}>
                  <td style={{ padding: '1rem 1.5rem', color: 'var(--text-muted)', fontFamily: 'monospace', fontSize: '0.85rem' }}>{topic.id}</td>
                  <td style={{ padding: '1rem 1.5rem', fontWeight: 600 }}>{topic.label || `Topic ${topic.id}`}</td>
                  <td style={{ padding: '1rem 1.5rem' }}>{topic.count}</td>
                  <td style={{ padding: '1rem 1.5rem' }}>
                    {topic.status === 'PENDING' ? (
                      <span className="badge badge-warning">Unclassified</span>
                    ) : topic.status === 'CORE' ? (
                      <span className="badge badge-success">CORE</span>
                    ) : topic.status === 'SUPPORTING' ? (
                      <span className="badge badge-warning">Supporting</span>
                    ) : (
                      <span className="badge" style={{ background: 'rgba(239,68,68,0.1)', color: 'var(--error)' }}>{topic.status}</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div style={{ padding: '0.75rem 1.5rem', background: 'var(--bg-tertiary)', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            {filtered.length} topic{filtered.length !== 1 ? 's' : ''} — {topics.filter(t => t.status !== 'PENDING').length} classified
          </div>
        </div>
      )}

      {/* Data links by completed goals */}
      {completedGoals.length > 0 && (
        <div className="card" style={{ marginTop: '2rem' }}>
          <h3 style={{ marginBottom: '1rem' }}>Available Data</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {completedGoals.map((g) => {
              const Icon = GOAL_ICONS[g.icon] || Target;
              return (
                <div key={g.id} style={{ display: 'flex', alignItems: 'center', gap: '1rem', padding: '0.75rem', borderRadius: '8px', background: 'var(--bg-tertiary)' }}>
                  <Icon size={18} color="var(--accent-primary)" />
                  <div style={{ flex: 1 }}>
                    <p style={{ margin: 0, fontWeight: 600, fontSize: '0.9rem' }}>{g.name}</p>
                    <p style={{ margin: 0, fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      {g.outputs?.map((o: string) => o.replace(/_/g, ' ')).join(', ')}
                    </p>
                  </div>
                  <a href={`/${activeProject.id}/results`} className="btn btn-outline" style={{ padding: '0.3rem 0.6rem', fontSize: '0.75rem', textDecoration: 'none' }}>
                    View Results
                  </a>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </motion.div>
  );
};

export default Explorer;
