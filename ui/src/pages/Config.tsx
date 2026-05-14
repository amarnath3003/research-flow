import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Save, Check, Eye, Edit3, Target, Globe, Layers, TrendingUp, Users, GitBranch, Search } from 'lucide-react';
import { fetchConfig, saveConfig as apiSaveConfig, listGoals } from '../api';
import { useProjects } from '../context/ProjectContext';
import TagInput from '../components/TagInput';

const GOAL_ICONS: Record<string, any> = {
  Globe, Layers, TrendingUp, Users, GitBranch, Search,
};

const Config = () => {
  const { activeProject } = useProjects();
  const [config, setConfig] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState('');
  const [showRaw, setShowRaw] = useState(false);
  const [rawQuery, setRawQuery] = useState('');
  const [goals, setGoals] = useState<any[]>([]);
  const [selectedGoal, setSelectedGoal] = useState<string>('landscape');

  const [includeTerms, setIncludeTerms] = useState<string[]>([]);
  const [excludeTerms, setExcludeTerms] = useState<string[]>([]);

  useEffect(() => {
    if (!activeProject) return;
    setLoading(true);
    Promise.all([
      fetchConfig(activeProject.id),
      listGoals(activeProject.id),
    ])
      .then(([data, goalList]) => {
        setConfig(data);
        setGoals(goalList);
        setLoading(false);
        // Use stored arrays if available, otherwise parse from query string
        if (data.includeTerms?.length) {
          setIncludeTerms(data.includeTerms);
        } else if (data.searchQuery) {
          const parts = (data.searchQuery ?? '').split(/ NOT /i);
          const pos = parts[0]?.replace(/[()]/g, '').split(/ AND /i).map((s: string) => s.trim().replace(/^"|"$/g, '')).filter(Boolean);
          setIncludeTerms(pos || []);
          const neg = parts[1]?.replace(/[()]/g, '').split(/ OR /i).map((s: string) => s.trim().replace(/^"|"$/g, '')).filter(Boolean);
          setExcludeTerms(neg || []);
        }
        setRawQuery(data.searchQuery || '');
      })
      .catch(err => { setError(err.message); setLoading(false); });
  }, [activeProject]);

  // Build live preview
  const generatedQuery = (() => {
    const parts: string[] = [];
    if (includeTerms.length) parts.push(`(${includeTerms.map(t => /^\w+$/.test(t) ? t : `"${t}"`).join(' AND ')})`);
    if (excludeTerms.length) parts.push(`NOT (${excludeTerms.map(t => /^\w+$/.test(t) ? t : `"${t}"`).join(' OR ')})`);
    return parts.join(' ');
  })();

  const handleSave = async () => {
    if (!activeProject) return;
    try {
      setError('');
      const finalQuery = showRaw ? rawQuery : generatedQuery;
      const payload = {
        ...config,
        searchQuery: finalQuery,
        includeTerms,
        excludeTerms,
      };
      await apiSaveConfig(activeProject.id, payload);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err: any) { setError(err.message); }
  };

  const update = (key: string, value: any) => setConfig((prev: any) => ({ ...prev, [key]: value }));

  if (!activeProject) return <div className="card"><p>Select a project first.</p></div>;
  if (loading) return <div className="card">Loading configuration...</div>;
  if (error && !config) return <div className="card" style={{ color: 'var(--error)' }}>Error: {error}</div>;

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
      <header style={{ marginBottom: '2rem' }}>
        <h1>{activeProject.name} — Research Setup</h1>
        <p>Configure your search strategy and select a research goal.</p>
      </header>

      {/* Goal Selector */}
      {goals.length > 0 && (
        <div className="card" style={{ marginBottom: '2rem' }}>
          <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
            <Target size={18} color="var(--accent-primary)" /> Research Goal
          </h3>
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            {goals.map((g) => {
              const Icon = GOAL_ICONS[g.icon] || Target;
              const isSelected = selectedGoal === g.id;
              return (
                <button
                  key={g.id}
                  onClick={() => setSelectedGoal(g.id)}
                  style={{
                    display: 'flex', alignItems: 'center', gap: '0.5rem',
                    padding: '0.6rem 1rem', borderRadius: '8px', border: isSelected ? `2px solid ${g.color}` : '1px solid var(--border-color)',
                    background: isSelected ? `${g.color}10` : 'var(--bg-secondary)',
                    color: isSelected ? g.color : 'var(--text-primary)',
                    cursor: 'pointer', fontSize: '0.85rem', fontWeight: isSelected ? 600 : 400,
                    transition: 'all 0.2s',
                  }}
                >
                  <Icon size={16} />
                  {g.name}
                </button>
              );
            })}
          </div>
          {selectedGoal && goals.find(g => g.id === selectedGoal) && (
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.75rem', lineHeight: 1.5 }}>
              {goals.find(g => g.id === selectedGoal)?.description}
            </p>
          )}
        </div>
      )}

      <div className="grid-2">
        {/* LEFT: Search Strategy */}
        <div className="card">
          <h3>Search Strategy</h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1.5rem' }}>
            Type a term and press <strong>Enter</strong> or <strong>,</strong> to add a capsule.
            Multi-word phrases are auto-quoted. Paste a comma-separated list to add many at once.
          </p>

          <TagInput
            label="Include (must match ALL of these)"
            tags={includeTerms}
            onChange={setIncludeTerms}
            placeholder="e.g. open science, research security, scientometrics"
            type="positive"
          />

          <TagInput
            label="Exclude (remove papers mentioning these)"
            tags={excludeTerms}
            onChange={setExcludeTerms}
            placeholder="e.g. medical, blockchain, smart farming"
            type="negative"
          />

          <div className="grid-2" style={{ marginTop: '1.5rem' }}>
            <div className="form-group">
              <label>Start Year</label>
              <input type="number" className="form-control" value={config.startYear ?? 2010}
                onChange={(e) => update('startYear', parseInt(e.target.value) || 2010)} />
            </div>
            <div className="form-group">
              <label>End Year</label>
              <input type="number" className="form-control" value={config.endYear ?? 2025}
                onChange={(e) => update('endYear', parseInt(e.target.value) || 2025)} />
            </div>
          </div>

          <div className="form-group">
            <label>Research Description</label>
            <textarea className="form-control" rows={2} value={config.description ?? ''}
              onChange={(e) => update('description', e.target.value)}
              placeholder="Brief description for AI interpretation prompts..." />
          </div>
        </div>

        {/* RIGHT: Preview + Pipeline Settings */}
        <div>
          {/* Query Preview */}
          <div className="card" style={{ borderColor: 'var(--accent-primary)', borderStyle: 'solid', borderWidth: '1px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <h3 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Eye size={18} color="var(--accent-primary)" />
                Generated Query
              </h3>
              <button
                className="btn btn-outline"
                style={{ padding: '0.3rem 0.6rem', fontSize: '0.75rem' }}
                onClick={() => { setShowRaw(!showRaw); if (!showRaw) setRawQuery(generatedQuery); }}
              >
                <Edit3 size={14} style={{ marginRight: '0.3rem' }} />
                {showRaw ? 'Use Capsules' : 'Edit Raw'}
              </button>
            </div>

            {showRaw ? (
              <textarea
                className="form-control"
                rows={4}
                value={rawQuery}
                onChange={(e) => setRawQuery(e.target.value)}
                style={{ fontFamily: 'monospace', fontSize: '0.85rem', resize: 'vertical' }}
              />
            ) : (
              <div style={{
                background: 'var(--bg-tertiary)', borderRadius: '8px', padding: '1rem',
                fontFamily: 'monospace', fontSize: '0.85rem', lineHeight: 1.6,
                minHeight: '80px', color: generatedQuery ? 'var(--text-primary)' : 'var(--text-muted)',
                wordBreak: 'break-word',
              }}>
                {generatedQuery || 'Add include terms above to see the query...'}
              </div>
            )}

            <div style={{ display: 'flex', gap: '0.75rem', marginTop: '1rem' }}>
              <button className="btn btn-primary" onClick={handleSave} style={{ flex: 1 }}>
                {saved ? <Check size={18} /> : <Save size={18} />}
                {saved ? 'Saved!' : 'Save Configuration'}
              </button>
            </div>
            {error && <p style={{ color: 'var(--error)', fontSize: '0.85rem', marginTop: '0.5rem' }}>{error}</p>}
          </div>

          {/* Pipeline Settings */}
          <div className="card" style={{ marginTop: '1.5rem' }}>
            <h3>Pipeline Settings</h3>
            <div className="form-group">
              <label>Max Results</label>
              <input type="number" className="form-control" value={config.maxResults ?? 5000}
                onChange={(e) => update('maxResults', parseInt(e.target.value) || 5000)} />
            </div>
            <div className="form-group">
              <label>Email (OpenAlex API — polite pool)</label>
              <input type="email" className="form-control" value={config.email ?? ''}
                onChange={(e) => update('email', e.target.value)} />
            </div>
            <div className="form-group">
              <label>Embedding Model</label>
              <select className="form-control" value={config.embeddingModel ?? 'all-MiniLM-L6-v2'}
                onChange={(e) => update('embeddingModel', e.target.value)}>
                <option value="all-MiniLM-L6-v2">all-MiniLM-L6-v2 (Fastest)</option>
                <option value="all-mpnet-base-v2">all-mpnet-base-v2 (Most Accurate)</option>
              </select>
            </div>
            <div className="form-group">
              <label>Min Topic Size</label>
              <input type="number" className="form-control" value={config.minTopicSize ?? 10}
                onChange={(e) => update('minTopicSize', parseInt(e.target.value) || 10)} />
            </div>
            <div className="form-group">
              <label>LLM Provider</label>
              <select className="form-control" value={config.llmProvider ?? ''}
                onChange={(e) => update('llmProvider', e.target.value || null)}>
                <option value="">Disabled</option>
                <option value="ollama">Ollama (Local)</option>
                <option value="openai">OpenAI</option>
                <option value="anthropic">Anthropic</option>
              </select>
            </div>
            <div className="form-group">
              <label>LLM Model</label>
              <input type="text" className="form-control" value={config.llmModel ?? ''}
                onChange={(e) => update('llmModel', e.target.value || null)}
                placeholder="e.g. gemma3:1b, gpt-4, claude-3" />
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default Config;
