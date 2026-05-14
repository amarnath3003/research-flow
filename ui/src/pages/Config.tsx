import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Save, RotateCcw } from 'lucide-react';

const Config = () => {
  const [config, setConfig] = useState({
    searchQuery: '("open science" OR "scholarly communication") AND ("research security" OR "cyber attack")',
    startYear: 2010,
    endYear: 2025,
    maxResults: 5000,
    email: 'researcher@example.com',
    embeddingModel: 'all-MiniLM-L6-v2',
    ollamaModel: 'gemma3:1b'
  });

  return (
    <motion.div 
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5 }}
    >
      <header style={{ marginBottom: '2.5rem' }}>
        <h1>Configuration</h1>
        <p>Define the parameters for your research project. These settings will update the Python pipeline.</p>
      </header>

      <div className="grid-2">
        <div className="card">
          <h3>Search Strategy</h3>
          <div className="form-group">
            <label>Boolean Search Query</label>
            <textarea 
              className="form-control" 
              rows={8} 
              value={config.searchQuery}
              onChange={(e) => setConfig({...config, searchQuery: e.target.value})}
              style={{ resize: 'vertical', fontFamily: 'monospace', fontSize: '0.9rem' }}
            />
          </div>
          <div className="grid-2">
            <div className="form-group">
              <label>Start Year</label>
              <input type="number" className="form-control" value={config.startYear} />
            </div>
            <div className="form-group">
              <label>End Year</label>
              <input type="number" className="form-control" value={config.endYear} />
            </div>
          </div>
        </div>

        <div className="card">
          <h3>Pipeline Settings</h3>
          <div className="form-group">
            <label>Max Results</label>
            <input type="number" className="form-control" value={config.maxResults} />
          </div>
          <div className="form-group">
            <label>User Email (for OpenAlex)</label>
            <input type="email" className="form-control" value={config.email} />
          </div>
          <div className="form-group">
            <label>Embedding Model</label>
            <select className="form-control">
              <option>all-MiniLM-L6-v2 (Fastest)</option>
              <option>all-mpnet-base-v2 (Most Accurate)</option>
            </select>
          </div>
          <div className="form-group">
            <label>Local LLM Model (Ollama)</label>
            <input type="text" className="form-control" value={config.ollamaModel} />
          </div>
          
          <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
            <button className="btn btn-primary">
              <Save size={18} />
              Save Configuration
            </button>
            <button className="btn btn-outline">
              <RotateCcw size={18} />
              Reset Defaults
            </button>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default Config;
