import { User, Sparkles, AlertCircle } from 'lucide-react';
import type { Message } from '../../hooks/useChat';
import ReactMarkdown from 'react-markdown';
import ChartRenderer from '../charts/ChartRenderer';

interface ChatMessageProps {
    message: Message;
}

export default function ChatMessage({ message }: ChatMessageProps) {
    const isUser = message.role === 'user';

    return (
        <div className={`flex gap-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
            {!isUser && (
                <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${message.isError
                    ? 'bg-red-500'
                    : 'bg-[rgb(var(--accent))]'
                    }`}>
                    {message.isError ? (
                        <AlertCircle className="w-5 h-5 text-white" />
                    ) : (
                        <Sparkles className="w-5 h-5 text-white" />
                    )}
                </div>
            )}

            <div
                className={`max-w-[80%] md:max-w-[70%] rounded-2xl px-4 py-3 ${isUser
                    ? 'bg-[rgb(var(--user-msg))] text-white'
                    : message.isError
                        ? 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-200 border border-red-200 dark:border-red-800'
                        : 'bg-[rgb(var(--assistant-msg))] text-[rgb(var(--text-primary))]'
                    }`}
            >
                <div className="text-sm md:text-base leading-relaxed prose prose-sm dark:prose-invert max-w-none">
                    <ReactMarkdown>{message.text}</ReactMarkdown>
                </div>

                {/* Query display (for debugging/transparency) */}
                {message.query && (
                    <div className="mt-3 pt-3 border-t border-[rgb(var(--border))]">
                        <p className="text-xs text-[rgb(var(--text-secondary))] font-mono">
                            Query: {message.query}
                        </p>
                    </div>
                )}

                {/* Chart visualization */}
                {message.chartData && message.chartData.type && (
                    <div className="mt-4">
                        <ChartRenderer chartData={message.chartData} />
                    </div>
                )}
            </div>

            {isUser && (
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-[rgb(var(--bg-tertiary))] flex items-center justify-center">
                    <User className="w-5 h-5" />
                </div>
            )}
        </div>
    );
}
