import axios from 'axios';

/**
 * API client for CricketIQ backend
 */
const apiClient = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
    headers: {
        'Content-Type': 'application/json',
    },
});

/**
 * Response type from the backend /chat/ask/ endpoint
 */
export interface ChatResponse {
    answer: string;
    query: string;
    data?: {
        type: 'value' | 'table' | 'bar' | 'line' | 'pie';
        data: unknown;
        columns?: string[];
    };
    error?: string;
}

/**
 * Send a question to the backend and get an AI-powered response
 * @param question - The user's natural language question about cricket stats
 * @returns The AI response with answer, query, and optional chart data
 */
export async function sendQuestion(question: string): Promise<ChatResponse> {
    try {
        const response = await apiClient.post<ChatResponse>('/chat/ask/', {
            question,
        });
        return response.data;
    } catch (error) {
        if (axios.isAxiosError(error)) {
            // Handle network errors or server errors
            const message = error.response?.data?.error || error.message || 'Failed to connect to server';
            throw new Error(message);
        }
        throw error;
    }
}

export default apiClient;
