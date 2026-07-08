import { useRef, useState, type ClipboardEvent, type FC, type KeyboardEvent } from 'react';
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
      .map((value) => value.trim().replace(/^["']|["']$/g, ''))
      .filter(Boolean);

    if (items.length === 0) return;

    const next = tags.concat(items.filter((item) => !tags.includes(item)));
    if (next.length !== tags.length) {
      onChange(next);
    }
  };

  const removeTag = (index: number) => onChange(tags.filter((_, currentIndex) => currentIndex !== index));

  const handleKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter' || event.key === ',') {
      event.preventDefault();
      commit(input);
      setInput('');
      return;
    }

    if (event.key === 'Backspace' && !input && tags.length > 0) {
      onChange(tags.slice(0, -1));
    }
  };

  const handlePaste = (event: ClipboardEvent<HTMLInputElement>) => {
    event.preventDefault();
    commit(event.clipboardData?.getData('text') || '');
  };

  const accentColor = type === 'positive' ? 'var(--accent-primary)' : 'var(--error)';
  const bgColor = type === 'positive' ? 'var(--bg-accent-soft)' : 'var(--bg-danger-soft)';
  const borderColor = type === 'positive' ? 'var(--border-strong)' : 'rgba(190, 63, 74, 0.25)';

  return (
    <div className="form-group">
      {label && <label style={{ color: accentColor }}>{label}</label>}

      <div
        className="form-control"
        onClick={() => inputRef.current?.focus()}
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: '0.4rem',
          minHeight: '52px',
          alignItems: 'center',
          padding: '0.55rem',
          cursor: 'text',
          borderColor: focused ? accentColor : undefined,
        }}
      >
        {tags.map((tag, index) => (
          <span
            key={`${tag}-${index}`}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.35rem',
              padding: '0.28rem 0.6rem 0.28rem 0.75rem',
              borderRadius: '999px',
              background: bgColor,
              color: accentColor,
              border: `1px solid ${borderColor}`,
              fontSize: '0.84rem',
              fontWeight: 600,
            }}
          >
            {tag}
            <X size={14} style={{ cursor: 'pointer' }} onClick={() => removeTag(index)} />
          </span>
        ))}

        <input
          ref={inputRef}
          type="text"
          value={input}
          onChange={(event) => setInput(event.target.value)}
          onKeyDown={handleKeyDown}
          onPaste={handlePaste}
          onFocus={() => setFocused(true)}
          onBlur={() => {
            setFocused(false);
            if (input.trim()) {
              commit(input);
              setInput('');
            }
          }}
          placeholder={tags.length === 0 ? placeholder : ''}
          style={{
            flex: 1,
            minWidth: '120px',
            border: 'none',
            outline: 'none',
            background: 'transparent',
            color: 'var(--text-primary)',
          }}
        />
      </div>

      <p style={{ margin: 0, color: 'var(--text-muted)', fontSize: '0.72rem' }}>
        Press <strong>Enter</strong> or <strong>comma</strong> to add. Paste multiple terms at once. Click x to remove.
      </p>
    </div>
  );
};

export default TagInput;
