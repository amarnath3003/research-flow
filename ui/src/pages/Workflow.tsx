import { useEffect, useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { Play, CheckCircle2, Circle, Loader2 } from 'lucide-react';
import { fetchStatus, runStage, subscribeLogs } from '../api';

const STAGE_ORDER = ['scientometric', 'advanced', 'phase1-export', 'phase1-refine', 'phase2-prepare', 'phase2-merge', 'phase3', 'phase4', 'phase5', 'finalize'];

const STAGE_INFO: Record<string, { name: string; desc: string }> = {
  scientometric: { name: 'Stage 0: Data Collection', desc: 'Fetch and clean base dataset from OpenAlex.' },
  advanced: { name: 'Stage 1: AI Processing', desc: 'Generate embeddings and initial BERTopic clusters.' },
  'phase1-export': { name: 'Stage 2: Topic Export', desc: 'Export topic summary for manual classification.' },
  'phase1-refine': { name: 'Stage 3: Manual Refinement', desc: 'Apply manual vetting and noise removal.' },
  'phase2-prepare': { name: 'Stage 4: Semantic Validation', desc: 'Generate theme-merging templates.' },
  'phase2-merge': { name: 'Stage 5: Theme Merging', desc: 'Apply user-defined theme merges.' },
  phase3: { name: 'Stage 6: Quantitative Analysis', desc: 'Run trend, source, and network analysis.' },
  phase4: { name: 'Stage 7: Interpretation', desc: 'Generate narratives and temporal evolution.' },
  phase5: { name: 'Stage 8: Visualization', desc: 'Generate manuscript-ready figures.' },
  finalize: { name: 'Stage 9: Report Generation', desc: 'Consolidate all outputs into final report.' },
};

const Workflow = () => {
  const [status, setStatus] = useState<any>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const [running, setRunning] = useState<string | null>(null);
  const consoleRef = useRef<HTMLDivElement>(null);

  const pollStatus = () => fetchStatus().then(setStatus).catch(() => {});
  useEffect(() => { pollStatus(); const i = setInterval(pollStatus, 3000); return () => clearInterval(i); }, []);

  const handleRun = async (stage: string) => {
    setRunning(stage);
    setLogs([]);
    try {
      await runStage(stage);
      subscribeLogs(
        (line) => setLogs((prev) => [...prev, line]),
        () => { setRunning(null); pollStatus(); },
      );
      // Also poll for log lines
      const logPoller = setInterval(async () => {
        try {
          const res = await fetch('/api/logs');
          const data = await res.json();
          if (data.lines) setLogs(data.lines);
        } catch {}
      }, 1000);
      // Stop poller when done
      setTimeout(() => clearInterval(logPoller), 300000);
    } catch (err: any) {
      setLogs((prev) => [...prev, `[ERROR] ${err.message}`]);
      setRunning(null);
    }
  };

  useEffect(() => {
    if (consoleRef.current) {
      consoleRef.current.scrollTop = consoleRef.current.scrollHeight;
    }
  }, [logs]);

  const stages = STAGE_ORDER.map((id) => {
    const found = status?.stages?.find((s: any) => s.id === id);
    return {
      id,
      name: STAGE_INFO[id]?.name ?? id,
      description: STAGE_INFO[id]?.desc ?? '',
      status: found?.status ?? 'pending',
    };
  });

  return (
    <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.5 }}>
      <header style={{ marginBottom: '2.5rem' }}>
        <h1>Research Pipeline Workflow</h1>
        <p>Monitor and trigger each stage of your research analysis.</p>
      </header>

      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        {stages.map((stage, i) => (
          <div key={stage.id} style={{
            display: 'flex', alignItems: 'center', padding: '1.5rem 2rem',
            borderBottom: i === stages.length - 1 ? 'none' : '1px solid var(--border-color)',
            background: stage.status === 'current' ? 'rgba(99, 102, 241, 0.05)' : 'transparent',
          }}>
            <div style={{ marginRight: '1.5rem' }}>
              {stage.status === 'completed' && <CheckCircle2 size={24} color="var(--success)" />}
              {stage.status === 'current' && <Play size={24} color="var(--accent-primary)" />}
              {stage.status === 'pending' && <Circle size={24} color="var(--text-muted)" />}
            </div>
            <div style={{ flex: 1 }}>
              <h3 style={{ margin: 0, color: stage.status === 'pending' ? 'var(--text-muted)' : 'var(--text-primary)' }}>{stage.name}</h3>
              <p style={{ margin: 0, fontSize: '0.85rem' }}>{stage.description}</p>
            </div>
            <div style={{ display: 'flex', gap: '0.75rem' }}>
              <button
                className={`btn ${stage.status === 'completed' ? 'btn-outline' : 'btn-primary'}`}
                onClick={() => handleRun(stage.id)}
                disabled={running !== null}
              >
                {running === stage.id ? <Loader2 size={16} className="spin" /> : null}
                {running === stage.id ? 'Running...' : stage.status === 'completed' ? 'Re-run' : 'Execute Stage'}
              </button>
            </div>
          </div>
        ))}
      </div>

      <div className="card" style={{ marginTop: '2rem', background: 'var(--bg-tertiary)', borderStyle: 'dashed' }}>
        <h3>Pipeline Output Console</h3>
        <div ref={consoleRef} style={{
          background: '#000', borderRadius: '8px', padding: '1rem',
          fontFamily: 'monospace', fontSize: '0.85rem', color: '#10b981',
          height: '300px', overflowY: 'auto', marginTop: '1rem',
        }}>
          {logs.length === 0 && <div style={{ color: '#64748b' }}>Waiting for output...</div>}
          {logs.map((line, i) => <div key={i}>{line}</div>)}
          <div style={{ color: '#fff' }}>_</div>
        </div>
      </div>
    </motion.div>
  );
};

export default Workflow;
