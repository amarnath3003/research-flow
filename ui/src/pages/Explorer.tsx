import React from 'react';
import { motion } from 'framer-motion';
import { Search, Filter, Download } from 'lucide-react';

const Explorer = () => {
  const topics = [
    { id: 0, label: 'Open Science Policy', count: 420, keywords: 'open access, policy, governance', status: 'CORE' },
    { id: 1, label: 'Cybersecurity in Academia', count: 385, keywords: 'threats, universities, data breach', status: 'CORE' },
    { id: 2, label: 'Research Data Repositories', count: 312, keywords: 'storage, repositories, FAIR data', status: 'CORE' },
    { id: 3, label: 'Ransomware in Healthcare', count: 120, keywords: 'hospital, patient, malware', status: 'NOISE' },
    { id: 4, label: 'Library Information Systems', count: 245, keywords: 'librarian, management, software', status: 'SUPPORTING' },
  ];

  return (
    <motion.div 
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5 }}
    >
      <header style={{ marginBottom: '2.5rem' }}>
        <h1>Data Explorer</h1>
        <p>Browse and search through identified topics and papers.</p>
      </header>

      <div className="card" style={{ padding: '1rem', marginBottom: '2rem', display: 'flex', gap: '1rem', alignItems: 'center' }}>
        <div style={{ position: 'relative', flex: 1 }}>
          <Search size={18} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
          <input 
            type="text" 
            className="form-control" 
            placeholder="Search topics, keywords, or authors..." 
            style={{ paddingLeft: '2.75rem' }}
          />
        </div>
        <button className="btn btn-outline">
          <Filter size={18} />
          Filter
        </button>
        <button className="btn btn-outline">
          <Download size={18} />
          Export CSV
        </button>
      </div>

      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
          <thead>
            <tr style={{ background: 'var(--bg-tertiary)', borderBottom: '1px solid var(--border-color)' }}>
              <th style={{ padding: '1rem 1.5rem', fontWeight: 600 }}>ID</th>
              <th style={{ padding: '1rem 1.5rem', fontWeight: 600 }}>Label</th>
              <th style={{ padding: '1rem 1.5rem', fontWeight: 600 }}>Count</th>
              <th style={{ padding: '1rem 1.5rem', fontWeight: 600 }}>Top Keywords</th>
              <th style={{ padding: '1rem 1.5rem', fontWeight: 600 }}>Status</th>
              <th style={{ padding: '1rem 1.5rem', fontWeight: 600 }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {topics.map((topic) => (
              <tr key={topic.id} style={{ borderBottom: '1px solid var(--border-color)' }}>
                <td style={{ padding: '1rem 1.5rem', color: 'var(--text-muted)' }}>{topic.id}</td>
                <td style={{ padding: '1rem 1.5rem', fontWeight: 600 }}>{topic.label}</td>
                <td style={{ padding: '1rem 1.5rem' }}>{topic.count}</td>
                <td style={{ padding: '1rem 1.5rem', fontSize: '0.85rem' }}>{topic.keywords}</td>
                <td style={{ padding: '1rem 1.5rem' }}>
                  <span className={`badge ${topic.status === 'CORE' ? 'badge-success' : 'badge-warning'}`}>
                    {topic.status}
                  </span>
                </td>
                <td style={{ padding: '1rem 1.5rem' }}>
                  <button className="btn btn-outline" style={{ padding: '0.4rem 0.8rem', fontSize: '0.75rem' }}>Edit</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </motion.div>
  );
};

export default Explorer;
