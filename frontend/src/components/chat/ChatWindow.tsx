import { useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ChatMessage from './ChatMessage';
import WelcomeScreen from './WelcomeScreen';
import TypingIndicator from './TypingIndicator';
import type { Message } from '../../hooks/useChat';

interface ChatWindowProps {
    messages: Message[];
    loading: boolean;
    onSuggestionClick?: (question: string) => void;
}

export default function ChatWindow({ messages, loading, onSuggestionClick }: ChatWindowProps) {
    const bottomRef = useRef<HTMLDivElement>(null);

    // Auto-scroll to bottom when new messages arrive
    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, loading]);

    return (
        <div className="h-full overflow-y-auto px-4 py-6">
            <div className="max-w-4xl mx-auto space-y-6">
                {messages.length === 0 ? (
                    <WelcomeScreen onSuggestionClick={onSuggestionClick} />
                ) : (
                    <AnimatePresence>
                        {messages.map((msg, index) => (
                            <motion.div
                                key={index}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ duration: 0.2 }}
                            >
                                <ChatMessage message={msg} />
                            </motion.div>
                        ))}
                    </AnimatePresence>
                )}

                {loading && <TypingIndicator />}
                <div ref={bottomRef} />
            </div>
        </div>
    );
}
