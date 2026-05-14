import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { ExternalLink, FileText, ImageIcon, Target, TrendingUp, Users, Globe, Layers, GitBranch, Search, CheckCircle2 } from 'lucide-react';
import { fetchFigures, fetchReport, fetchStats, listGoals, fetchGoalStatus } from '../api';
import { useProjects } from '../context/ProjectContext';

const GOAL_ICONS: Record<string, any> = {
  Globe, Layers, TrendingUp, Users, GitBranch, Search,
};

const Results = () => {
  const { activeProject } = useProjects();
  const [figures, setFigures] = useState<any[]>([]);
  const [report, setReport] = useState<any>(null);
  const [stats, setStats] = useState<any>(null);
  const [goals, setGoals] = useState<any[]>([]);
  const [goalStatus, setGoalStatus] = useState<Record<string, any>>({});
  const [activeTab, setActiveTab] = useState<string | null>(null);

  useEffect(() => {
    if (!activeProject) return;
    fetchFigures(activeProject.id).then(setFigures).catch(() => {});
    fetchReport(activeProject.id).then(setReport).catch(() => {});
    fetchStats(activeProject.id).then(setStats).catch(() => {});
    listGoals(activeProject.id).then(setGoals).catch(() => {});
    fetchGoalStatus(activeProject.id).then(setGoalStatus).catch(() => {});
  }, [activeProject]);

  if (!activeProject) return <div className="card"><p>Select a project first.</p></div>;

  const completedGoals = goals.filter((g) => goalStatus[g.id]?.complete);
  const noResults = figures.length === 0 && (report === null || !report.exists);

  return (
    <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.5 }}>
      <header style={{ marginBottom: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
        <div>
          <h1>{activeProject.name} — Results</h1>
          <p>Research outputs organized by goal.</p>
        </div>
        {report?.exists && (
          <button className="btn btn-primary" onClick={() => window.open(`/api/${activeProject.id}/report`, '_blank')}>
            <FileText size={18} /> View Report
          </button>
        )}
      </header>

      {noResults && (
        <div className="card">
          <p style={{ color: 'var(--text-muted)' }}>No results yet. Go to <a href={`/${activeProject.id}/research`} style={{ color: 'var(--accent-primary)' }}>Research</a> to run a goal.</p>
        </div>
      )}

      {/* Completed Goals Tabs */}
      {completedGoals.length > 0 && (
        <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
          <button
            className={`btn ${activeTab === null ? 'btn-primary' : 'btn-outline'}`}
            onClick={() => setActiveTab(null)}
            style={{ padding: '0.4rem 0.8rem', fontSize: '0.8rem' }}
          >
            All Results
          </button>
          {completedGoals.map((g) => {
            const Icon = GOAL_ICONS[g.icon] || Target;
            return (
              <button
                key={g.id}
                className={`btn ${activeTab === g.id ? 'btn-primary' : 'btn-outline'}`}
                onClick={() => setActiveTab(g.id)}
                style={{ padding: '0.4rem 0.8rem', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}
              >
                <CheckCircle2 size={12} color="var(--success)" />
                <Icon size={14} />
                {g.name}
              </button>
            );
          })}
        </div>
      )}

      {/* Figures Gallery */}
      {figures.length > 0 && (activeTab === null || ['landscape', 'trends', 'evolution', 'topics'].includes(activeTab)) && (
        <div style={{ marginBottom: '2rem' }}>
          <h3 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <ImageIcon size={18} /> Figures
          </h3>
          <div className="grid-2">
            {figures.filter((fig) => {
              // If no filter or showing all, include all
              return true;
            }).map((fig, i) => (
              <div key={i} className="card" style={{ padding: 0, overflow: 'hidden' }}>
                <div style={{ height: '220px', background: 'var(--bg-tertiary)', display: 'flex', alignItems: 'center', justifyContent: 'center', borderBottom: '1px solid var(--border-color)', overflow: 'hidden' }}>
                  {fig.type === 'png' ? (
                    <img src={`/figures/${activeProject.id}/${fig.filename}`} alt={fig.filename} style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain' }} />
                  ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.5rem', color: 'var(--text-muted)' }}>
                      <ImageIcon size={48} />
                      <span style={{ fontSize: '0.85rem' }}>Interactive: {fig.filename}</span>
                    </div>
                  )}
                </div>
                <div style={{ padding: '1rem 1.25rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div>
                      <span style={{ fontSize: '0.7rem', fontWeight: 800, color: 'var(--accent-primary)', textTransform: 'uppercase' }}>Figure {i + 1}</span>
                      <h3 style={{ marginTop: '0.25rem', fontSize: '0.95rem' }}>{fig.filename.replace(/\.[^.]+$/, '').replace(/_/g, ' ')}</h3>
                    </div>
                    <button className="btn btn-outline" style={{ padding: '0.4rem' }} onClick={() => window.open(`/figures/${activeProject.id}/${fig.filename}`, '_blank')}>
                      <ExternalLink size={14} />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Report */}
      {report?.exists && report?.content && (
        <div className="card" style={{ marginBottom: '2rem' }}>
          <h3>Executive Discussion</h3>
          <div style={{ fontSize: '0.9rem', color: 'var(--text-primary)', lineHeight: 1.8, whiteSpace: 'pre-wrap', maxHeight: '500px', overflowY: 'auto' }}>
            {report.content.split('\n').map((line: string, i: number) => {
              if (line.startsWith('# ')) return <h3 key={i} style={{ marginTop: '1rem' }}>{line.replace('# ', '')}</h3>;
              if (line.startsWith('## ')) return <h4 key={i} style={{ marginTop: '1rem', color: 'var(--accent-primary)' }}>{line.replace('## ', '')}</h4>;
              if (line.startsWith('- ')) return <li key={i} style={{ marginLeft: '1.5rem' }}>{line.replace('- ', '')}</li>;
              if (line.trim() === '') return <br key={i} />;
              return <p key={i}>{line}</p>;
            })}
          </div>
        </div>
      )}

      {/* Report Summary Stats */}
      {stats && (stats.papersFetched > 0 || stats.uniqueTopics > 0) && (
        <div className="card">
          <h3>Report Summary</h3>
          <div style={{ fontSize: '0.85rem', display: 'flex', gap: '2rem', marginTop: '1rem', flexWrap: 'wrap' }}>
            {stats.papersFetched > 0 && <div><span style={{ color: 'var(--text-muted)' }}>Papers:</span> {stats.papersFetched}</div>}
            {stats.uniqueTopics > 0 && <div><span style={{ color: 'var(--text-muted)' }}>Topics:</span> {stats.uniqueTopics}</div>}
            {stats.keyAuthors > 0 && <div><span style={{ color: 'var(--text-muted)' }}>Authors:</span> {stats.keyAuthors}</div>}
            {stats.avgGrowthRate && stats.avgGrowthRate !== '0%' && <div><span style={{ color: 'var(--text-muted)' }}>Growth:</span> {stats.avgGrowthRate}</div>}
          </div>
        </div>
      )}
    </motion.div>
  );
};

export default Results;
