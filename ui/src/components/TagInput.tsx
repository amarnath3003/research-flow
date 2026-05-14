import { useState, useRef, type FC, type KeyboardEvent, type ClipboardEvent } from 'react';
import { X } from 'lucide-react';

interface TagInputProps {
  tags: string[];
  onChange: (tags: string[]) => void;
  placeholder?: string;
  label?: string;
  type?: 'positive' | 'negative';
}

const TagInput: FC<TagInputProps> = ({ tags, onChange, placeholder, label, type = 'positive' }) => {
  const [input, setInput] = useState('');
  const [focused, setFocused] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const commit = (raw: string) => {
    const items = raw
      .split(/[,;]/)
      .map(s => s.trim().replace(/^["']|["']$/g, ''))
      .filter(Boolean);
    if (items.length === 0) return;
    const newTags = tags.concat(items.filter(t => !tags.includes(t)));
    if (newTags.length !== tags.length) onChange(newTags);
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault();
      commit(input);
      setInput('');
    } else if (e.key === 'Backspace' && !input && tags.length > 0) {
      onChange(tags.slice(0, -1));
    }
  };

  const handlePaste = (e: ClipboardEvent<HTMLInputElement>) => {
    e.preventDefault();
    const pasted = e.clipboardData?.getData('text') || '';
    commit(pasted);
  };

  const removeTag = (index: number) => onChange(tags.filter((_, i) => i !== index));

  const accentColor = type === 'positive' ? 'var(--accent-primary)' : 'var(--error)';
  const bgColor = type === 'positive' ? 'rgba(99, 102, 241, 0.08)' : 'rgba(239, 68, 68, 0.08)';
  const borderColor = type === 'positive' ? 'rgba(99, 102, 241, 0.25)' : 'rgba(239, 68, 68, 0.25)';

  return (
    <div className="form-group">
      {label && <label style={{ color: accentColor, fontWeight: 600 }}>{label}</label>}
      <div
        onClick={() => inputRef.current?.focus()}
        className="form-control"
        style={{
          display: 'flex', flexWrap: 'wrap', gap: '0.4rem',
          minHeight: '48px', alignItems: 'center', padding: '0.5rem',
          cursor: 'text', borderColor: focused ? accentColor : undefined,
          transition: 'border-color 0.2s',
        }}
      >
        {tags.map((tag, i) => (
          <span
            key={i}
            style={{
              display: 'inline-flex', alignItems: 'center', gap: '0.3rem',
              backgroundColor: bgColor, color: accentColor,
              padding: '0.25rem 0.5rem 0.25rem 0.7rem',
              borderRadius: '20px', fontSize: '0.85rem', fontWeight: 500,
              border: `1px solid ${borderColor}`,
              animation: 'fadeIn 0.2s ease-out',
            }}
          >
            {tag}
            <X size={14} style={{ cursor: 'pointer', opacity: 0.7, flexShrink: 0 }} onClick={() => removeTag(i)} />
          </span>
        ))}
        <input
          ref={inputRef}
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          onPaste={handlePaste}
          onFocus={() => setFocused(true)}
          onBlur={() => { setFocused(false); if (input.trim()) { commit(input); setInput(''); } }}
          placeholder={tags.length === 0 ? placeholder : ''}
          style={{
            border: 'none', outline: 'none', flex: 1, minWidth: '120px',
            background: 'transparent', fontSize: '0.9rem', color: 'var(--text-primary)',
          }}
        />
      </div>
      <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.3rem', marginBottom: 0 }}>
        Press <strong>Enter</strong> or <strong>comma</strong> to add · Paste multiple terms at once · Click × to remove
      </p>
    </div>
  );
};

export default TagInput;
