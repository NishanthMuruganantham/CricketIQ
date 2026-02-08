import React from 'react';
import { Sun, Moon } from 'lucide-react';
import { useTheme } from '../../hooks/useTheme.ts';

const ThemeToggle: React.FC = () => {
  const { theme, toggleTheme, isDark } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className="relative flex items-center justify-between w-14 h-7 p-1 rounded-full bg-slate-200 dark:bg-slate-800 transition-colors"
      aria-label="Toggle theme"
    >
      <div className={`absolute w-5 h-5 bg-white dark:bg-slate-300 rounded-full shadow-sm transform transition-transform duration-300 flex items-center justify-center ${
        isDark ? 'translate-x-7' : 'translate-x-0'
      }`}>
        {isDark ? (
          <Moon className="w-3 h-3 text-slate-800" />
        ) : (
          <Sun className="w-3 h-3 text-brand-500" />
        )}
      </div>
      <Sun className={`ml-1 w-3.5 h-3.5 text-brand-500 transition-opacity ${isDark ? 'opacity-0' : 'opacity-100'}`} />
      <Moon className={`mr-1 w-3.5 h-3.5 text-slate-400 transition-opacity ${isDark ? 'opacity-100' : 'opacity-0'}`} />
    </button>
  );
};

export default ThemeToggle;