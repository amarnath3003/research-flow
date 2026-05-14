import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Save, Check } from 'lucide-react';
import { fetchConfig, saveConfig as apiSaveConfig } from '../api';

const Config = () => {
  const [config, setConfig] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchConfig()
      .then(data => { setConfig(data); setLoading(false); })
      .catch(err => { setError(err.message); setLoading(false); });
  }, []);

  const handleSave = async () => {
    try {
      setError('');
      await apiSaveConfig(config);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err: any) {
      setError(err.message);
    }
  };

  const update = (key: string, value: any) => setConfig((prev: any) => ({ ...prev, [key]: value }));

  if (loading) return <div className="card">Loading configuration...</div>;
  if (error && !config) return <div className="card" style={{ color: 'var(--error)' }}>Error: {error}</div>;

  return (
    <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.5 }}>
      <header style={{ marginBottom: '2.5rem' }}>
        <h1>Configuration</h1>
        <p>Define the parameters for your research project. These settings update the Python pipeline.</p>
      </header>

      <div className="grid-2">
        <div className="card">
          <h3>Search Strategy</h3>
          <div className="form-group">
            <label>Boolean Search Query</label>
            <textarea
              className="form-control"
              rows={8}
              value={config.searchQuery ?? ''}
              onChange={(e) => update('searchQuery', e.target.value)}
              style={{ resize: 'vertical', fontFamily: 'monospace', fontSize: '0.9rem' }}
            />
          </div>
          <div className="grid-2">
            <div className="form-group">
              <label>Start Year</label>
              <input type="number" className="form-control" value={config.startYear ?? 2010} onChange={(e) => update('startYear', parseInt(e.target.value) || 2010)} />
            </div>
            <div className="form-group">
              <label>End Year</label>
              <input type="number" className="form-control" value={config.endYear ?? 2025} onChange={(e) => update('endYear', parseInt(e.target.value) || 2025)} />
            </div>
          </div>
          <div className="form-group">
            <label>Research Description</label>
            <textarea
              className="form-control"
              rows={3}
              value={config.description ?? ''}
              onChange={(e) => update('description', e.target.value)}
            />
          </div>
        </div>

        <div className="card">
          <h3>Pipeline Settings</h3>
          <div className="form-group">
            <label>Max Results</label>
            <input type="number" className="form-control" value={config.maxResults ?? 5000} onChange={(e) => update('maxResults', parseInt(e.target.value) || 5000)} />
          </div>
          <div className="form-group">
            <label>User Email (for OpenAlex)</label>
            <input type="email" className="form-control" value={config.email ?? ''} onChange={(e) => update('email', e.target.value)} />
          </div>
          <div className="form-group">
            <label>Embedding Model</label>
            <select className="form-control" value={config.embeddingModel ?? 'all-MiniLM-L6-v2'} onChange={(e) => update('embeddingModel', e.target.value)}>
              <option value="all-MiniLM-L6-v2">all-MiniLM-L6-v2 (Fastest)</option>
              <option value="all-mpnet-base-v2">all-mpnet-base-v2 (Most Accurate)</option>
            </select>
          </div>
          <div className="form-group">
            <label>Min Topic Size</label>
            <input type="number" className="form-control" value={config.minTopicSize ?? 10} onChange={(e) => update('minTopicSize', parseInt(e.target.value) || 10)} />
          </div>
          <div className="form-group">
            <label>LLM Provider</label>
            <select className="form-control" value={config.llmProvider ?? ''} onChange={(e) => update('llmProvider', e.target.value || null)}>
              <option value="">Disabled</option>
              <option value="ollama">Ollama (Local)</option>
              <option value="openai">OpenAI</option>
              <option value="anthropic">Anthropic</option>
            </select>
          </div>
          <div className="form-group">
            <label>LLM Model</label>
            <input type="text" className="form-control" value={config.llmModel ?? ''} onChange={(e) => update('llmModel', e.target.value || null)} placeholder="e.g. gemma3:1b, gpt-4" />
          </div>

          {error && <p style={{ color: 'var(--error)', fontSize: '0.85rem' }}>{error}</p>}
          <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
            <button className="btn btn-primary" onClick={handleSave}>
              {saved ? <Check size={18} /> : <Save size={18} />}
              {saved ? 'Saved!' : 'Save Configuration'}
            </button>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default Config;
