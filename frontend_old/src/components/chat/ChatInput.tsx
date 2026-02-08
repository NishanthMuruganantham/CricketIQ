import { useState } from 'react';
import { Send } from 'lucide-react';

interface ChatInputProps {
    onSend: (message: string) => void;
    disabled?: boolean;
}

export default function ChatInput({ onSend, disabled }: ChatInputProps) {
    const [input, setInput] = useState('');

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || disabled) return;

        onSend(input.trim());
        setInput('');
    };

    return (
        <form onSubmit={handleSubmit} className="p-4">
            <div className="flex gap-3 items-end">
                <textarea
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => {
                        if (e.key === 'Enter' && !e.shiftKey) {
                            e.preventDefault();
                            handleSubmit(e);
                        }
                    }}
                    placeholder="Ask about cricket stats..."
                    disabled={disabled}
                    rows={1}
                    className="flex-1 resize-none rounded-2xl bg-[rgb(var(--bg-tertiary))] px-4 py-3 
                     text-[rgb(var(--text-primary))] placeholder-[rgb(var(--text-secondary))]
                     border border-[rgb(var(--border))] focus:outline-none focus:ring-2 
                     focus:ring-[rgb(var(--accent))] disabled:opacity-50 transition-all"
                    aria-label="Chat input"
                />

                <button
                    type="submit"
                    disabled={!input.trim() || disabled}
                    className="flex-shrink-0 w-10 h-10 rounded-full bg-[rgb(var(--accent))] text-white
                     flex items-center justify-center hover:opacity-90 disabled:opacity-50
                     transition-opacity"
                    aria-label="Send message"
                >
                    <Send className="w-5 h-5" />
                </button>
            </div>
        </form>
    );
}
