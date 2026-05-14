import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, Users, BookOpen, Layers } from 'lucide-react';

const Dashboard = () => {
  const stats = [
    { label: 'Papers Fetched', value: '4,786', icon: <BookOpen size={20} />, trend: '+12%' },
    { label: 'Unique Topics', value: '52', icon: <Layers size={20} />, trend: 'Manual vetting required' },
    { label: 'Key Authors', value: '842', icon: <Users size={20} />, trend: '+5%' },
    { label: 'Avg Growth Rate', value: '24%', icon: <TrendingUp size={20} />, trend: 'CAGR' },
  ];

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <header style={{ marginBottom: '3rem' }}>
        <p style={{ color: 'var(--accent-primary)', fontWeight: 600, marginBottom: '0.5rem' }}>Welcome back, Researcher</p>
        <h1>Project Overview</h1>
        <p>Current Research: <strong>Scholarly Communication & Research Security</strong></p>
      </header>

      <div className="grid-3" style={{ gridTemplateColumns: 'repeat(4, 1fr)', marginBottom: '3rem' }}>
        {stats.map((stat, i) => (
          <div key={i} className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
              <div style={{ color: 'var(--accent-primary)' }}>{stat.icon}</div>
              <span style={{ fontSize: '0.75rem', color: i === 1 ? 'var(--warning)' : 'var(--success)', fontWeight: 700 }}>
                {stat.trend}
              </span>
            </div>
            <h2 style={{ fontSize: '1.75rem', marginBottom: '0.25rem' }}>{stat.value}</h2>
            <p style={{ fontSize: '0.85rem', margin: 0 }}>{stat.label}</p>
          </div>
        ))}
      </div>

      <div className="grid-2">
        <div className="card">
          <h3>Recent Pipeline Activity</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '1.5rem' }}>
            {[
              { task: 'Phase 5: Visualizations generated', time: '2 hours ago', status: 'completed' },
              { task: 'Phase 4: Burst detection analysis', time: '4 hours ago', status: 'completed' },
              { task: 'Phase 2: Topic merging applied', time: 'Yesterday', status: 'completed' },
            ].map((activity, i) => (
              <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: '0.75rem', borderBottom: '1px solid var(--border-color)' }}>
                <div>
                  <p style={{ color: 'var(--text-primary)', margin: 0, fontSize: '0.9rem', fontWeight: 500 }}>{activity.task}</p>
                  <p style={{ margin: 0, fontSize: '0.75rem' }}>{activity.time}</p>
                </div>
                <span className="badge badge-success">Completed</span>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <h3>Quick Actions</h3>
          <p>Get started with the next steps in your research flow.</p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginTop: '1rem' }}>
            <button className="btn btn-primary" style={{ width: '100%' }}>Run Full Pipeline</button>
            <button className="btn btn-outline" style={{ width: '100%' }}>Export Diagnostic Data</button>
            <button className="btn btn-outline" style={{ width: '100%' }}>Open Final Report</button>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default Dashboard;
