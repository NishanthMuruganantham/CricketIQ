// API Base URL - Update this to your Django backend endpoint
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/chat';

interface ConversationMessage {
  role: 'user' | 'assistant';
  text: string;
}

export async function sendQuestion(question: string, conversationHistory?: ConversationMessage[]) {
  try {
    const response = await fetch(`${API_BASE_URL}/ask/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        question,
        conversation_history: conversationHistory || []
      }),
    });

    if (!response.ok) {
      throw new Error(`API request failed with status ${response.status}`);
    }

    const data = await response.json();

    /**
     * Expected backend response format:
     * {
     *   "answer": "Virat Kohli has scored...",
     *   "chart_data": {
     *      "type": "bar",
     *      "labels": ["2021", "2022", "2023"],
     *      "values": [500, 650, 800],
     *      "title": "Yearly Runs",
     *      "x_axis": "Year",
     *      "y_axis": "Runs"
     *   },
     *   "query_executed": "SELECT sum(runs) FROM matches WHERE player_id=..."
     * }
     */
    return data;
  } catch (error) {
    console.error('API Service Error:', error);
    throw error;
  }
}