import { useEffect, useState, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Play, CheckCircle2, Circle, Loader2, Clock, AlertCircle, Terminal, FileText,
  Globe, Layers, TrendingUp, Users, GitBranch, Search, ArrowRight, ChevronDown, ChevronUp,
} from 'lucide-react';
import { listGoals, runGoal, fetchGoalStatus, subscribeGoalLogs, fetchGoalResults, fetchStats, fetchFigures, fetchRefinementOptions, runRefinement } from '../api';
import { useProjects } from '../context/ProjectContext';
import CsvEditor from '../components/CsvEditor';

const ICON_MAP: Record<string, any> = {
  Globe, Layers, TrendingUp, Users, GitBranch, Search,
};

interface GoalDef {
  id: string; name: string; description: string; icon: string; color: string;
  outputs: string[]; supportsRefinement: boolean; estimatedMinutes: string; numSteps: number;
}

const Research = () => {
  const { activeProject } = useProjects();
  const [goals, setGoals] = useState<GoalDef[]>([]);
  const [selectedGoal, setSelectedGoal] = useState<string | null>(null);
  const [goalStatuses, setGoalStatuses] = useState<Record<string, any>>({});
  const [running, setRunning] = useState(false);
  const [progress, setProgress] = useState<{ current: number; total: number; message: string; status: string }[]>([]);
  const [results, setResults] = useState<any[] | null>(null);
  const [showDetails, setShowDetails] = useState(true);
  const [liveStats, setLiveStats] = useState<any>({});
  const [figuresCount, setFiguresCount] = useState(0);
  const [refinementOptions, setRefinementOptions] = useState<any[]>([]);
  const [refining, setRefining] = useState<string | null>(null);
  const [csvEditorOpen, setCsvEditorOpen] = useState<string | null>(null);
  const logEndRef = useRef<HTMLDivElement>(null);
  const unsubRef = useRef<(() => void) | null>(null);
  const runningRef = useRef(false);

  // Cleanup EventSource on unmount
  useEffect(() => {
    return () => { unsubRef.current?.(); };
  }, []);

  const goal = goals.find(g => g.id === selectedGoal);
  const IconComponent = goal ? ICON_MAP[goal.icon] || Play : null;

  useEffect(() => {
    if (!activeProject) return;
    listGoals(activeProject.id).then(setGoals).catch(() => {});
    fetchGoalStatus(activeProject.id).then(setGoalStatuses).catch(() => {});
    fetchStats(activeProject.id).then(setLiveStats).catch(() => {});
    fetchFigures(activeProject.id).then(f => setFiguresCount(f.length)).catch(() => {});
    fetchRefinementOptions(activeProject.id).then(setRefinementOptions).catch(() => {});
  }, [activeProject]);

  const pollStatuses = useCallback(() => {
    if (!activeProject) return;
    fetchGoalStatus(activeProject.id).then(setGoalStatuses).catch(() => {});
  }, [activeProject]);

  useEffect(() => {
    if (!activeProject) return;
    const i = setInterval(pollStatuses, 5000);
    return () => clearInterval(i);
  }, [activeProject, pollStatuses]);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [progress]);

  const handleRun = async () => {
    if (!activeProject || !selectedGoal) return;
    const pid = activeProject.id;
    unsubRef.current?.();
    runningRef.current = true;
    setRunning(true);
    setProgress([]);
    setResults(null);

    try {
      await runGoal(pid, selectedGoal);
      unsubRef.current = subscribeGoalLogs(pid,
        (ev) => { if (runningRef.current) setProgress((prev) => [...prev, ev]); },
        () => {
          runningRef.current = false;
          setRunning(false);
          unsubRef.current = null;
          fetchGoalStatus(pid).then(setGoalStatuses).catch(() => {});
          fetchGoalResults(pid).then((r) => setResults(r.results)).catch(() => {});
          fetchStats(pid).then(setLiveStats).catch(() => {});
          fetchFigures(pid).then(f => setFiguresCount(f.length)).catch(() => {});
        },
      );
    } catch (err: any) {
      setProgress((prev) => [...prev, { current: 0, total: 0, message: `Error: ${err.message}`, status: 'failed' }]);
      setRunning(false);
      runningRef.current = false;
    }
  };

  const handleRefine = async (refinementId: string) => {
    if (!activeProject) return;
    unsubRef.current?.();
    setRefining(refinementId);
    setProgress([]);
    try {
      await runRefinement(activeProject.id, refinementId);
      unsubRef.current = subscribeGoalLogs(activeProject.id,
        (ev) => { if (runningRef.current) setProgress((prev) => [...prev, ev]); },
        () => {
          setRefining(null);
          unsubRef.current = null;
          fetchRefinementOptions(activeProject.id).then(setRefinementOptions).catch(() => {});
          fetchStats(activeProject.id).then(setLiveStats).catch(() => {});
        },
      );
    } catch (err: any) {
      setProgress((prev) => [...prev, { current: 0, total: 0, message: `Error: ${err.message}`, status: 'failed' }]);
      setRefining(null);
    }
  };

  if (!activeProject) return <div className="card"><p>Select a project first.</p></div>;

  const completedCount = Object.values(goalStatuses).filter((s: any) => s?.complete).length;
  const totalGoals = goals.length;

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
      <header style={{ marginBottom: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
        <div>
          <h1>{activeProject.name} — Research</h1>
          <p>Choose a research goal to run, or re-run a completed one.</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
          <span>{completedCount}/{totalGoals} goals completed</span>
        </div>
      </header>

      {/* Goal Cards Grid */}
      <div className="grid-3" style={{ marginBottom: '2rem', gap: '1rem' }}>
        {goals.map((g) => {
          const status = goalStatuses[g.id];
          const isComplete = status?.complete;
          const isRunning = status?.running;
          const Icon = ICON_MAP[g.icon] || Play;
          const isSelected = selectedGoal === g.id;
          return (
            <motion.div
              key={g.id}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => { if (!running) { setSelectedGoal(g.id); setShowDetails(true); } }}
              className="card"
              style={{
                cursor: running ? 'default' : 'pointer',
                border: isSelected ? `2px solid ${g.color}` : '2px solid transparent',
                opacity: running && !isSelected ? 0.5 : 1,
                position: 'relative', overflow: 'hidden',
              }}
            >
              {isComplete && (
                <div style={{ position: 'absolute', top: 8, right: 8 }}>
                  <CheckCircle2 size={18} color="var(--success)" />
                </div>
              )}
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}>
                <div style={{ width: 40, height: 40, borderRadius: 10, background: `${g.color}15`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Icon size={20} color={g.color} />
                </div>
                <div>
                  <h3 style={{ margin: 0, fontSize: '1rem' }}>{g.name}</h3>
                  {status && (
                    <span style={{ fontSize: '0.75rem', color: isComplete ? 'var(--success)' : 'var(--text-muted)' }}>
                      {isComplete ? `${status.done}/${status.total} steps` : `${status.done ?? 0}/${status.total ?? g.numSteps} steps`}
                    </span>
                  )}
                </div>
              </div>
              {isSelected && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                  {(g.description ?? '').substring(0, 120)}...
                </motion.div>
              )}
            </motion.div>
          );
        })}
      </div>

      {/* Selected Goal Details */}
      <AnimatePresence>
        {goal && showDetails && (
          <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} className="card" style={{ marginBottom: '2rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                {IconComponent && <div style={{ width: 48, height: 48, borderRadius: 12, background: `${goal.color}15`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <IconComponent size={24} color={goal.color} />
                </div>}
                <div>
                  <h2 style={{ margin: 0 }}>{goal.name}</h2>
                  <p style={{ margin: '0.25rem 0 0', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                    {goal.numSteps} steps · ~{goal.estimatedMinutes} · {goal.supportsRefinement ? 'Supports refinement' : 'Fully automatic'}
                  </p>
                </div>
              </div>
              <button className="btn btn-outline" style={{ padding: '0.3rem 0.6rem', fontSize: '0.75rem' }}
                onClick={() => setShowDetails(false)}>
                <ChevronUp size={14} />
              </button>
            </div>
            <p style={{ color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: '1.5rem' }}>{goal.description}</p>
            <div className="grid-2" style={{ gap: '1rem', marginBottom: '1.5rem' }}>
              <div>
                <h4 style={{ fontSize: '0.8rem', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '0.5rem', letterSpacing: '0.05em' }}>Expected Outputs</h4>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                  {goal.outputs.map((o) => (
                    <span key={o} style={{ display: 'inline-block', padding: '0.2rem 0.6rem', borderRadius: '4px', fontSize: '0.75rem', background: 'rgba(99, 102, 241, 0.1)', color: 'var(--accent-primary)' }}>{o.replace(/_/g, ' ')}</span>
                  ))}
                </div>
              </div>
              <div>
                <h4 style={{ fontSize: '0.8rem', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '0.5rem', letterSpacing: '0.05em' }}>Execution Plan</h4>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                  {goal.numSteps} module{goal.numSteps > 1 ? 's' : ''} will run in sequence
                </div>
              </div>
            </div>
            <button
              className="btn btn-primary"
              onClick={handleRun}
              disabled={running}
              style={{ padding: '0.75rem 2rem', fontSize: '1rem', fontWeight: 600 }}
            >
              {running ? <><Loader2 size={18} className="spin" style={{ marginRight: '0.5rem' }} /> Running...</> : <><Play size={18} style={{ marginRight: '0.5rem' }} /> Run Goal</>}
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Progress View */}
      {progress.length > 0 && (
        <div className="card" style={{ marginBottom: '2rem' }}>
          <h3 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            {running ? <><Loader2 size={16} className="spin" color="var(--accent-primary)" /> Executing...</> : <><CheckCircle2 size={16} color="var(--success)" /> Complete</>}
          </h3>

          {/* Module progress steps */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', marginBottom: '1.5rem' }}>
            {progress.map((p, i) => {
              const isStepActive = p.status === 'running';
              const isStepDone = p.status === 'completed';
              const isStepFailed = p.status === 'failed';
              return (
                <motion.div key={i} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }}
                  style={{
                    display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0.5rem 0.75rem', borderRadius: '8px',
                    background: isStepActive ? 'rgba(99, 102, 241, 0.08)' : isStepFailed ? 'rgba(239,68,68,0.08)' : 'transparent',
                  }}>
                  <div style={{ width: 22, display: 'flex', justifyContent: 'center' }}>
                    {isStepDone ? <CheckCircle2 size={16} color="var(--success)" /> :
                     isStepActive ? <Loader2 size={14} className="spin" color="var(--accent-primary)" /> :
                     isStepFailed ? <AlertCircle size={16} color="var(--error)" /> :
                     <Circle size={14} color="var(--text-muted)" />}
                  </div>
                  <span style={{
                    fontFamily: 'monospace', fontSize: '0.85rem', flex: 1,
                    color: isStepDone ? 'var(--success)' : isStepActive ? 'var(--accent-primary)' : isStepFailed ? 'var(--error)' : 'var(--text-muted)',
                  }}>
                    {p.message}
                  </span>
                  {isStepActive && <span style={{ fontSize: '0.75rem', color: 'var(--accent-primary)' }}>{p.current}/{p.total}</span>}
                </motion.div>
              );
            })}
            <div ref={logEndRef} />
          </div>

          {/* Results summary */}
          {results && !running && (
            <div>
              <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', marginBottom: '1rem' }}>
                {liveStats.papersFetched > 0 && (
                  <div className="card" style={{ padding: '0.75rem 1rem', flex: 1, minWidth: 120 }}>
                    <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', margin: 0, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Papers</p>
                    <p style={{ fontSize: '1.3rem', fontWeight: 700, margin: 0 }}>{liveStats.papersFetched}</p>
                  </div>
                )}
                {liveStats.uniqueTopics > 0 && (
                  <div className="card" style={{ padding: '0.75rem 1rem', flex: 1, minWidth: 120 }}>
                    <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', margin: 0, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Topics</p>
                    <p style={{ fontSize: '1.3rem', fontWeight: 700, margin: 0 }}>{liveStats.uniqueTopics}</p>
                  </div>
                )}
                {liveStats.keyAuthors > 0 && (
                  <div className="card" style={{ padding: '0.75rem 1rem', flex: 1, minWidth: 120 }}>
                    <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', margin: 0, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Authors</p>
                    <p style={{ fontSize: '1.3rem', fontWeight: 700, margin: 0 }}>{liveStats.keyAuthors}</p>
                  </div>
                )}
                {figuresCount > 0 && (
                  <div className="card" style={{ padding: '0.75rem 1rem', flex: 1, minWidth: 120 }}>
                    <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', margin: 0, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Figures</p>
                    <p style={{ fontSize: '1.3rem', fontWeight: 700, margin: 0 }}>{figuresCount}</p>
                  </div>
                )}
              </div>

              <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', marginBottom: '1.5rem' }}>
                <a href={`/${activeProject.id}/results`} className="btn btn-primary" style={{ textDecoration: 'none' }}>
                  <FileText size={16} style={{ marginRight: '0.5rem' }} /> View Full Results
                </a>
              </div>

              {/* Refinement options */}
              {refinementOptions.length > 0 && (
                <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '1.5rem' }}>
                  <h4 style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <ArrowRight size={16} /> Post-Hoc Refinement
                  </h4>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
                    Refine your results by classifying topics or merging themes. Edit the CSV files in-browser, then apply.
                  </p>
                  <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                    {refinementOptions.map((opt) => (
                      <div key={opt.id} className="card" style={{ padding: '1rem 1.25rem', flex: 1, minWidth: 240 }}>
                        <h5 style={{ margin: '0 0 0.5rem', fontSize: '0.9rem' }}>{opt.name}</h5>
                        <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>{opt.description}</p>
                        <div style={{ display: 'flex', gap: '0.5rem' }}>
                          <button className="btn btn-outline" style={{ padding: '0.4rem 0.8rem', fontSize: '0.8rem' }}
                            onClick={() => setCsvEditorOpen(csvEditorOpen === opt.csvFile ? null : opt.csvFile)}>
                            Edit CSV
                          </button>
                          <button className="btn btn-primary" style={{ padding: '0.4rem 0.8rem', fontSize: '0.8rem' }}
                            onClick={() => handleRefine(opt.id)} disabled={refining !== null}>
                            {refining === opt.id ? <><Loader2 size={12} className="spin" /> Applying...</> : 'Apply'}
                          </button>
                        </div>
                        {csvEditorOpen === opt.csvFile && activeProject && (
                          <div style={{ marginTop: '1rem' }}>
                            <CsvEditor projectId={activeProject.id} filename={opt.csvFile}
                              onSaved={() => setCsvEditorOpen(null)} />
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </motion.div>
  );
};

export default Research;
