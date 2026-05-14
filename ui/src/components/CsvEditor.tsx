import { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Save, Check, AlertCircle, Loader2, FileDown } from 'lucide-react';

interface CsvEditorProps {
  projectId: string;
  filename: string;
  onSaved?: () => void;
}

const CsvEditor = ({ projectId, filename, onSaved }: CsvEditorProps) => {
  const [columns, setColumns] = useState<string[]>([]);
  const [rows, setRows] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState('');
  const [dirty, setDirty] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const resp = await fetch(`/api/${projectId}/csv/${filename}`);
      if (!resp.ok) {
        const text = await resp.text();
        throw new Error(text);
      }
      const data = await resp.json();
      setColumns(data.columns);
      setRows(data.rows);
    } catch (err: any) {
      setError(err.message);
    }
    setLoading(false);
  }, [projectId, filename]);

  useEffect(() => { load(); }, [load]);

  const updateCell = (rowIdx: number, col: string, value: string) => {
    setRows((prev) => {
      const next = [...prev];
      next[rowIdx] = { ...next[rowIdx], [col]: value };
      return next;
    });
    setDirty(true);
    setSaved(false);
  };

  const handleSave = async () => {
    setSaving(true);
    setError('');
    try {
      const resp = await fetch(`/api/${projectId}/csv/${filename}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ rows }),
      });
      if (!resp.ok) throw new Error('Save failed');
      setSaved(true);
      setDirty(false);
      onSaved?.();
      setTimeout(() => setSaved(false), 3000);
    } catch (err: any) {
      setError(err.message);
    }
    setSaving(false);
  };

  const handleDownload = () => {
    const header = columns.join(',');
    const csvRows = rows.map((r) => columns.map((c) => `"${String(r[c] || '').replace(/"/g, '""')}"`).join(','));
    const blob = new Blob([[header, ...csvRows].join('\n')], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  const classificationOptions = (col: string) => {
    if (col === 'classification') return ['', 'CORE', 'SUPPORTING', 'NOISE'];
    if (col === 'keep/remove') return ['', 'keep', 'remove'];
    return null;
  };

  if (loading) return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '1rem', color: 'var(--text-muted)' }}>
      <Loader2 size={16} className="spin" /> Loading {filename}...
    </div>
  );

  if (error) return (
    <div style={{ padding: '1rem', color: 'var(--error)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
      <AlertCircle size={16} /> {error}
    </div>
  );

  return (
    <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} style={{ overflow: 'hidden' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
        <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
          {rows.length} rows · {columns.length} columns
          {dirty && <span style={{ color: 'var(--warning)', marginLeft: '0.5rem' }}>· unsaved changes</span>}
        </span>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button className="btn btn-outline" style={{ padding: '0.3rem 0.6rem', fontSize: '0.75rem' }} onClick={handleDownload}>
            <FileDown size={14} /> Download CSV
          </button>
          <button
            className={`btn ${dirty ? 'btn-primary' : 'btn-outline'}`}
            style={{ padding: '0.3rem 0.6rem', fontSize: '0.75rem' }}
            onClick={handleSave}
            disabled={saving || !dirty}
          >
            {saving ? <Loader2 size={14} className="spin" /> : saved ? <Check size={14} /> : <Save size={14} />}
            {saving ? 'Saving...' : saved ? 'Saved!' : 'Save'}
          </button>
        </div>
      </div>

      <div style={{ overflowX: 'auto', borderRadius: '8px', border: '1px solid var(--border-color)', maxHeight: '400px', overflowY: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8rem' }}>
          <thead>
            <tr style={{ background: 'var(--bg-secondary)', position: 'sticky', top: 0, zIndex: 1 }}>
              <th style={{ padding: '0.5rem 0.75rem', borderBottom: '1px solid var(--border-color)', fontWeight: 600, textAlign: 'left', whiteSpace: 'nowrap', color: 'var(--text-muted)' }}>#</th>
              {columns.map((col) => (
                <th key={col} style={{ padding: '0.5rem 0.75rem', borderBottom: '1px solid var(--border-color)', fontWeight: 600, textAlign: 'left', whiteSpace: 'nowrap' }}>
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, rowIdx) => (
              <tr key={rowIdx} style={{ borderBottom: '1px solid var(--border-color)', background: rowIdx % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.02)' }}>
                <td style={{ padding: '0.4rem 0.75rem', color: 'var(--text-muted)', fontSize: '0.75rem' }}>{rowIdx + 1}</td>
                {columns.map((col) => {
                  const opts = classificationOptions(col);
                  const val = row[col] ?? '';
                  return (
                    <td key={col} style={{ padding: '0.25rem 0.5rem' }}>
                      {opts ? (
                        <select
                          value={val}
                          onChange={(e) => updateCell(rowIdx, col, e.target.value)}
                          style={{
                            width: '100%', background: 'var(--bg-tertiary)', border: '1px solid var(--border-color)',
                            borderRadius: '4px', padding: '0.35rem 0.5rem', color: 'var(--text-primary)', fontSize: '0.8rem',
                            cursor: 'pointer',
                          }}
                        >
                          {opts.map((o) => (
                            <option key={o} value={o}>{o || '(empty)'}</option>
                          ))}
                        </select>
                      ) : (
                        <input
                          type="text"
                          value={val}
                          onChange={(e) => updateCell(rowIdx, col, e.target.value)}
                          style={{
                            width: '100%', background: 'transparent', border: '1px solid transparent',
                            borderRadius: '4px', padding: '0.35rem 0.5rem', color: 'var(--text-primary)', fontSize: '0.8rem',
                            outline: 'none', transition: 'border-color 0.2s',
                          }}
                          onFocus={(e) => (e.target.style.borderColor = 'var(--accent-primary)')}
                          onBlur={(e) => (e.target.style.borderColor = 'transparent')}
                        />
                      )}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </motion.div>
  );
};

export default CsvEditor;
