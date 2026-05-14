import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Save, Check } from 'lucide-react';
import { fetchConfig, saveConfig as apiSaveConfig } from '../api';
import { useProjects } from '../context/ProjectContext';
import TagInput from '../components/TagInput';

const Config = () => {
  const { activeProject } = useProjects();
  const [config, setConfig] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState('');

  // Derived state for tags
  const [includeTerms, setIncludeTerms] = useState<string[]>([]);
  const [excludeTerms, setExcludeTerms] = useState<string[]>([]);

  useEffect(() => {
    if (!activeProject) return;
    setLoading(true);
    fetchConfig(activeProject.id)
      .then(data => { 
        setConfig(data); 
        setLoading(false);
        // Parse current query into tags if it exists
        // This is a simplified parser for (A AND B) NOT (C OR D)
        const query = data.searchQuery || '';
        const parts = query.split(/ NOT /i);
        const pos = parts[0]?.replace(/[()]/g, '').split(/ AND /i).map((s: string) => s.trim()).filter(Boolean);
        const neg = parts[1]?.replace(/[()]/g, '').split(/ OR /i).map((s: string) => s.trim()).filter(Boolean);
        setIncludeTerms(pos || []);
        setExcludeTerms(neg || []);
      })
      .catch(err => { setError(err.message); setLoading(false); });
  }, [activeProject]);

  const handleSave = async () => {
    if (!activeProject) return;
    try {
      setError('');
      // Build structured query
      let query = '';
      if (includeTerms.length > 0) {
        query = `(${includeTerms.join(' AND ')})`;
      }
      if (excludeTerms.length > 0) {
        query += ` NOT (${excludeTerms.join(' OR ')})`;
      }
      
      const payload = { ...config, searchQuery: query };
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
    <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.5 }}>
      <header style={{ marginBottom: '2.5rem' }}>
        <h1>{activeProject.name} — Configuration</h1>
        <p>These settings update the Python pipeline for this project.</p>
      </header>

      <div className="grid-2">
        <div className="card">
          <h3>Search Strategy</h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1.5rem' }}>
            Terms are combined into a Boolean query. Press <strong>Space</strong> or <strong>Enter</strong> to add a term.
          </p>
          
          <TagInput 
            label="Included Research Terms" 
            tags={includeTerms} 
            onChange={setIncludeTerms} 
            placeholder="e.g. scientometrics, open access" 
            type="positive"
          />

          <TagInput 
            label="Excluded Terms (Negative)" 
            tags={excludeTerms} 
            onChange={setExcludeTerms} 
            placeholder="e.g. medical, hardware" 
            type="negative"
          />

          <div className="grid-2" style={{ marginTop: '2rem' }}>
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
            <textarea className="form-control" rows={3} value={config.description ?? ''}
              onChange={(e) => update('description', e.target.value)} />
          </div>
        </div>

        <div className="card">
          <h3>Pipeline Settings</h3>
          <div className="form-group">
            <label>Max Results</label>
            <input type="number" className="form-control" value={config.maxResults ?? 5000}
              onChange={(e) => update('maxResults', parseInt(e.target.value) || 5000)} />
          </div>
          <div className="form-group">
            <label>Email (OpenAlex API)</label>
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
              <option value="ollama">Ollama</option>
              <option value="openai">OpenAI</option>
              <option value="anthropic">Anthropic</option>
            </select>
          </div>
          <div className="form-group">
            <label>LLM Model</label>
            <input type="text" className="form-control" value={config.llmModel ?? ''}
              onChange={(e) => update('llmModel', e.target.value || null)}
              placeholder="e.g. gemma3:1b, gpt-4" />
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
