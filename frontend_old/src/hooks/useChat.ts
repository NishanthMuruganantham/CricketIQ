import { useState, useCallback } from 'react';
import { sendQuestion, type ChatResponse } from '../services/api';

/**
 * Message type for chat history
 */
export interface Message {
    role: 'user' | 'assistant';
    text: string;
    chartData?: ChatResponse['data'];
    query?: string;
    isError?: boolean;
}

/**
 * Return type for useChat hook
 */
interface UseChatReturn {
    messages: Message[];
    loading: boolean;
    ask: (question: string) => Promise<void>;
    clearMessages: () => void;
}

/**
 * Custom hook for managing chat state and API communication
 * Implements optimistic updates for smooth UX
 */
export function useChat(): UseChatReturn {
    const [messages, setMessages] = useState<Message[]>([]);
    const [loading, setLoading] = useState(false);

    /**
     * Send a question to the backend
     * - Optimistically adds user message immediately
     * - Adds assistant response (or error) when API returns
     */
    const ask = useCallback(async (question: string) => {
        if (!question.trim() || loading) return;

        // Optimistic update: add user message immediately
        const userMessage: Message = {
            role: 'user',
            text: question,
        };
        setMessages((prev) => [...prev, userMessage]);
        setLoading(true);

        try {
            const response = await sendQuestion(question);

            const assistantMessage: Message = {
                role: 'assistant',
                text: response.answer,
                chartData: response.data,
                query: response.query,
            };
            setMessages((prev) => [...prev, assistantMessage]);
        } catch (error) {
            const errorMessage: Message = {
                role: 'assistant',
                text: error instanceof Error ? error.message : 'An unexpected error occurred',
                isError: true,
            };
            setMessages((prev) => [...prev, errorMessage]);
        } finally {
            setLoading(false);
        }
    }, [loading]);

    /**
     * Clear all messages and start fresh
     */
    const clearMessages = useCallback(() => {
        setMessages([]);
    }, []);

    return { messages, loading, ask, clearMessages };
}
