import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, Users, BookOpen, Layers, Target, CheckCircle2, Loader2, ArrowRight } from 'lucide-react';
import { fetchStats, fetchGoalStatus, listGoals } from '../api';
import { useProjects } from '../context/ProjectContext';

const Dashboard = () => {
  const { activeProject } = useProjects();
  const [stats, setStats] = useState<any>(null);
  const [goalStatus, setGoalStatus] = useState<Record<string, any>>({});
  const [goals, setGoals] = useState<any[]>([]);

  useEffect(() => {
    if (!activeProject) return;
    fetchStats(activeProject.id).then(setStats).catch((e) => console.error('fetchStats:', e));
    listGoals(activeProject.id).then(setGoals).catch((e) => console.error('listGoals:', e));
    fetchGoalStatus(activeProject.id).then(setGoalStatus).catch((e) => console.error('fetchGoalStatus:', e));
    const poll = setInterval(() => {
      fetchGoalStatus(activeProject.id).then(setGoalStatus).catch(() => {});
    }, 5000);
    return () => clearInterval(poll);
  }, [activeProject]);

  if (!activeProject) return <div className="card"><p>Select a project to begin.</p></div>;

  const completedGoals = Object.values(goalStatus).filter((s: any) => s?.complete).length;
  const totalGoals = Object.keys(goalStatus).length;
  const anyRunning = Object.values(goalStatus).some((s: any) => s?.running);

  const statCards = [
    { label: 'Papers Fetched', value: stats?.papersFetched ?? '—', icon: <BookOpen size={20} />, subtitle: stats?.papersFetched ? 'Total publications' : '—' },
    { label: 'Unique Topics', value: stats?.uniqueTopics ?? '—', icon: <Layers size={20} />, subtitle: stats?.uniqueTopics ? 'BERTopic clusters' : '—' },
    { label: 'Key Authors', value: stats?.keyAuthors ?? '—', icon: <Users size={20} />, subtitle: stats?.keyAuthors ? 'Unique researchers' : '—' },
    { label: 'Avg Growth Rate', value: stats?.avgGrowthRate ?? '—', icon: <TrendingUp size={20} />, subtitle: 'CAGR' },
  ];

  const goalList = goals.map((g) => ({
    ...g,
    status: goalStatus[g.id],
  }));

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
      <header style={{ marginBottom: '2.5rem' }}>
        <p style={{ color: 'var(--accent-primary)', fontWeight: 600, marginBottom: '0.5rem' }}>Research Project</p>
        <h1>{activeProject.name}</h1>
        <p>{activeProject.description || 'Project Overview'}</p>
      </header>

      {/* Stats Grid */}
      <div className="grid-4" style={{ marginBottom: '3rem' }}>
        {statCards.map((stat, i) => (
          <div key={i} className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
              <div style={{ color: 'var(--accent-primary)' }}>{stat.icon}</div>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 700 }}>{stat.subtitle}</span>
            </div>
            <h2 style={{ fontSize: '1.75rem', marginBottom: '0.25rem' }}>{stat.value}</h2>
            <p style={{ fontSize: '0.85rem', margin: 0 }}>{stat.label}</p>
          </div>
        ))}
      </div>

      <div className="grid-2">
        {/* Goal Progress */}
        <div className="card">
          <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Target size={18} color="var(--accent-primary)" /> Research Goals
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '1rem' }}>
            {goalList.map((g, i) => {
              const isComplete = g.status?.complete;
              const isRunning = g.status?.running;
              return (
                <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: '0.75rem', borderBottom: '1px solid var(--border-color)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    {isComplete ? <CheckCircle2 size={18} color="var(--success)" /> :
                     isRunning ? <Loader2 size={16} className="spin" color="var(--warning)" /> :
                     <div style={{ width: 18, height: 18, borderRadius: '50%', border: '2px solid var(--text-muted)' }} />}
                    <div>
                      <p style={{ margin: 0, fontSize: '0.9rem', fontWeight: 500, color: isComplete ? 'var(--success)' : 'var(--text-primary)' }}>{g.name}</p>
                      {g.status && (
                        <p style={{ margin: 0, fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                          {g.status.done}/{g.status.total} steps
                        </p>
                      )}
                    </div>
                  </div>
                  <a href={`/${activeProject.id}/research`} className="btn btn-outline" style={{ padding: '0.3rem 0.6rem', fontSize: '0.75rem', textDecoration: 'none' }}>
                    {isComplete ? 'Re-run' : 'Run'}
                  </a>
                </div>
              );
            })}
            {goalList.length === 0 && (
              <p style={{ color: 'var(--text-muted)' }}>No goals available. Set up your project to get started.</p>
            )}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="card">
          <h3>Quick Actions</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Start a research goal or view your results.</p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginTop: '1rem' }}>
            <a href={`/${activeProject.id}/research`} className="btn btn-primary" style={{ width: '100%', textDecoration: 'none', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}>
              <Target size={18} /> Start Research
            </a>
            <a href={`/${activeProject.id}/results`} className="btn btn-outline" style={{ width: '100%', textDecoration: 'none', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}>
              <ArrowRight size={18} /> View Results
            </a>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default Dashboard;
