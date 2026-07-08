/* eslint-disable @typescript-eslint/no-explicit-any */
import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { BarChart3, ImageIcon, Search } from 'lucide-react';
import { fetchDataset, fetchTopics, fetchWorkspace } from '../api';
import { useProjects } from '../context/ProjectContext';

const DATASETS = [
  { id: 'authors', label: 'Top authors' },
  { id: 'sources', label: 'Top venues' },
  { id: 'trends/summary', label: 'Trend summary' },
  { id: 'geopolitical', label: 'Country collaboration' },
  { id: 'bursts', label: 'Burst terms' },
  { id: 'evolution', label: 'Theme evolution' },
  { id: 'narrative', label: 'Narrative draft' },
];

const Explorer = () => {
  const { activeProject } = useProjects();
  const [workspace, setWorkspace] = useState<any>(null);
  const [topics, setTopics] = useState<any[]>([]);
  const [search, setSearch] = useState('');
  const [tab, setTab] = useState<'topics' | 'evidence' | 'figures'>('topics');
  const [datasets, setDatasets] = useState<Record<string, any>>({});

  useEffect(() => {
    if (!activeProject) return;

    fetchWorkspace(activeProject.id).then(setWorkspace).catch(() => {});
    fetchTopics(activeProject.id).then(setTopics).catch(() => {});

    Promise.allSettled(DATASETS.map((dataset) => fetchDataset(activeProject.id, dataset.id))).then((results) => {
      const next: Record<string, any> = {};
      results.forEach((result, index) => {
        if (result.status === 'fulfilled') {
          next[DATASETS[index].id] = result.value;
        }
      });
      setDatasets(next);
    });
  }, [activeProject]);

  if (!activeProject) {
    return <div className="card">Select a project first.</div>;
  }

  const filteredTopics = topics.filter((topic) => {
    const needle = search.trim().toLowerCase();
    if (!needle) return true;
    return topic.label?.toLowerCase().includes(needle) || String(topic.id).includes(needle);
  });

  return (
    <motion.div className="page" initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }}>
      <section className="card hero-card" style={{ marginBottom: '1rem' }}>
        <p className="eyebrow">Evidence Explorer</p>
        <h1>Inspect the dataset, not just the headline metrics.</h1>
        <p className="lede" style={{ maxWidth: '54rem', marginTop: '0.9rem' }}>
          Use this room to pressure-test the output: search topics, skim the strongest tables, and verify whether the figures actually support the claims you plan to write.
        </p>
      </section>

      <section className="inline-list" style={{ marginBottom: '1rem' }}>
        <button className={`btn ${tab === 'topics' ? 'btn-primary' : 'btn-outline'}`} onClick={() => setTab('topics')}>
          <Search size={16} />
          Topics
        </button>
        <button className={`btn ${tab === 'evidence' ? 'btn-primary' : 'btn-outline'}`} onClick={() => setTab('evidence')}>
          <BarChart3 size={16} />
          Evidence tables
        </button>
        <button className={`btn ${tab === 'figures' ? 'btn-primary' : 'btn-outline'}`} onClick={() => setTab('figures')}>
          <ImageIcon size={16} />
          Figures
        </button>
      </section>

      {tab === 'topics' && (
        <section className="stack">
          <div className="card">
            <div className="section-head">
              <div>
                <p className="eyebrow">Topic Search</p>
                <h2>Topic inventory</h2>
              </div>
            </div>
            <input
              className="form-control"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search by topic label or id…"
            />
          </div>

          <div className="card table-shell">
            {filteredTopics.length === 0 ? (
              <div className="muted">No topics available yet. Run a topic-oriented goal first.</div>
            ) : (
              <table>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Label</th>
                    <th>Papers</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredTopics.map((topic) => (
                    <tr key={topic.id}>
                      <td>{topic.id}</td>
                      <td>{topic.label || `Topic ${topic.id}`}</td>
                      <td>{topic.count}</td>
                      <td>
                        <span className={`badge ${topic.status === 'CORE' ? 'badge-success' : topic.status === 'PENDING' ? 'badge-warning' : 'badge-neutral'}`}>
                          {topic.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </section>
      )}

      {tab === 'evidence' && (
        <section className="grid-2">
          {DATASETS.filter((dataset) => datasets[dataset.id]).map((dataset) => {
            const payload = datasets[dataset.id];
            const rows = Array.isArray(payload) ? payload : null;
            const content = payload?.content;

            return (
              <div key={dataset.id} className="card">
                <div className="section-head">
                  <div>
                    <p className="eyebrow">Dataset</p>
                    <h2>{dataset.label}</h2>
                  </div>
                  <span className="badge badge-neutral">
                    {rows ? `${rows.length} rows` : 'Text output'}
                  </span>
                </div>

                {rows ? (
                  <div className="table-shell">
                    <table>
                      <thead>
                        <tr>
                          {Object.keys(rows[0] ?? {}).slice(0, 4).map((column) => (
                            <th key={column}>{column}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {rows.slice(0, 5).map((row: any, index: number) => (
                          <tr key={index}>
                            {Object.keys(row).slice(0, 4).map((column) => (
                              <td key={column}>{String(row[column])}</td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="report-shell">{content}</div>
                )}
              </div>
            );
          })}
        </section>
      )}

      {tab === 'figures' && (
        <section className="figure-grid">
          {(workspace?.figuresPreview ?? []).length === 0 ? (
            <div className="card">
              <div className="muted">No figures are available yet.</div>
            </div>
          ) : (
            workspace.figuresPreview.map((figure: any) => (
              <div key={figure.filename} className="card">
                <div className="figure-frame">
                  {figure.type === 'html' ? (
                    <div className="muted">Interactive figure: {figure.filename}</div>
                  ) : (
                    <img src={`/figures/${activeProject.id}/${figure.filename}`} alt={figure.filename} />
                  )}
                </div>
                <div style={{ marginTop: '1rem' }}>
                  <strong>{figure.filename.replace(/\.[^.]+$/, '').replace(/_/g, ' ')}</strong>
                </div>
              </div>
            ))
          )}
        </section>
      )}
    </motion.div>
  );
};

export default Explorer;
