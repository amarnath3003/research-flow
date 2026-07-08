/* eslint-disable @typescript-eslint/no-explicit-any */
import { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import {
  ArrowRight,
  CheckCircle2,
  Circle,
  Compass,
  Loader2,
  Play,
  WandSparkles,
} from 'lucide-react';
import { fetchGoalResults, fetchWorkspace, runGoal, runRefinement, subscribeGoalLogs } from '../api';
import { useProjects } from '../context/ProjectContext';
import CsvEditor from '../components/CsvEditor';

const ICONS: Record<string, any> = {
  Globe: Compass,
  Layers: WandSparkles,
  TrendingUp: ArrowRight,
  Users: Compass,
  GitBranch: ArrowRight,
  Search: Compass,
};

const Research = () => {
  const { activeProject } = useProjects();
  const [workspace, setWorkspace] = useState<any>(null);
  const [selectedGoal, setSelectedGoal] = useState<string | null>(null);
  const [progress, setProgress] = useState<any[]>([]);
  const [results, setResults] = useState<any[]>([]);
  const [runningId, setRunningId] = useState<string | null>(null);
  const [csvEditorOpen, setCsvEditorOpen] = useState<string | null>(null);
  const [error, setError] = useState('');
  const logEndRef = useRef<HTMLDivElement | null>(null);
  const unsubRef = useRef<(() => void) | null>(null);

  useEffect(() => {
    return () => unsubRef.current?.();
  }, []);

  useEffect(() => {
    if (!activeProject) return;
    fetchWorkspace(activeProject.id)
      .then((response) => {
        setWorkspace(response);
        setSelectedGoal((current: string | null) => current ?? response.goals?.[0]?.id ?? null);
      })
      .catch((reason: Error) => setError(reason.message));
  }, [activeProject]);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }, [progress]);

  if (!activeProject) {
    return <div className="card">Select a project first.</div>;
  }

  const refreshWorkspace = async () => {
    const response = await fetchWorkspace(activeProject.id);
    setWorkspace(response);
    return response;
  };

  const selected = workspace?.goals?.find((goal: any) => goal.id === selectedGoal) ?? workspace?.goals?.[0];

  const startRun = async (kind: 'goal' | 'refinement', id: string) => {
    unsubRef.current?.();
    setError('');
    setProgress([]);
    setResults([]);
    setRunningId(id);

    const pid = activeProject.id;

    try {
      if (kind === 'goal') {
        await runGoal(pid, id);
      } else {
        await runRefinement(pid, id);
      }

      unsubRef.current = subscribeGoalLogs(
        pid,
        (event) => setProgress((current) => [...current, event]),
        async () => {
          setRunningId(null);
          unsubRef.current = null;
          const [workspaceResponse, resultResponse] = await Promise.all([
            refreshWorkspace(),
            fetchGoalResults(pid),
          ]);
          setResults(resultResponse.results ?? []);
          if (!selectedGoal) {
            setSelectedGoal(workspaceResponse.goals?.[0]?.id ?? null);
          }
        },
      );
    } catch (reason: any) {
      setError(reason.message);
      setRunningId(null);
    }
  };

  return (
    <motion.div className="page" initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }}>
      <section className="card hero-card" style={{ marginBottom: '1rem' }}>
        <p className="eyebrow">Research Lab</p>
        <h1>Run focused analyses, then refine them with editorial control.</h1>
        <p className="lede" style={{ maxWidth: '54rem', marginTop: '0.9rem' }}>
          This is the execution room for the project. Pick a goal that matches the research question, monitor the module chain, then edit classification and merge files only when the evidence says refinement is needed.
        </p>
        <div className="inline-list" style={{ marginTop: '1.1rem' }}>
          <span className={`badge ${workspace?.readiness?.configured ? 'badge-success' : 'badge-warning'}`}>
            {workspace?.readiness?.configured ? 'Ready for execution' : 'Setup incomplete'}
          </span>
          <span className="badge badge-neutral">{workspace?.stats?.papersFetched ?? 0} papers</span>
          <span className="badge badge-neutral">{workspace?.stats?.uniqueTopics ?? 0} topics</span>
        </div>
      </section>

      <section className="grid-3" style={{ marginBottom: '1rem' }}>
        {(workspace?.goals ?? []).map((goal: any) => {
          const Icon = ICONS[goal.icon] ?? WandSparkles;
          const isSelected = selected?.id === goal.id;
          const status = goal.status ?? {};

          return (
            <button
              key={goal.id}
              className={`card goal-card ${isSelected ? 'selected' : ''}`}
              onClick={() => setSelectedGoal(goal.id)}
              style={{ textAlign: 'left' }}
              disabled={Boolean(runningId)}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', gap: '0.75rem' }}>
                <span className="goal-icon" style={{ background: `${goal.color}22`, color: goal.color }}>
                  <Icon size={22} />
                </span>
                <span className={`badge ${status.complete ? 'badge-success' : status.running ? 'badge-warning' : 'badge-neutral'}`}>
                  {status.running ? 'Running' : status.complete ? 'Complete' : `${goal.numSteps} steps`}
                </span>
              </div>
              <div>
                <h3>{goal.name}</h3>
                <p className="muted" style={{ marginTop: '0.45rem' }}>{goal.description}</p>
              </div>
              <div className="inline-list">
                {(goal.outputs ?? []).slice(0, 3).map((output: string) => (
                  <span key={output} className="pill">{output.replace(/_/g, ' ')}</span>
                ))}
              </div>
            </button>
          );
        })}
      </section>

      {selected && (
        <section className="grid-2" style={{ marginBottom: '1rem' }}>
          <div className="card">
            <div className="section-head">
              <div>
                <p className="eyebrow">Selected Goal</p>
                <h2>{selected.name}</h2>
                <p className="muted">{selected.estimatedMinutes} minutes · {selected.numSteps} modules</p>
              </div>
            </div>

            <p className="muted" style={{ marginBottom: '1rem' }}>{selected.description}</p>

            <div className="query-box" style={{ marginBottom: '1rem' }}>
              {workspace?.config?.searchQuery || 'No query configured yet.'}
            </div>

            <div className="inline-list" style={{ marginBottom: '1rem' }}>
              {(selected.outputs ?? []).map((output: string) => (
                <span key={output} className="pill">{output.replace(/_/g, ' ')}</span>
              ))}
            </div>

            <button
              className="btn btn-primary"
              onClick={() => startRun('goal', selected.id)}
              disabled={Boolean(runningId) || !workspace?.readiness?.configured}
            >
              {runningId === selected.id ? <Loader2 size={16} className="spin" /> : <Play size={16} />}
              {runningId === selected.id ? 'Running goal…' : 'Run this goal'}
            </button>
          </div>

          <div className="card">
            <div className="section-head">
              <div>
                <p className="eyebrow">Execution Log</p>
                <h2>Live module chain</h2>
              </div>
            </div>

            {progress.length === 0 ? (
              <div className="empty-state">
                <div className="muted">Start a goal or refinement to stream progress events here.</div>
              </div>
            ) : (
              <div className="log-box" style={{ maxHeight: '26rem', overflow: 'auto' }}>
                <div className="stack" style={{ gap: '0.45rem' }}>
                  {progress.map((item, index) => {
                    const isDone = item.status === 'completed';
                    const isRunning = item.status === 'running';
                    const isFailed = item.status === 'failed';
                    return (
                      <div key={`${item.message}-${index}`} className="checklist-item">
                        {isDone ? (
                          <CheckCircle2 size={16} color="var(--success)" />
                        ) : isRunning ? (
                          <Loader2 size={16} className="spin" color="var(--accent-primary)" />
                        ) : isFailed ? (
                          <Circle size={16} color="var(--error)" />
                        ) : (
                          <Circle size={16} color="var(--text-muted)" />
                        )}
                        <div style={{ flex: 1 }}>
                          <strong>{item.message}</strong>
                          <div className="muted">{item.current}/{item.total}</div>
                        </div>
                      </div>
                    );
                  })}
                  <div ref={logEndRef} />
                </div>
              </div>
            )}
          </div>
        </section>
      )}

      <section className="grid-2" style={{ marginBottom: '1rem' }}>
        <div className="card">
          <div className="section-head">
            <div>
              <p className="eyebrow">Refinement</p>
              <h2>Post-run editorial controls</h2>
              <p className="muted">Use these only after reviewing the first topic map.</p>
            </div>
          </div>

          {(workspace?.refinements ?? []).length === 0 ? (
            <div className="empty-state">
              <div className="muted">No refinement files are available yet. Run a goal with topic modeling first.</div>
            </div>
          ) : (
            <div className="stack">
              {workspace.refinements.map((option: any) => (
                <div key={option.id} className="card-flat" style={{ padding: '1rem' }}>
                  <div className="list-row" style={{ padding: 0 }}>
                    <div>
                      <strong>{option.name}</strong>
                      <div className="muted">{option.description}</div>
                    </div>
                    <div className="inline-list">
                      <button
                        className="btn btn-outline"
                        onClick={() => setCsvEditorOpen((current) => current === option.csvFile ? null : option.csvFile)}
                      >
                        Edit CSV
                      </button>
                      <button
                        className="btn btn-primary"
                        onClick={() => startRun('refinement', option.id)}
                        disabled={Boolean(runningId)}
                      >
                        {runningId === option.id ? <Loader2 size={16} className="spin" /> : <Play size={16} />}
                        Apply
                      </button>
                    </div>
                  </div>

                  {csvEditorOpen === option.csvFile && (
                    <div style={{ marginTop: '1rem' }}>
                      <CsvEditor projectId={activeProject.id} filename={option.csvFile} />
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="card">
          <div className="section-head">
            <div>
              <p className="eyebrow">Latest Outcome</p>
              <h2>Run summary</h2>
            </div>
          </div>

          {results.length === 0 ? (
            <div className="empty-state">
              <div className="muted">No completed run summary yet.</div>
            </div>
          ) : (
            <div className="stack" style={{ gap: '0.35rem' }}>
              {results.map((result: any) => (
                <div key={`${result.module}-${result.status}`} className="list-row">
                  <div>
                    <strong>{result.module}</strong>
                    {result.error && <div className="muted">{result.error}</div>}
                  </div>
                  <span className={`badge ${result.status === 'completed' ? 'badge-success' : 'badge-danger'}`}>
                    {result.status}
                  </span>
                </div>
              ))}
            </div>
          )}

          <div style={{ marginTop: '1rem' }}>
            <a href={`/${activeProject.id}/results`} className="btn btn-outline">
              Open Report Room
              <ArrowRight size={16} />
            </a>
          </div>
        </div>
      </section>

      {error && (
        <section className="card" style={{ color: 'var(--error)' }}>
          {error}
        </section>
      )}
    </motion.div>
  );
};

export default Research;
