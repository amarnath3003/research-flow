import { useState } from 'react';
import { X } from 'lucide-react';
import type { KeyboardEvent } from 'react';

interface TagInputProps {
  tags: string[];
  onChange: (tags: string[]) => void;
  placeholder?: string;
  label?: string;
  type?: 'positive' | 'negative';
}

const TagInput: React.FC<TagInputProps> = ({ tags, onChange, placeholder, label, type = 'positive' }) => {
  const [input, setInput] = useState('');

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === ' ' || e.key === 'Enter') {
      e.preventDefault();
      addTag();
    } else if (e.key === 'Backspace' && !input && tags.length > 0) {
      removeTag(tags.length - 1);
    }
  };

  const addTag = () => {
    const trimmed = input.trim().replace(/^,+|,+$/g, '');
    if (trimmed && !tags.includes(trimmed)) {
      onChange([...tags, trimmed]);
      setInput('');
    }
  };

  const removeTag = (index: number) => {
    onChange(tags.filter((_, i) => i !== index));
  };

  const accentColor = type === 'positive' ? 'var(--accent-primary)' : 'var(--error)';
  const bgColor = type === 'positive' ? 'rgba(0, 33, 71, 0.05)' : 'rgba(114, 28, 36, 0.05)';

  return (
    <div className="form-group">
      {label && <label style={{ color: accentColor }}>{label}</label>}
      <div 
        className="form-control" 
        style={{ 
          display: 'flex', 
          flexWrap: 'wrap', 
          gap: '0.5rem', 
          minHeight: '48px', 
          alignItems: 'center',
          padding: '0.5rem'
        }}
      >
        {tags.map((tag, i) => (
          <span 
            key={i} 
            style={{ 
              display: 'inline-flex', 
              alignItems: 'center', 
              gap: '0.25rem',
              backgroundColor: bgColor,
              color: accentColor,
              padding: '0.25rem 0.6rem',
              borderRadius: '4px',
              fontSize: '0.85rem',
              fontWeight: 600,
              border: `1px solid ${accentColor}20`
            }}
          >
            {tag}
            <X 
              size={14} 
              style={{ cursor: 'pointer' }} 
              onClick={() => removeTag(i)} 
            />
          </span>
        ))}
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          onBlur={addTag}
          placeholder={tags.length === 0 ? placeholder : ''}
          style={{ 
            border: 'none', 
            outline: 'none', 
            flex: 1, 
            minWidth: '120px', 
            background: 'transparent',
            fontSize: '0.95rem',
            color: 'var(--text-primary)'
          }}
        />
      </div>
    </div>
  );
};

export default TagInput;
