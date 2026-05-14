import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Search, Filter } from 'lucide-react';
import { fetchTopics } from '../api';

const Explorer = () => {
  const [topics, setTopics] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    fetchTopics()
      .then((data) => { setTopics(data); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  const filtered = topics.filter((t) =>
    !search || t.label?.toLowerCase().includes(search.toLowerCase()) || String(t.id).includes(search)
  );

  return (
    <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.5 }}>
      <header style={{ marginBottom: '2.5rem' }}>
        <h1>Data Explorer</h1>
        <p>Browse and search through identified topics and papers.</p>
      </header>

      <div className="card" style={{ padding: '1rem', marginBottom: '2rem', display: 'flex', gap: '1rem', alignItems: 'center' }}>
        <div style={{ position: 'relative', flex: 1 }}>
          <Search size={18} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
          <input type="text" className="form-control" placeholder="Search topics, keywords, or authors..." style={{ paddingLeft: '2.75rem' }}
            value={search} onChange={(e) => setSearch(e.target.value)} />
        </div>
        <button className="btn btn-outline" onClick={() => setSearch('')}>
          <Filter size={18} />
          Clear
        </button>
      </div>

      {loading ? (
        <div className="card">Loading topics...</div>
      ) : filtered.length === 0 ? (
        <div className="card">
          <p style={{ color: 'var(--text-muted)' }}>
            {topics.length === 0 ? 'No topics found. Run the pipeline first (Stages 0-2).' : 'No results match your search.'}
          </p>
        </div>
      ) : (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr style={{ background: 'var(--bg-tertiary)', borderBottom: '1px solid var(--border-color)' }}>
                <th style={{ padding: '1rem 1.5rem', fontWeight: 600 }}>ID</th>
                <th style={{ padding: '1rem 1.5rem', fontWeight: 600 }}>Label</th>
                <th style={{ padding: '1rem 1.5rem', fontWeight: 600 }}>Paper Count</th>
                <th style={{ padding: '1rem 1.5rem', fontWeight: 600 }}>Classification</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((topic) => (
                <tr key={topic.id} style={{ borderBottom: '1px solid var(--border-color)' }}>
                  <td style={{ padding: '1rem 1.5rem', color: 'var(--text-muted)' }}>{topic.id}</td>
                  <td style={{ padding: '1rem 1.5rem', fontWeight: 600 }}>{topic.label || `Topic ${topic.id}`}</td>
                  <td style={{ padding: '1rem 1.5rem' }}>{topic.count}</td>
                  <td style={{ padding: '1rem 1.5rem' }}>
                    {topic.status === 'PENDING' ? (
                      <span className="badge badge-warning">Unclassified</span>
                    ) : (
                      <span className={`badge ${topic.status === 'CORE' ? 'badge-success' : 'badge-warning'}`}>
                        {topic.status}
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </motion.div>
  );
};

export default Explorer;
