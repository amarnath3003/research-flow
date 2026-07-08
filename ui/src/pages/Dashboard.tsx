/* eslint-disable @typescript-eslint/no-explicit-any */
import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, CheckCircle2, Compass, FlaskConical, Settings2, Sparkles } from 'lucide-react';
import { fetchWorkspace } from '../api';
import { useProjects } from '../context/ProjectContext';

const Dashboard = () => {
  const { activeProject } = useProjects();
  const [workspace, setWorkspace] = useState<any>(null);

  useEffect(() => {
    if (!activeProject) return;
    fetchWorkspace(activeProject.id).then(setWorkspace).catch(() => {});
  }, [activeProject]);

  if (!activeProject) {
    return <div className="card">Select a project first.</div>;
  }

  const readiness = workspace?.readiness;
  const stats = workspace?.stats ?? {};
  const goals = workspace?.goals ?? [];
  const nextAction = !readiness?.configured
    ? { label: 'Finish setup', href: `/${activeProject.id}/config`, icon: Settings2 }
    : !readiness?.hasDataset
      ? { label: 'Run first analysis', href: `/${activeProject.id}/research`, icon: Sparkles }
      : { label: 'Inspect evidence', href: `/${activeProject.id}/explorer`, icon: Compass };
  const NextIcon = nextAction.icon;

  return (
    <motion.div className="page" initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }}>
      <section className="card hero-card" style={{ marginBottom: '1rem' }}>
        <p className="eyebrow">Research Overview</p>
        <h1>{activeProject.name}</h1>
        <p className="lede" style={{ maxWidth: '52rem', marginTop: '0.9rem' }}>
          {activeProject.description || 'This workspace turns a broad literature question into a traceable pipeline of search, topic discovery, field mapping, refinement, and reporting.'}
        </p>

        <div className="inline-list" style={{ marginTop: '1.2rem' }}>
          <span className={`badge ${readiness?.configured ? 'badge-success' : 'badge-warning'}`}>
            {readiness?.configured ? 'Research brief ready' : 'Setup incomplete'}
          </span>
          <span className="badge badge-neutral">{stats.papersFetched ?? 0} papers</span>
          <span className="badge badge-neutral">{stats.uniqueTopics ?? 0} topics</span>
          <span className="badge badge-neutral">{workspace?.figuresPreview?.length ?? 0} preview figures</span>
        </div>

        <div className="two-up" style={{ marginTop: '1.4rem' }}>
          <div className="query-box">
            <div className="section-head">
              <div>
                <p className="eyebrow">Current Search Logic</p>
                <h3>Study scope</h3>
              </div>
            </div>
            {workspace?.config?.searchQuery ? workspace.config.searchQuery : 'No search query has been configured yet.'}
          </div>

          <div className="card-flat" style={{ padding: '1rem 1.1rem' }}>
            <p className="eyebrow">Best Next Step</p>
            <h3 style={{ marginBottom: '0.5rem' }}>{nextAction.label}</h3>
            <p className="muted" style={{ marginBottom: '1rem' }}>
              {!readiness?.configured
                ? 'Define the search strategy and pipeline settings before you spend compute on analysis.'
                : !readiness?.hasDataset
                  ? 'Run a goal that matches the research question and generate the first evidence pack.'
                  : 'Review topics, trends, and artifacts before writing or exporting the report.'}
            </p>
            <a className="btn btn-primary" href={nextAction.href}>
              <NextIcon size={16} />
              {nextAction.label}
            </a>
          </div>
        </div>
      </section>

      <section className="grid-4" style={{ marginBottom: '1rem' }}>
        <div className="card metric-card">
          <span className="metric-label">Corpus Size</span>
          <strong className="metric-value">{stats.papersFetched ?? 0}</strong>
          <span className="metric-meta">Records currently available for analysis.</span>
        </div>
        <div className="card metric-card">
          <span className="metric-label">Topic Count</span>
          <strong className="metric-value">{stats.uniqueTopics ?? 0}</strong>
          <span className="metric-meta">Machine-discovered themes in the current corpus.</span>
        </div>
        <div className="card metric-card">
          <span className="metric-label">Researcher Graph</span>
          <strong className="metric-value">{stats.keyAuthors ?? 0}</strong>
          <span className="metric-meta">Unique authors detected in the processed dataset.</span>
        </div>
        <div className="card metric-card">
          <span className="metric-label">Growth Signal</span>
          <strong className="metric-value">{stats.avgGrowthRate ?? '0%'}</strong>
          <span className="metric-meta">Aggregate publication growth pulled from trend outputs.</span>
        </div>
      </section>

      <section className="grid-2" style={{ marginBottom: '1rem' }}>
        <div className="card">
          <div className="section-head">
            <div>
              <p className="eyebrow">Journey</p>
              <h2>Project flow</h2>
              <p className="muted">A strong run should move through these checkpoints without guesswork.</p>
            </div>
          </div>
          <div className="checklist">
            <div className="checklist-item">
              <Settings2 size={18} color="var(--accent-primary)" />
              <div>
                <strong>1. Scope the study</strong>
                <div className="muted">Clarify search logic, years, exclusions, and AI settings.</div>
              </div>
            </div>
            <div className="checklist-item">
              <Sparkles size={18} color="var(--accent-primary)" />
              <div>
                <strong>2. Run the right goal</strong>
                <div className="muted">Choose a full landscape map, quick scan, experts view, or evolution pass.</div>
              </div>
            </div>
            <div className="checklist-item">
              <Compass size={18} color="var(--accent-primary)" />
              <div>
                <strong>3. Inspect the evidence</strong>
                <div className="muted">Use topics, tables, and figures to validate whether the field map makes sense.</div>
              </div>
            </div>
            <div className="checklist-item">
              <FlaskConical size={18} color="var(--accent-primary)" />
              <div>
                <strong>4. Refine and report</strong>
                <div className="muted">Classify noise, merge themes, then review the narrative and visuals.</div>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="section-head">
            <div>
              <p className="eyebrow">Readiness</p>
              <h2>Operational status</h2>
            </div>
          </div>

          <div className="stack" style={{ gap: '0.25rem' }}>
            {(readiness?.missing ?? []).length === 0 ? (
              <div className="list-row">
                <div style={{ display: 'flex', gap: '0.75rem' }}>
                  <CheckCircle2 size={18} color="var(--success)" />
                  <div>
                    <strong>Workspace configured</strong>
                    <div className="muted">The app has enough information to run research goals.</div>
                  </div>
                </div>
              </div>
            ) : (
              readiness.missing.map((item: string) => (
                <div key={item} className="list-row">
                  <div>
                    <strong>{item}</strong>
                    <div className="muted">Resolve this in Setup before running new goals.</div>
                  </div>
                </div>
              ))
            )}
            <div className="list-row">
              <div>
                <strong>Classified topics</strong>
                <div className="muted">Manual refinement coverage across topic outputs.</div>
              </div>
              <strong>{readiness?.classifiedTopics ?? 0}</strong>
            </div>
            <div className="list-row">
              <div>
                <strong>Report available</strong>
                <div className="muted">Narrative package ready for inspection or export.</div>
              </div>
              <strong>{readiness?.hasReport ? 'Yes' : 'No'}</strong>
            </div>
          </div>
        </div>
      </section>

      <section className="grid-2">
        <div className="card">
          <div className="section-head">
            <div>
              <p className="eyebrow">Research Goals</p>
              <h2>What this workspace can produce</h2>
            </div>
            <a href={`/${activeProject.id}/research`} className="btn btn-outline">
              Open Lab
              <ArrowRight size={16} />
            </a>
          </div>
          <div className="stack" style={{ gap: '0.2rem' }}>
            {goals.slice(0, 4).map((goal: any) => (
              <div key={goal.id} className="list-row">
                <div>
                  <strong>{goal.name}</strong>
                  <div className="muted">{goal.description}</div>
                </div>
                <span className={`badge ${goal.status?.complete ? 'badge-success' : goal.status?.running ? 'badge-warning' : 'badge-neutral'}`}>
                  {goal.status?.running ? 'Running' : goal.status?.complete ? 'Complete' : `${goal.numSteps} steps`}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <div className="section-head">
            <div>
              <p className="eyebrow">Topic Preview</p>
              <h2>Leading themes</h2>
            </div>
            <a href={`/${activeProject.id}/explorer`} className="btn btn-outline">
              Open Explorer
              <ArrowRight size={16} />
            </a>
          </div>

          {workspace?.topicsPreview?.length ? (
            <div className="stack" style={{ gap: '0.2rem' }}>
              {workspace.topicsPreview.map((topic: any) => (
                <div key={topic.id} className="list-row">
                  <div>
                    <strong>{topic.label || `Topic ${topic.id}`}</strong>
                    <div className="muted">Topic #{topic.id}</div>
                  </div>
                  <span className="badge badge-neutral">{topic.count} papers</span>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <div className="muted">No topic preview yet. Run a goal that includes topic modeling to populate this area.</div>
            </div>
          )}
        </div>
      </section>
    </motion.div>
  );
};

export default Dashboard;
