import { Sun, Moon } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';
import { motion, AnimatePresence } from 'framer-motion';

const ThemeToggle = () => {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className="btn btn-outline"
      style={{
        width: '100%',
        justifyContent: 'flex-start',
        gap: '1rem',
        padding: '0.85rem 1.25rem',
        border: 'none',
        background: 'transparent',
        color: 'var(--text-secondary)',
        fontSize: '0.95rem',
        fontWeight: 500,
        position: 'relative',
        overflow: 'hidden'
      }}
      aria-label="Toggle theme"
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', width: '100%' }}>
        <div style={{ position: 'relative', width: 20, height: 20 }}>
          <AnimatePresence mode="wait">
            {theme === 'light' ? (
              <motion.div
                key="sun"
                initial={{ opacity: 0, rotate: -90, scale: 0.5 }}
                animate={{ opacity: 1, rotate: 0, scale: 1 }}
                exit={{ opacity: 0, rotate: 90, scale: 0.5 }}
                transition={{ duration: 0.2 }}
                style={{ position: 'absolute', top: 0, left: 0 }}
              >
                <Sun size={20} />
              </motion.div>
            ) : (
              <motion.div
                key="moon"
                initial={{ opacity: 0, rotate: -90, scale: 0.5 }}
                animate={{ opacity: 1, rotate: 0, scale: 1 }}
                exit={{ opacity: 0, rotate: 90, scale: 0.5 }}
                transition={{ duration: 0.2 }}
                style={{ position: 'absolute', top: 0, left: 0 }}
              >
                <Moon size={20} />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
        <span style={{ transition: 'color 0.3s ease' }}>
          {theme === 'light' ? 'Light Mode' : 'Dark Mode'}
        </span>
      </div>
    </button>
  );
};

export default ThemeToggle;
