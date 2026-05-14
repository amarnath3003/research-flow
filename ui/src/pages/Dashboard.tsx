import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, Users, BookOpen, Layers } from 'lucide-react';
import { fetchStats, fetchStatus } from '../api';

const Dashboard = () => {
  const [stats, setStats] = useState<any>(null);
  const [status, setStatus] = useState<any>(null);

  useEffect(() => {
    fetchStats().then(setStats).catch(() => {});
    const poll = setInterval(() => {
      fetchStatus().then(setStatus).catch(() => {});
    }, 5000);
    return () => clearInterval(poll);
  }, []);

  const cards = [
    { label: 'Papers Fetched', value: stats?.papersFetched ?? '—', icon: <BookOpen size={20} />, trend: stats?.papersFetched ? 'Total' : '—' },
    { label: 'Unique Topics', value: stats?.uniqueTopics ?? '—', icon: <Layers size={20} />, trend: stats?.uniqueTopics ? 'BERTopic clusters' : '—' },
    { label: 'Key Authors', value: stats?.keyAuthors ?? '—', icon: <Users size={20} />, trend: stats?.keyAuthors ? 'Unique' : '—' },
    { label: 'Avg Growth Rate', value: stats?.avgGrowthRate ?? '—', icon: <TrendingUp size={20} />, trend: 'CAGR' },
  ];

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
      <header style={{ marginBottom: '3rem' }}>
        <p style={{ color: 'var(--accent-primary)', fontWeight: 600, marginBottom: '0.5rem' }}>Welcome back, Researcher</p>
        <h1>Project Overview</h1>
        <p>Current Research: <strong>ResearchFlow Pipeline</strong></p>
      </header>

      <div className="grid-4" style={{ marginBottom: '3rem' }}>
        {cards.map((stat, i) => (
          <div key={i} className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
              <div style={{ color: 'var(--accent-primary)' }}>{stat.icon}</div>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 700 }}>{stat.trend}</span>
            </div>
            <h2 style={{ fontSize: '1.75rem', marginBottom: '0.25rem' }}>{stat.value}</h2>
            <p style={{ fontSize: '0.85rem', margin: 0 }}>{stat.label}</p>
          </div>
        ))}
      </div>

      <div className="grid-2">
        <div className="card">
          <h3>Pipeline Status</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '1.5rem' }}>
            {status?.stages?.filter((s: any) => s.status !== 'pending').slice(0, 6).map((s: any, i: number) => (
              <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: '0.75rem', borderBottom: '1px solid var(--border-color)' }}>
                <div>
                  <p style={{ color: 'var(--text-primary)', margin: 0, fontSize: '0.9rem', fontWeight: 500 }}>{s.name}</p>
                </div>
                <span className={`badge ${s.status === 'completed' ? 'badge-success' : 'badge-warning'}`}>
                  {s.status === 'completed' ? 'Completed' : s.status === 'current' ? 'Running' : 'Pending'}
                </span>
              </div>
            ))}
            {(!status || status.stages?.every((s: any) => s.status === 'pending')) && (
              <p style={{ color: 'var(--text-muted)' }}>No pipeline activity yet. Go to Workflow to start.</p>
            )}
          </div>
        </div>

        <div className="card">
          <h3>Quick Actions</h3>
          <p>Get started with the next steps in your research flow.</p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginTop: '1rem' }}>
            <button className="btn btn-primary" style={{ width: '100%' }} onClick={() => window.location.href = '/workflow'}>
              Open Workflow
            </button>
            <button className="btn btn-outline" style={{ width: '100%' }} onClick={() => window.location.href = '/results'}>
              View Results
            </button>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default Dashboard;
