/* eslint-disable @typescript-eslint/no-explicit-any */
import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Check, Eye, Save, Settings2, Sparkles } from 'lucide-react';
import { fetchConfig, fetchWorkspace, saveConfig } from '../api';
import { useProjects } from '../context/ProjectContext';
import TagInput from '../components/TagInput';

const Config = () => {
  const { activeProject } = useProjects();
  const [config, setConfig] = useState<any>(null);
  const [workspace, setWorkspace] = useState<any>(null);
  const [includeTerms, setIncludeTerms] = useState<string[]>([]);
  const [excludeTerms, setExcludeTerms] = useState<string[]>([]);
  const [rawMode, setRawMode] = useState(false);
  const [rawQuery, setRawQuery] = useState('');
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!activeProject) return;

    Promise.all([fetchConfig(activeProject.id), fetchWorkspace(activeProject.id)])
      .then(([configResponse, workspaceResponse]) => {
        setConfig(configResponse);
        setWorkspace(workspaceResponse);
        setIncludeTerms(configResponse.includeTerms ?? []);
        setExcludeTerms(configResponse.excludeTerms ?? []);
        setRawQuery(configResponse.searchQuery ?? '');
      })
      .catch((reason: Error) => setError(reason.message));
  }, [activeProject]);

  if (!activeProject) {
    return <div className="card">Select a project first.</div>;
  }

  if (!config) {
    return <div className="card">Loading setup…</div>;
  }

  const updateConfig = (key: string, value: any) => {
    setConfig((current: any) => ({ ...current, [key]: value }));
  };

  const generatedQuery = (() => {
    const parts: string[] = [];
    if (includeTerms.length > 0) {
      parts.push(`(${includeTerms.map((term) => /^\w+$/.test(term) ? term : `"${term}"`).join(' AND ')})`);
    }
    if (excludeTerms.length > 0) {
      parts.push(`NOT (${excludeTerms.map((term) => /^\w+$/.test(term) ? term : `"${term}"`).join(' OR ')})`);
    }
    return parts.join(' ');
  })();

  const handleSave = async () => {
    if (!activeProject) return;
    setSaving(true);
    setError('');

    try {
      const payload = {
        ...config,
        searchQuery: rawMode ? rawQuery : generatedQuery,
        includeTerms,
        excludeTerms,
      };
      await saveConfig(activeProject.id, payload);
      setSaved(true);
      setTimeout(() => setSaved(false), 2500);
      const refreshed = await fetchWorkspace(activeProject.id);
      setWorkspace(refreshed);
    } catch (reason: any) {
      setError(reason.message);
    } finally {
      setSaving(false);
    }
  };

  const missing = workspace?.readiness?.missing ?? [];

  return (
    <motion.div className="page" initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }}>
      <section className="card hero-card" style={{ marginBottom: '1rem' }}>
        <p className="eyebrow">Study Setup</p>
        <h1>Define the research brief before you spend compute.</h1>
        <p className="lede" style={{ maxWidth: '52rem', marginTop: '0.9rem' }}>
          This page should answer three questions clearly: what literature you want, what you want excluded, and how deep the pipeline should go.
        </p>

        <div className="inline-list" style={{ marginTop: '1.2rem' }}>
          <span className={`badge ${workspace?.readiness?.configured ? 'badge-success' : 'badge-warning'}`}>
            {workspace?.readiness?.configured ? 'Ready to run' : 'Still missing requirements'}
          </span>
          <span className="badge badge-neutral">{includeTerms.length} include terms</span>
          <span className="badge badge-neutral">{excludeTerms.length} exclusion terms</span>
        </div>
      </section>

      <section className="two-up">
        <div className="stack">
          <div className="card">
            <div className="section-head">
              <div>
                <p className="eyebrow">Search Design</p>
                <h2>Build the retrieval logic</h2>
              </div>
              <Settings2 size={20} color="var(--accent-primary)" />
            </div>

            <TagInput
              label="Include terms"
              tags={includeTerms}
              onChange={setIncludeTerms}
              placeholder="e.g. meta research, open science, research integrity"
              type="positive"
            />

            <TagInput
              label="Exclude terms"
              tags={excludeTerms}
              onChange={setExcludeTerms}
              placeholder="e.g. clinical, agriculture, blockchain"
              type="negative"
            />

            <div className="grid-2">
              <div className="form-group">
                <label>Start year</label>
                <input
                  className="form-control"
                  type="number"
                  value={config.startYear ?? 2010}
                  onChange={(event) => updateConfig('startYear', Number(event.target.value) || 2010)}
                />
              </div>
              <div className="form-group">
                <label>End year</label>
                <input
                  className="form-control"
                  type="number"
                  value={config.endYear ?? 2025}
                  onChange={(event) => updateConfig('endYear', Number(event.target.value) || 2025)}
                />
              </div>
            </div>

            <div className="form-group">
              <label>Research brief</label>
              <textarea
                className="form-control"
                rows={4}
                value={config.description ?? ''}
                onChange={(event) => updateConfig('description', event.target.value)}
                placeholder="Explain the field boundary, why it matters, and what the later narrative should emphasize."
              />
            </div>
          </div>

          <div className="card">
            <div className="section-head">
              <div>
                <p className="eyebrow">Advanced Controls</p>
                <h2>Pipeline settings</h2>
              </div>
            </div>

            <div className="form-group">
              <label>Maximum records</label>
              <input
                className="form-control"
                type="number"
                value={config.maxResults ?? 5000}
                onChange={(event) => updateConfig('maxResults', Number(event.target.value) || 5000)}
              />
            </div>

            <div className="form-group">
              <label>Email for OpenAlex</label>
              <input
                className="form-control"
                type="email"
                value={config.email ?? ''}
                onChange={(event) => updateConfig('email', event.target.value)}
                placeholder="name@example.com"
              />
            </div>

            <div className="grid-2">
              <div className="form-group">
                <label>Embedding model</label>
                <select
                  className="form-control"
                  value={config.embeddingModel ?? 'all-MiniLM-L6-v2'}
                  onChange={(event) => updateConfig('embeddingModel', event.target.value)}
                >
                  <option value="all-MiniLM-L6-v2">all-MiniLM-L6-v2</option>
                  <option value="all-mpnet-base-v2">all-mpnet-base-v2</option>
                </select>
              </div>
              <div className="form-group">
                <label>Minimum topic size</label>
                <input
                  className="form-control"
                  type="number"
                  value={config.minTopicSize ?? 10}
                  onChange={(event) => updateConfig('minTopicSize', Number(event.target.value) || 10)}
                />
              </div>
            </div>

            <div className="grid-2">
              <div className="form-group">
                <label>LLM provider</label>
                <select
                  className="form-control"
                  value={config.llmProvider ?? ''}
                  onChange={(event) => updateConfig('llmProvider', event.target.value || null)}
                >
                  <option value="">Disabled</option>
                  <option value="ollama">Ollama</option>
                  <option value="openai">OpenAI</option>
                  <option value="anthropic">Anthropic</option>
                </select>
              </div>
              <div className="form-group">
                <label>LLM model</label>
                <input
                  className="form-control"
                  type="text"
                  value={config.llmModel ?? ''}
                  onChange={(event) => updateConfig('llmModel', event.target.value || null)}
                  placeholder="e.g. gemma3:4b"
                />
              </div>
            </div>
          </div>
        </div>

        <div className="stack">
          <div className="card">
            <div className="section-head">
              <div>
                <p className="eyebrow">Query Preview</p>
                <h2>Inspect the final boolean query</h2>
              </div>
              <button className="btn btn-outline" onClick={() => setRawMode((value) => !value)}>
                <Eye size={16} />
                {rawMode ? 'Use builder' : 'Edit raw'}
              </button>
            </div>

            {rawMode ? (
              <textarea
                className="form-control"
                rows={8}
                value={rawQuery}
                onChange={(event) => setRawQuery(event.target.value)}
              />
            ) : (
              <div className="query-box" style={{ minHeight: '12rem' }}>
                {generatedQuery || 'Add include terms to generate a boolean query.'}
              </div>
            )}

            <div style={{ marginTop: '1rem', display: 'flex', gap: '0.75rem' }}>
              <button className="btn btn-primary btn-block" onClick={handleSave} disabled={saving}>
                {saving ? <Sparkles size={16} className="spin" /> : saved ? <Check size={16} /> : <Save size={16} />}
                {saving ? 'Saving…' : saved ? 'Saved' : 'Save setup'}
              </button>
            </div>

            {error && <p style={{ color: 'var(--error)', marginTop: '0.8rem' }}>{error}</p>}
          </div>

          <div className="card">
            <div className="section-head">
              <div>
                <p className="eyebrow">Run Readiness</p>
                <h2>Pre-flight checklist</h2>
              </div>
            </div>

            <div className="stack" style={{ gap: '0.25rem' }}>
              <div className="list-row">
                <div>
                  <strong>Search query present</strong>
                  <div className="muted">The pipeline needs an explicit boolean query or query-builder output.</div>
                </div>
                <span className={`badge ${workspace?.config?.searchQuery ? 'badge-success' : 'badge-warning'}`}>
                  {workspace?.config?.searchQuery ? 'Yes' : 'No'}
                </span>
              </div>
              <div className="list-row">
                <div>
                  <strong>Contact email</strong>
                  <div className="muted">Required to use OpenAlex politely and avoid throttling.</div>
                </div>
                <span className={`badge ${workspace?.config?.email ? 'badge-success' : 'badge-warning'}`}>
                  {workspace?.config?.email ? 'Provided' : 'Missing'}
                </span>
              </div>
              <div className="list-row">
                <div>
                  <strong>Advanced model path</strong>
                  <div className="muted">Optional, but useful when you want richer narrative interpretation.</div>
                </div>
                <span className="badge badge-neutral">
                  {workspace?.config?.llmProvider ? `${workspace.config.llmProvider}/${workspace.config.llmModel || 'default'}` : 'Disabled'}
                </span>
              </div>
            </div>

            {missing.length > 0 && (
              <div className="query-box" style={{ marginTop: '1rem' }}>
                {missing.map((item: string) => `• ${item}`).join('\n')}
              </div>
            )}
          </div>
        </div>
      </section>
    </motion.div>
  );
};

export default Config;
