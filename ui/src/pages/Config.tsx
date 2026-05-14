import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Save, Check, RotateCcw } from 'lucide-react';
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
              value={config.searchQuery || ''}
              onChange={(e) => update('searchQuery', e.target.value)}
              style={{ resize: 'vertical', fontFamily: 'monospace', fontSize: '0.9rem' }}
            />
          </div>
          <div className="grid-2">
            <div className="form-group">
              <label>Start Year</label>
              <input 
                type="number" 
                className="form-control" 
                value={config.startYear} 
                onChange={(e) => update('startYear', parseInt(e.target.value))}
              />
            </div>
            <div className="form-group">
              <label>End Year</label>
              <input 
                type="number" 
                className="form-control" 
                value={config.endYear} 
                onChange={(e) => update('endYear', parseInt(e.target.value))}
              />
            </div>
          </div>
          <div className="form-group">
            <label>Research Description</label>
            <textarea 
              className="form-control" 
              rows={3} 
              value={config.description || ''}
              onChange={(e) => update('description', e.target.value)}
            />
          </div>
        </div>

        <div className="card">
          <h3>Pipeline Settings</h3>
          <div className="form-group">
            <label>Max Results</label>
            <input 
              type="number" 
              className="form-control" 
              value={config.maxResults} 
              onChange={(e) => update('maxResults', parseInt(e.target.value))}
            />
          </div>
          <div className="form-group">
            <label>User Email (for OpenAlex)</label>
            <input 
              type="email" 
              className="form-control" 
              value={config.email || ''} 
              onChange={(e) => update('email', e.target.value)}
            />
          </div>
          <div className="form-group">
            <label>Embedding Model</label>
            <select 
              className="form-control" 
              value={config.embeddingModel} 
              onChange={(e) => update('embeddingModel', e.target.value)}
            >
              <option value="all-MiniLM-L6-v2">all-MiniLM-L6-v2 (Fastest)</option>
              <option value="all-mpnet-base-v2">all-mpnet-base-v2 (Most Accurate)</option>
            </select>
          </div>
          <div className="form-group">
            <label>Min Topic Size</label>
            <input 
              type="number" 
              className="form-control" 
              value={config.minTopicSize} 
              onChange={(e) => update('minTopicSize', parseInt(e.target.value))}
            />
          </div>
          <div className="form-group">
            <label>Local LLM Model (Ollama)</label>
            <input 
              type="text" 
              className="form-control" 
              value={config.llmModel || ''} 
              onChange={(e) => update('llmModel', e.target.value)}
              placeholder="e.g. gemma3:1b"
            />
          </div>
          
          <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
            <button className="btn btn-primary" onClick={handleSave} disabled={saved}>
              {saved ? <Check size={18} /> : <Save size={18} />}
              {saved ? 'Saved!' : 'Save Configuration'}
            </button>
            <button className="btn btn-outline" onClick={() => window.location.reload()}>
              <RotateCcw size={18} />
              Reset
            </button>
          </div>
          {error && <p style={{ color: 'var(--error)', marginTop: '1rem' }}>{error}</p>}
        </div>
      </div>
    </motion.div>
  );
};

export default Config;
