/* eslint-disable @typescript-eslint/no-explicit-any, react-hooks/set-state-in-effect */
import { useCallback, useEffect, useState } from 'react';
import { Check, FileDown, Loader2, Save, TriangleAlert } from 'lucide-react';

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
  const [dirty, setDirty] = useState(false);
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    setLoading(true);
    setError('');

    try {
      const response = await fetch(`/api/${projectId}/csv/${filename}`);
      if (!response.ok) {
        throw new Error(await response.text());
      }

      const payload = await response.json();
      setColumns(payload.columns);
      setRows(payload.rows);
    } catch (reason: any) {
      setError(reason.message);
    } finally {
      setLoading(false);
    }
  }, [filename, projectId]);

  useEffect(() => {
    load();
  }, [load]);

  const updateCell = (rowIndex: number, column: string, value: string) => {
    setRows((current) => {
      const next = [...current];
      next[rowIndex] = { ...next[rowIndex], [column]: value };
      return next;
    });
    setDirty(true);
    setSaved(false);
  };

  const handleSave = async () => {
    setSaving(true);
    setError('');

    try {
      const response = await fetch(`/api/${projectId}/csv/${filename}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ rows }),
      });

      if (!response.ok) {
        throw new Error(await response.text());
      }

      setSaved(true);
      setDirty(false);
      onSaved?.();
      setTimeout(() => setSaved(false), 2500);
    } catch (reason: any) {
      setError(reason.message);
    } finally {
      setSaving(false);
    }
  };

  const handleDownload = () => {
    const header = columns.join(',');
    const serializedRows = rows.map((row) =>
      columns.map((column) => `"${String(row[column] ?? '').replace(/"/g, '""')}"`).join(','),
    );
    const blob = new Blob([[header, ...serializedRows].join('\n')], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
  };

  const optionsFor = (column: string) => {
    if (column === 'classification') return ['', 'CORE', 'SUPPORTING', 'NOISE'];
    if (column === 'keep/remove') return ['', 'keep', 'remove'];
    return null;
  };

  if (loading) {
    return (
      <div className="query-box" style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
        <Loader2 size={16} className="spin" />
        Loading {filename}…
      </div>
    );
  }

  if (error) {
    return (
      <div className="query-box" style={{ color: 'var(--error)', display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
        <TriangleAlert size={16} />
        {error}
      </div>
    );
  }

  return (
    <div className="stack">
      <div className="list-row" style={{ padding: 0 }}>
        <div className="muted">
          {rows.length} rows · {columns.length} columns
          {dirty ? ' · unsaved changes' : ''}
        </div>
        <div className="inline-list">
          <button className="btn btn-outline" onClick={handleDownload}>
            <FileDown size={14} />
            Download
          </button>
          <button className={`btn ${dirty ? 'btn-primary' : 'btn-outline'}`} onClick={handleSave} disabled={saving || !dirty}>
            {saving ? <Loader2 size={14} className="spin" /> : saved ? <Check size={14} /> : <Save size={14} />}
            {saving ? 'Saving…' : saved ? 'Saved' : 'Save'}
          </button>
        </div>
      </div>

      <div className="table-shell" style={{ maxHeight: '24rem' }}>
        <table>
          <thead>
            <tr>
              <th>#</th>
              {columns.map((column) => <th key={column}>{column}</th>)}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, rowIndex) => (
              <tr key={rowIndex}>
                <td>{rowIndex + 1}</td>
                {columns.map((column) => {
                  const options = optionsFor(column);
                  const value = row[column] ?? '';

                  return (
                    <td key={`${rowIndex}-${column}`}>
                      {options ? (
                        <select
                          className="form-control"
                          value={value}
                          onChange={(event) => updateCell(rowIndex, column, event.target.value)}
                          style={{ minWidth: '9rem', padding: '0.55rem 0.75rem' }}
                        >
                          {options.map((option) => (
                            <option key={option} value={option}>{option || '(empty)'}</option>
                          ))}
                        </select>
                      ) : (
                        <input
                          className="form-control"
                          type="text"
                          value={value}
                          onChange={(event) => updateCell(rowIndex, column, event.target.value)}
                          style={{ minWidth: '12rem', padding: '0.55rem 0.75rem' }}
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
    </div>
  );
};

export default CsvEditor;
