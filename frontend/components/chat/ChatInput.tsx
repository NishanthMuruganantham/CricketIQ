import React, { useState, useRef, useEffect } from 'react';
import { SendHorizonal } from 'lucide-react';

interface ChatInputProps {
  onSend: (text: string) => void;
  disabled?: boolean;
}

const ChatInput: React.FC<ChatInputProps> = ({ onSend, disabled }) => {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'inherit';
      const scrollHeight = textareaRef.current.scrollHeight;
      textareaRef.current.style.height = `${Math.min(scrollHeight, 200)}px`;
    }
  }, [input]);

  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();
    if (input.trim() && !disabled) {
      onSend(input);
      setInput('');
      // Small delay to reset height after state clear
      setTimeout(() => {
        if (textareaRef.current) textareaRef.current.style.height = 'inherit';
      }, 0);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <form onSubmit={handleSubmit} className="relative group">
      <div className="relative flex items-end w-full bg-slate-100 dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 focus-within:border-brand-500 dark:focus-within:border-brand-500 transition-all shadow-sm ring-brand-500/20 focus-within:ring-2">
        <textarea
          ref={textareaRef}
          rows={1}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about cricket stats..."
          disabled={disabled}
          autoComplete="off"
          autoCorrect="off"
          spellCheck="false"
          className="w-full bg-transparent border-none focus:ring-0 text-slate-800 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-500 resize-none py-4 px-5 pr-14 text-base md:text-base max-h-48 scrollbar-none outline-none"
        />
        <button
          type="submit"
          disabled={!input.trim() || disabled}
          className={`absolute right-2 bottom-2 p-2 rounded-xl transition-all ${
            input.trim() && !disabled 
              ? 'bg-brand-500 text-white hover:bg-brand-600 active:scale-95 shadow-md' 
              : 'bg-slate-200 dark:bg-slate-700 text-slate-400 dark:text-slate-500 scale-90'
          }`}
          aria-label="Send message"
        >
          <SendHorizonal className="w-5 h-5" />
        </button>
      </div>
    </form>
  );
};

export default ChatInput;