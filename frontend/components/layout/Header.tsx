import React from 'react';
import { BarChart3, RotateCcw } from 'lucide-react';
import ThemeToggle from '../ui/ThemeToggle.tsx';
import Container from './Container.tsx';

interface HeaderProps {
  onClearChat: () => void;
}

const Header: React.FC<HeaderProps> = ({ onClearChat }) => {
  return (
    <header className="sticky top-0 z-50 w-full bg-white/80 dark:bg-slate-950/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 transition-colors">
      <Container className="h-16 flex items-center justify-between">
        <div className="flex items-center gap-2 group cursor-default">
          <div className="p-1.5 bg-brand-500 rounded-lg group-hover:scale-110 transition-transform">
            <BarChart3 className="w-5 h-5 text-white" />
          </div>
          <h1 className="text-xl font-bold bg-gradient-to-r from-brand-500 to-purple-600 bg-clip-text text-transparent">
            CricketIQ
          </h1>
        </div>
        
        <div className="flex items-center gap-3">
          <button 
            onClick={onClearChat}
            className="p-2 text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-all"
            title="Clear Chat"
          >
            <RotateCcw className="w-5 h-5" />
          </button>
          <ThemeToggle />
        </div>
      </Container>
    </header>
  );
};

export default Header;