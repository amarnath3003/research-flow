import { useEffect, useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Play, CheckCircle2, Circle, Loader2, ChevronDown, ChevronRight, Clock, Database, BarChart3, Brain, FileText, Tags, Layers, GitMerge, TrendingUp, ImageIcon, FileCheck, Trash2 } from 'lucide-react';
import { fetchStatus, runStage, subscribeLogs, fetchStats, fetchTopics, fetchFigures, resetProject } from '../api';

type StageId = typeof STAGE_ORDER[number];

const STAGE_ORDER = ['scientometric', 'advanced', 'phase1-export', 'phase1-refine', 'phase2-prepare', 'phase2-merge', 'phase3', 'phase4', 'phase5', 'finalize'] as const;

interface StageDetail {
  name: string;
  desc: string;
  icon: any;
  subScripts: string[];
  outputs: string[];
}

const STAGE_INFO: Record<StageId, StageDetail> = {
  scientometric: {
    name: 'Stage 0: Data Collection',
    desc: 'Fetch papers from OpenAlex, clean, deduplicate, and filter by relevance.',
    icon: Database,
    subScripts: ['fetch_openalex()', 'clean_dataset()', 'run_basic_analysis()', 'export_vosviewer()'],
    outputs: ['data/raw/openalex_raw.csv', 'data/cleaned/final_dataset.csv', 'outputs/figures/publication_trend.png'],
  },
  advanced: {
    name: 'Stage 1: AI Processing',
    desc: 'Generate sentence embeddings, run BERTopic clustering, build networks, AI interpretation.',
    icon: Brain,
    subScripts: ['generate_embeddings()', 'run_topic_modeling()', 'build_networks()', 'run_trend_analysis()', 'run_ai_interpretation()', 'export_diagnostics()'],
    outputs: ['data/processed/embeddings.npy', 'data/processed/topic_dataset.csv', 'models/bertopic_model', 'outputs/reports/topic_interpretations.csv'],
  },
  'phase1-export': {
    name: 'Stage 2: Topic Export',
    desc: 'Export topic classification CSV for manual labelling (CORE/SUPPORTING/NOISE).',
    icon: Tags,
    subScripts: ['export_classification.run()'],
    outputs: ['outputs/stats/topic_classification.csv'],
  },
  'phase1-refine': {
    name: 'Stage 3: Manual Refinement',
    desc: 'Apply manual classifications to remove noise and keep relevant topics.',
    icon: Layers,
    subScripts: ['refine_dataset.run()'],
    outputs: ['data/processed/final_curated_dataset.csv'],
  },
  'phase2-prepare': {
    name: 'Stage 4: Semantic Validation',
    desc: 'Generate validation report and theme-merging template for manual editing.',
    icon: GitMerge,
    subScripts: ['validate_semantics.generate_validation_report()', 'validate_semantics.generate_merge_template()'],
    outputs: ['outputs/stats/semantic_validation_report.md', 'outputs/stats/topic_merging_map.csv'],
  },
  'phase2-merge': {
    name: 'Stage 5: Theme Merging',
    desc: 'Apply user-defined theme merges to consolidate topics into 8–15 themes.',
    icon: Layers,
    subScripts: ['apply_merges.run()'],
    outputs: ['data/processed/final_thematic_dataset.csv'],
  },
  phase3: {
    name: 'Stage 6: Quantitative Analysis',
    desc: 'Run CAGR, source H-index, geopolitical mapping, and network analysis.',
    icon: BarChart3,
    subScripts: ['trends.run()', 'sources.run()', 'geopolitical.run()', 'networks.run()', 'authors.run()'],
    outputs: ['outputs/trends/trend_summary.csv', 'outputs/sources/top_sources.csv', 'outputs/networks/keyword_cooccurrence_edges.csv'],
  },
  phase4: {
    name: 'Stage 7: Interpretation',
    desc: 'Track theme evolution over time, detect burst keywords, generate narrative.',
    icon: TrendingUp,
    subScripts: ['evolution.run()', 'bursts.run()', 'narrative.run()'],
    outputs: ['outputs/evolution/theme_evolution.csv', 'outputs/bursts/burst_detection.csv', 'outputs/narrative/discussion_draft.md'],
  },
  phase5: {
    name: 'Stage 8: Visualization',
    desc: 'Generate 5 manuscript-ready figures (timeline, network, map, evolution, landscape).',
    icon: ImageIcon,
    subScripts: ['growth.run()', 'keyword_network.run()', 'collaboration.run()', 'thematic_evolution.run()', 'landscape.run()'],
    outputs: ['outputs/figures/figure1_growth_timeline.png', 'outputs/figures/figure2_keyword_network.png', 'outputs/figures/figure3_collaboration_map.html', 'outputs/figures/figure4_thematic_evolution.png', 'outputs/figures/figure5_cluster_landscape.png'],
  },
  finalize: {
    name: 'Stage 9: Report Generation',
    desc: 'Consolidate all outputs into FINAL_RESEARCH_REPORT.md and FinalOutputs/.',
    icon: FileCheck,
    subScripts: ['report_builder.run()', 'gather_outputs.run()'],
    outputs: ['FINAL_RESEARCH_REPORT.md', 'FinalOutputs/'],
  },
};

const Workflow = () => {
  const [status, setStatus] = useState<any>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const [running, setRunning] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [liveStats, setLiveStats] = useState<any>({});
  const [topicsCount, setTopicsCount] = useState<number>(0);
  const [figuresCount, setFiguresCount] = useState<number>(0);
  const consoleRef = useRef<HTMLDivElement>(null);

  const pollStatus = () => fetchStatus().then(setStatus).catch(() => {});
  useEffect(() => {
    pollStatus();
    const i = setInterval(pollStatus, 3000);
    return () => clearInterval(i);
  }, []);

  useEffect(() => {
    fetchStats().then(setLiveStats).catch(() => {});
    fetchTopics().then((t) => setTopicsCount(t.length)).catch(() => {});
    fetchFigures().then((f) => setFiguresCount(f.length)).catch(() => {});
  }, [status]);

  const handleReset = async () => {
    if (!window.confirm('WARNING: This will permanently delete ALL collected data, models, and research outputs for the current project. Continue?')) return;
    try {
      await resetProject();
      setLogs(['[SYSTEM] All project data has been cleared. Starting fresh.']);
      pollStatus();
    } catch (err: any) {
      alert(`Reset failed: ${err.message}`);
    }
  };

  const handleRun = async (stage: string) => {
    setRunning(stage);
    setLogs([]);
    setExpanded(stage);
    try {
      await runStage(stage);
      subscribeLogs(
        (line) => setLogs((prev) => [...prev, line]),
        () => { setRunning(null); pollStatus(); },
      );
      const logPoller = setInterval(async () => {
        try {
          const data = await (await fetch('/api/logs')).json();
          if (data.lines) setLogs(data.lines);
        } catch {}
      }, 1000);
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
    const info = STAGE_INFO[id];
    return { id, ...info, status: found?.status ?? 'pending' };
  });

  const toggleExpand = (id: string) => setExpanded(expanded === id ? null : id);

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
      <header style={{ marginBottom: '2.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
        <div>
          <h1>Research Pipeline Workflow</h1>
          <p>Click any stage to expand details, or hit "Execute Stage" to run it.</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
          <button 
            className="btn btn-outline" 
            style={{ borderColor: 'var(--error)', color: 'var(--error)', padding: '0.4rem 0.8rem', fontSize: '0.8rem' }}
            onClick={handleReset}
          >
            <Trash2 size={14} />
            Reset Project
          </button>
          {status && (
            <div style={{ display: 'flex', gap: '1.5rem', fontSize: '0.85rem' }}>
              <span style={{ color: 'var(--success)' }}>{status.stages?.filter((s: any) => s.status === 'completed').length ?? 0}/10 done</span>
              <span style={{ color: 'var(--text-muted)' }}>{status.progress ?? 0}%</span>
            </div>
          )}
        </div>
      </header>

      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        {stages.map((stage, i) => {
          const Icon = stage.icon;
          const isExpanded = expanded === stage.id;
          return (
            <div key={stage.id}>
              <div
                onClick={() => toggleExpand(stage.id)}
                style={{
                  display: 'flex', alignItems: 'center', padding: '1.25rem 2rem', cursor: 'pointer',
                  borderBottom: isExpanded ? 'none' : (i === stages.length - 1 ? 'none' : '1px solid var(--border-color)'),
                  background: stage.status === 'current' ? 'rgba(99, 102, 241, 0.05)' : 'transparent',
                  transition: 'background 0.2s',
                }}
                onMouseEnter={(e) => { if (stage.status !== 'current') (e.currentTarget.style.background = 'var(--bg-tertiary)'); }}
                onMouseLeave={(e) => { if (stage.status !== 'current') (e.currentTarget.style.background = 'transparent'); }}
              >
                <div style={{ marginRight: '1rem' }}>
                  {stage.status === 'completed' && <CheckCircle2 size={22} color="var(--success)" />}
                  {stage.status === 'current' && <Play size={22} color="var(--accent-primary)" />}
                  {stage.status === 'pending' && <Circle size={22} color="var(--text-muted)" />}
                </div>
                <div style={{ marginRight: '1rem', color: stage.status === 'pending' ? 'var(--text-muted)' : 'var(--accent-primary)' }}>
                  <Icon size={20} />
                </div>
                <div style={{ flex: 1 }}>
                  <h3 style={{ margin: 0, fontSize: '1rem', color: stage.status === 'pending' ? 'var(--text-muted)' : 'var(--text-primary)' }}>
                    {stage.name}
                  </h3>
                  <p style={{ margin: 0, fontSize: '0.8rem' }}>{stage.desc}</p>
                </div>
                <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
                  <button
                    className={`btn ${stage.status === 'completed' ? 'btn-outline' : 'btn-primary'}`}
                    onClick={(e) => { e.stopPropagation(); handleRun(stage.id); }}
                    disabled={running !== null}
                    style={{ padding: '0.5rem 1rem', fontSize: '0.8rem' }}
                  >
                    {running === stage.id ? <Loader2 size={14} className="spin" /> : null}
                    {running === stage.id ? 'Running...' : stage.status === 'completed' ? 'Re-run' : 'Execute'}
                  </button>
                  <div style={{ color: 'var(--text-muted)' }}>
                    {isExpanded ? <ChevronDown size={18} /> : <ChevronRight size={18} />}
                  </div>
                </div>
              </div>

              <AnimatePresence>
                {isExpanded && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.3 }}
                    style={{ overflow: 'hidden', borderBottom: i === stages.length - 1 ? 'none' : '1px solid var(--border-color)' }}
                  >
                    <div style={{ padding: '1.5rem 2rem 2rem', background: 'var(--bg-tertiary)' }}>
                      {/* Sub-scripts */}
                      <div style={{ marginBottom: '1.5rem' }}>
                        <h4 style={{ fontSize: '0.8rem', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '0.75rem', letterSpacing: '0.05em' }}>
                          <Play size={14} style={{ marginRight: '0.5rem', verticalAlign: 'middle' }} />
                          Sub-scripts executed
                        </h4>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                          {stage.subScripts.map((s, idx) => (
                            <span key={idx} style={{
                              background: 'var(--bg-secondary)', padding: '0.4rem 0.75rem',
                              borderRadius: '6px', fontSize: '0.8rem', fontFamily: 'monospace',
                              border: '1px solid var(--border-color)',
                              color: running === stage.id ? 'var(--accent-primary)' : 'var(--text-secondary)',
                            }}>
                              {s}
                            </span>
                          ))}
                        </div>
                      </div>

                      {/* Output files + enrichment cards */}
                      <div className="grid-2" style={{ gap: '1rem' }}>
                        <div>
                          <h4 style={{ fontSize: '0.8rem', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '0.75rem', letterSpacing: '0.05em' }}>
                            <FileText size={14} style={{ marginRight: '0.5rem', verticalAlign: 'middle' }} />
                            Output Files
                          </h4>
                          <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                            {stage.outputs.map((f, idx) => (
                              <li key={idx} style={{
                                padding: '0.35rem 0', fontSize: '0.8rem', fontFamily: 'monospace',
                                color: stage.status === 'completed' ? 'var(--success)' : 'var(--text-muted)',
                                display: 'flex', alignItems: 'center', gap: '0.5rem',
                              }}>
                                {stage.status === 'completed' ? <CheckCircle2 size={12} /> : <Circle size={12} />}
                                {f}
                              </li>
                            ))}
                          </ul>
                        </div>

                        {/* Enrichment: live data snapshot */}
                        <div>
                          <h4 style={{ fontSize: '0.8rem', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '0.75rem', letterSpacing: '0.05em' }}>
                            <BarChart3 size={14} style={{ marginRight: '0.5rem', verticalAlign: 'middle' }} />
                            Live Data Snapshot
                          </h4>
                          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                            {stage.id === 'scientometric' && (
                              <>
                                <DataRow label="Papers fetched" value={liveStats.papersFetched ?? '—'} />
                                <DataRow label="Authors extracted" value={liveStats.keyAuthors ?? '—'} />
                              </>
                            )}
                            {stage.id === 'advanced' && (
                              <>
                                <DataRow label="Topics discovered" value={liveStats.uniqueTopics ?? '—'} />
                                <DataRow label="AI interpretations" value={liveStats.uniqueTopics ? `${liveStats.uniqueTopics} topics` : '—'} />
                              </>
                            )}
                            {stage.id === 'phase1-export' && (
                              <DataRow label="Topics to classify" value={topicsCount || liveStats.uniqueTopics || '—'} />
                            )}
                            {(stage.id === 'phase1-refine' || stage.id === 'phase2-merge') && (
                              <DataRow label="Unique topics" value={liveStats.uniqueTopics ?? '—'} />
                            )}
                            {stage.id === 'phase2-prepare' && (
                              <DataRow label="Topics for merging" value={liveStats.uniqueTopics ?? '—'} />
                            )}
                            {stage.id === 'phase3' && (
                              <>
                                <DataRow label="Growth rate" value={liveStats.avgGrowthRate ?? '—'} />
                                <DataRow label="Papers analyzed" value={liveStats.papersFetched ?? '—'} />
                              </>
                            )}
                            {stage.id === 'phase4' && (
                              <DataRow label="Topics tracked" value={liveStats.uniqueTopics ?? '—'} />
                            )}
                            {stage.id === 'phase5' && (
                              <DataRow label="Figures generated" value={figuresCount} />
                            )}
                            {stage.id === 'finalize' && (
                              <>
                                <DataRow label="Figures" value={figuresCount} />
                                <DataRow label="Papers in report" value={liveStats.papersFetched ?? '—'} />
                              </>
                            )}
                            {!['scientometric', 'advanced', 'phase1-export', 'phase1-refine', 'phase2-prepare', 'phase2-merge', 'phase3', 'phase4', 'phase5', 'finalize'].includes(stage.id) && (
                              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                                Run this stage to populate data.
                              </div>
                            )}
                          </div>
                        </div>
                      </div>

                      {/* Console for running stage */}
                      {running === stage.id && (
                        <div style={{ marginTop: '1.5rem' }}>
                          <h4 style={{ fontSize: '0.8rem', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
                            <Clock size={14} style={{ marginRight: '0.5rem', verticalAlign: 'middle' }} />
                            Console Output
                          </h4>
                          <div ref={consoleRef} style={{
                            background: '#000', borderRadius: '8px', padding: '0.75rem',
                            fontFamily: 'monospace', fontSize: '0.8rem', color: '#10b981',
                            height: '180px', overflowY: 'auto',
                          }}>
                            {logs.length === 0 && <span style={{ color: '#64748b' }}>Waiting...</span>}
                            {logs.map((line, i) => <div key={i}>{line}</div>)}
                          </div>
                        </div>
                      )}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          );
        })}
      </div>
    </motion.div>
  );
};

const DataRow = ({ label, value }: { label: string; value: any }) => (
  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', padding: '0.3rem 0', borderBottom: '1px solid var(--border-color)' }}>
    <span style={{ color: 'var(--text-muted)' }}>{label}</span>
    <span style={{ color: 'var(--text-primary)', fontWeight: 600 }}>{value}</span>
  </div>
);

export default Workflow;
