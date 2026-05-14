import React from 'react';
import { motion } from 'framer-motion';
import { Play, CheckCircle2, Circle, AlertCircle } from 'lucide-react';

const Workflow = () => {
  const stages = [
    { id: 'scientometric', name: 'Stage 0: Data Collection', description: 'Fetch and clean base dataset from OpenAlex.', status: 'completed' },
    { id: 'advanced', name: 'Stage 1: AI Processing', description: 'Generate embeddings and initial BERTopic clusters.', status: 'completed' },
    { id: 'phase1-export', name: 'Stage 2: Topic Export', description: 'Export topic summary for manual classification.', status: 'completed' },
    { id: 'phase1-refine', name: 'Stage 3: Manual Refinement', description: 'Apply manual vetting and noise removal.', status: 'current' },
    { id: 'phase2-prepare', name: 'Stage 4: Semantic Validation', description: 'Generate theme-merging templates.', status: 'pending' },
    { id: 'phase3', name: 'Stage 5: Quantitative Analysis', description: 'Run trend, source, and network analysis.', status: 'pending' },
    { id: 'phase4', name: 'Stage 6: Interpretation', description: 'Generate narratives and temporal evolution.', status: 'pending' },
    { id: 'finalize', name: 'Stage 7: Report Generation', description: 'Consolidate all outputs into final report.', status: 'pending' },
  ];

  return (
    <motion.div 
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5 }}
    >
      <header style={{ marginBottom: '2.5rem' }}>
        <h1>Research Pipeline Workflow</h1>
        <p>Monitor and trigger each stage of your research analysis.</p>
      </header>

      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        {stages.map((stage, i) => (
          <div 
            key={stage.id} 
            style={{ 
              display: 'flex', 
              alignItems: 'center', 
              padding: '1.5rem 2rem', 
              borderBottom: i === stages.length - 1 ? 'none' : '1px solid var(--border-color)',
              background: stage.status === 'current' ? 'rgba(99, 102, 241, 0.05)' : 'transparent'
            }}
          >
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
                className={`btn ${stage.status === 'pending' || stage.status === 'current' ? 'btn-primary' : 'btn-outline'}`}
                disabled={stage.status === 'completed'}
              >
                {stage.status === 'completed' ? 'Re-run' : 'Execute Stage'}
              </button>
              {stage.status === 'current' && (
                <button className="btn btn-outline" style={{ borderColor: 'var(--warning)', color: 'var(--warning)' }}>
                  <AlertCircle size={18} />
                  Stop
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="card" style={{ marginTop: '2rem', background: 'var(--bg-tertiary)', borderStyle: 'dashed' }}>
        <h3>Pipeline Output Console</h3>
        <div style={{ 
          background: '#000', 
          borderRadius: '8px', 
          padding: '1rem', 
          fontFamily: 'monospace', 
          fontSize: '0.85rem', 
          color: '#10b981',
          height: '200px',
          overflowY: 'auto',
          marginTop: '1rem'
        }}>
          <div>[INFO] Starting Stage 3: Manual Refinement...</div>
          <div>[INFO] Loading dataset from phase1_refinement/topic_classification.csv...</div>
          <div>[SUCCESS] 42 topics identified as CORE.</div>
          <div>[SUCCESS] 10 topics identified as NOISE and removed.</div>
          <div>[INFO] Exporting final_curated_dataset.csv...</div>
          <div style={{ color: '#fff' }}>_</div>
        </div>
      </div>
    </motion.div>
  );
};

export default Workflow;
