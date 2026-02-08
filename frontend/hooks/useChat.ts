import { useState, useCallback } from 'react';
import { Message } from '../types.ts';
import { sendQuestion } from '../services/api.ts';

export const useChat = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);

  const ask = useCallback(async (question: string) => {
    const trimmed = question?.trim();
    if (!trimmed || loading) return;

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      text: trimmed,
    };

    setMessages(prev => [...prev, userMessage]);
    setLoading(true);

    try {
      const response = await sendQuestion(trimmed);
      
      const assistantMessage: Message = {
        id: `bot-${Date.now()}`,
        role: 'assistant',
        text: typeof response.answer === 'string' ? response.answer : "I processed your request but couldn't format the text response.",
        chartData: response.chart_data || null,
        query_executed: response.query_executed || "Direct knowledge retrieval.",
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: Message = {
        id: `err-${Date.now()}`,
        role: 'assistant',
        text: "I'm sorry, I encountered an error while fetching the statistics. Please try again in a moment.",
        error: true,
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  }, [loading]);

  const clearChat = useCallback(() => {
    setMessages([]);
  }, []);

  return { messages, loading, ask, clearChat };
};