import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { ExternalLink, FileText, ImageIcon } from 'lucide-react';
import { fetchFigures, fetchReport, fetchStats } from '../api';

const Results = () => {
  const [figures, setFigures] = useState<any[]>([]);
  const [report, setReport] = useState<any>(null);
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    fetchFigures().then(setFigures).catch(() => {});
    fetchReport().then(setReport).catch(() => {});
    fetchStats().then(setStats).catch(() => {});
  }, []);

  return (
    <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.5 }}>
      <header style={{ marginBottom: '2.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
        <div>
          <h1>Final Results</h1>
          <p>The final research report and manuscript-ready visualizations.</p>
        </div>
        <div style={{ display: 'flex', gap: '1rem' }}>
          {report?.exists && (
            <button className="btn btn-primary" onClick={() => window.open('/api/report', '_blank')}>
              <FileText size={18} />
              View Full Report
            </button>
          )}
        </div>
      </header>

      {figures.length === 0 ? (
        <div className="card">
          <p style={{ color: 'var(--text-muted)' }}>No figures generated yet. Run Phase 5 (Visualization) to generate them.</p>
        </div>
      ) : (
        <div className="grid-2">
          {figures.map((fig, i) => (
            <div key={i} className="card" style={{ padding: 0, overflow: 'hidden' }}>
              <div style={{ height: '240px', background: 'var(--bg-tertiary)', display: 'flex', alignItems: 'center', justifyContent: 'center', borderBottom: '1px solid var(--border-color)', overflow: 'hidden' }}>
                {fig.type === 'png' ? (
                  <img src={fig.path} alt={fig.filename} style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain' }} />
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.5rem', color: 'var(--text-muted)' }}>
                    <ImageIcon size={48} />
                    <span style={{ fontSize: '0.85rem' }}>Interactive: {fig.filename}</span>
                  </div>
                )}
              </div>
              <div style={{ padding: '1.5rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div>
                    <span style={{ fontSize: '0.7rem', fontWeight: 800, color: 'var(--accent-primary)', textTransform: 'uppercase' }}>
                      Figure {i + 1}
                    </span>
                    <h3 style={{ marginTop: '0.25rem' }}>{fig.filename.replace(/\.[^.]+$/, '').replace(/_/g, ' ')}</h3>
                  </div>
                  <button className="btn btn-outline" style={{ padding: '0.5rem' }} onClick={() => window.open(fig.path, '_blank')}>
                    <ExternalLink size={16} />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {report?.exists && report?.content && (
        <div className="card" style={{ marginTop: '2rem' }}>
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

      {stats && (
        <div className="card" style={{ marginTop: '2rem' }}>
          <h3>Report Summary</h3>
          <div style={{ fontSize: '0.85rem', display: 'flex', gap: '2rem', marginTop: '1rem', flexWrap: 'wrap' }}>
            <div><span style={{ color: 'var(--text-muted)' }}>Papers:</span> {stats.papersFetched}</div>
            <div><span style={{ color: 'var(--text-muted)' }}>Topics:</span> {stats.uniqueTopics}</div>
            <div><span style={{ color: 'var(--text-muted)' }}>Authors:</span> {stats.keyAuthors}</div>
            <div><span style={{ color: 'var(--text-muted)' }}>Growth:</span> {stats.avgGrowthRate}</div>
          </div>
        </div>
      )}
    </motion.div>
  );
};

export default Results;
