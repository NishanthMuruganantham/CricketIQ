
import React from 'react';
import { Bot } from 'lucide-react';

const TypingIndicator: React.FC = () => {
  return (
    <div className="flex w-full justify-start animate-fade-in">
      <div className="flex gap-3 max-w-[80%]">
        <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-brand-500 flex items-center justify-center">
          <Bot className="w-5 h-5 text-white" />
        </div>
        <div className="bg-slate-100 dark:bg-slate-800 px-4 py-3 rounded-2xl rounded-tl-none border border-slate-200 dark:border-slate-700 flex items-center gap-1">
          <div className="w-1.5 h-1.5 bg-slate-400 dark:bg-slate-500 rounded-full typing-dot" />
          <div className="w-1.5 h-1.5 bg-slate-400 dark:bg-slate-500 rounded-full typing-dot" />
          <div className="w-1.5 h-1.5 bg-slate-400 dark:bg-slate-500 rounded-full typing-dot" />
        </div>
      </div>
    </div>
  );
};

export default TypingIndicator;
