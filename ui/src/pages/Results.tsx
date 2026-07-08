/* eslint-disable @typescript-eslint/no-explicit-any */
import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { ExternalLink, FileText, ImageIcon, LibraryBig } from 'lucide-react';
import { fetchReport, fetchWorkspace } from '../api';
import { useProjects } from '../context/ProjectContext';

const Results = () => {
  const { activeProject } = useProjects();
  const [workspace, setWorkspace] = useState<any>(null);
  const [report, setReport] = useState<any>(null);

  useEffect(() => {
    if (!activeProject) return;

    Promise.all([fetchWorkspace(activeProject.id), fetchReport(activeProject.id)])
      .then(([workspaceResponse, reportResponse]) => {
        setWorkspace(workspaceResponse);
        setReport(reportResponse);
      })
      .catch(() => {});
  }, [activeProject]);

  if (!activeProject) {
    return <div className="card">Select a project first.</div>;
  }

  const figures = workspace?.figuresPreview ?? [];
  const hasReport = report?.exists;

  return (
    <motion.div className="page" initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }}>
      <section className="card hero-card" style={{ marginBottom: '1rem' }}>
        <p className="eyebrow">Report Room</p>
        <h1>Review the outputs as if they were headed into a manuscript.</h1>
        <p className="lede" style={{ maxWidth: '54rem', marginTop: '0.9rem' }}>
          This page collects the narrative draft, figure pack, and delivery signals so you can decide whether the project is publishable, needs refinement, or needs a new scope.
        </p>
        <div className="inline-list" style={{ marginTop: '1.1rem' }}>
          <span className={`badge ${hasReport ? 'badge-success' : 'badge-warning'}`}>
            {hasReport ? 'Narrative available' : 'No report yet'}
          </span>
          <span className="badge badge-neutral">{workspace?.stats?.papersFetched ?? 0} papers</span>
          <span className="badge badge-neutral">{figures.length} figures shown</span>
        </div>
      </section>

      <section className="grid-2" style={{ marginBottom: '1rem' }}>
        <div className="card">
          <div className="section-head">
            <div>
              <p className="eyebrow">Narrative Draft</p>
              <h2>Executive report</h2>
            </div>
            {hasReport && (
              <button className="btn btn-outline" onClick={() => window.open(`/api/${activeProject.id}/report`, '_blank')}>
                <ExternalLink size={16} />
                Open raw
              </button>
            )}
          </div>

          {hasReport ? (
            <div className="report-shell">
              {report.content.split('\n').map((line: string, index: number) => {
                if (line.startsWith('# ')) return <h3 key={index}>{line.slice(2)}</h3>;
                if (line.startsWith('## ')) return <h4 key={index}>{line.slice(3)}</h4>;
                if (line.startsWith('- ')) return <p key={index}>• {line.slice(2)}</p>;
                if (!line.trim()) return <br key={index} />;
                return <p key={index}>{line}</p>;
              })}
            </div>
          ) : (
            <div className="empty-state">
              <div className="muted">No final report exists yet. Run a goal that includes narrative generation and report assembly.</div>
            </div>
          )}
        </div>

        <div className="stack">
          <div className="card">
            <div className="section-head">
              <div>
                <p className="eyebrow">Delivery Signals</p>
                <h2>Project coverage</h2>
              </div>
              <LibraryBig size={20} color="var(--accent-secondary)" />
            </div>

            <div className="stack" style={{ gap: '0.25rem' }}>
              <div className="list-row">
                <div>
                  <strong>Topic map generated</strong>
                  <div className="muted">Required for a defensible thematic discussion.</div>
                </div>
                <span className={`badge ${workspace?.readiness?.hasTopics ? 'badge-success' : 'badge-warning'}`}>
                  {workspace?.readiness?.hasTopics ? 'Yes' : 'No'}
                </span>
              </div>
              <div className="list-row">
                <div>
                  <strong>Figure pack generated</strong>
                  <div className="muted">Visual outputs are useful for both inspection and publication.</div>
                </div>
                <span className={`badge ${workspace?.readiness?.hasFigures ? 'badge-success' : 'badge-warning'}`}>
                  {workspace?.readiness?.hasFigures ? 'Yes' : 'No'}
                </span>
              </div>
              <div className="list-row">
                <div>
                  <strong>Topic refinement applied</strong>
                  <div className="muted">Manual curation coverage in the current project.</div>
                </div>
                <span className="badge badge-neutral">{workspace?.readiness?.classifiedTopics ?? 0} topics</span>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="section-head">
              <div>
                <p className="eyebrow">Snapshot</p>
                <h2>Summary metrics</h2>
              </div>
            </div>
            <div className="grid-2">
              <div className="metric-card card-flat" style={{ padding: '1rem', minHeight: 'auto' }}>
                <span className="metric-label">Papers</span>
                <strong className="metric-value" style={{ fontSize: '1.6rem' }}>{workspace?.stats?.papersFetched ?? 0}</strong>
              </div>
              <div className="metric-card card-flat" style={{ padding: '1rem', minHeight: 'auto' }}>
                <span className="metric-label">Topics</span>
                <strong className="metric-value" style={{ fontSize: '1.6rem' }}>{workspace?.stats?.uniqueTopics ?? 0}</strong>
              </div>
              <div className="metric-card card-flat" style={{ padding: '1rem', minHeight: 'auto' }}>
                <span className="metric-label">Authors</span>
                <strong className="metric-value" style={{ fontSize: '1.6rem' }}>{workspace?.stats?.keyAuthors ?? 0}</strong>
              </div>
              <div className="metric-card card-flat" style={{ padding: '1rem', minHeight: 'auto' }}>
                <span className="metric-label">Growth</span>
                <strong className="metric-value" style={{ fontSize: '1.6rem' }}>{workspace?.stats?.avgGrowthRate ?? '0%'}</strong>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="card">
        <div className="section-head">
          <div>
            <p className="eyebrow">Figure Pack</p>
            <h2>Visual evidence</h2>
          </div>
          <ImageIcon size={20} color="var(--accent-secondary)" />
        </div>

        {figures.length === 0 ? (
          <div className="empty-state">
            <div className="muted">No figures available yet.</div>
          </div>
        ) : (
          <div className="figure-grid">
            {figures.map((figure: any) => (
              <div key={figure.filename} className="card-flat" style={{ padding: '1rem' }}>
                <div className="figure-frame">
                  {figure.type === 'html' ? (
                    <div className="muted">Interactive figure: {figure.filename}</div>
                  ) : (
                    <img src={`/figures/${activeProject.id}/${figure.filename}`} alt={figure.filename} />
                  )}
                </div>
                <div style={{ marginTop: '0.9rem', display: 'flex', justifyContent: 'space-between', gap: '0.75rem' }}>
                  <div>
                    <strong>{figure.filename.replace(/\.[^.]+$/, '').replace(/_/g, ' ')}</strong>
                  </div>
                  <button className="btn btn-outline" onClick={() => window.open(`/figures/${activeProject.id}/${figure.filename}`, '_blank')}>
                    <FileText size={14} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </motion.div>
  );
};

export default Results;
