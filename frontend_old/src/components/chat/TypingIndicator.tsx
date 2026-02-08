import { Sparkles } from 'lucide-react';

export default function TypingIndicator() {
    return (
        <div className="flex gap-4 items-start">
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-[rgb(var(--accent))] flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-white" />
            </div>

            <div className="bg-[rgb(var(--assistant-msg))] rounded-2xl px-4 py-3 flex gap-1">
                <span
                    className="w-2 h-2 bg-[rgb(var(--text-secondary))] rounded-full animate-bounce"
                    style={{ animationDelay: '0ms' }}
                />
                <span
                    className="w-2 h-2 bg-[rgb(var(--text-secondary))] rounded-full animate-bounce"
                    style={{ animationDelay: '150ms' }}
                />
                <span
                    className="w-2 h-2 bg-[rgb(var(--text-secondary))] rounded-full animate-bounce"
                    style={{ animationDelay: '300ms' }}
                />
            </div>
        </div>
    );
}
