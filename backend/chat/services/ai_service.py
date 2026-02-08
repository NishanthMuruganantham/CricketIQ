import google.generativeai as genai
from decouple import config
from django.conf import settings
import json
from .schema_service import get_schema
import re

# Configure Gemini
genai.configure(api_key=config("GEMINI_API_KEY"))

SYSTEM_PROMPT = """
You are a cricket statistics assistant. You have access to two Men's T20I datasets loaded as pandas DataFrames.

Available DataFrames:
- `match_df` — Match-level summary data (one row per match)
- `ball_df` — Ball-by-ball delivery data (one row per delivery)
- They are linked via `match_id`. Use pd.merge() when you need data from both.

{schema}

When the user asks a question:
1. Decide which DataFrame to use (or both via merge).
2. Write a pandas expression to extract the answer.
3. Return ONLY a valid JSON object — no extra text, no markdown, no ```json fences:

{{
    "pandas_code": "<valid pandas expression using match_df, ball_df, and pd>",
    "answer_template": "<how to phrase the answer, use {{result}} as placeholder>",
    "chart_suggestion": {{
        "type": "bar | line | pie | null",
        "title": "...",
        "x_axis": "...",
        "y_axis": "..."
    }}
}}

Rules:
- Only `match_df`, `ball_df`, and `pd` are in scope. Do not use `df`.
- Only read data. Never modify any DataFrame.
- If the question is not about cricket or this dataset, return: {{"error": "Question not related to cricket data."}}
- Always suggest a chart type when the result is a list or ranking. Use null only for single-value answers.
- pandas_code must be a single expression that returns a value — not multiple statements.
- For player run totals, use: ball_df.groupby('batter')['batsman_runs'].sum()
- For wickets, filter: ball_df[ball_df['player_dismissed'].notna()].groupby('bowler').size()
- For dot balls, filter: ball_df[ball_df['batsman_runs'] == 0] (exclude extras-only deliveries if needed)
- For match wins by team, check both team_1 and team_2 against winner in match_df.
- Extract year from date: match_df['date'].str[:4] (it is a string column in YYYY-MM-DD format)
- over_number in ball_df is 0-indexed. Over 1 in cricket = over_number 0 in data.
"""

def get_generated_query(question: str, conversation_history: list = None) -> dict:
    """
    Generates a pandas query from the user's question using Gemini.
    
    Args:
        question (str): The user's natural language question.
        conversation_history (list): Optional list of previous conversation turns.
        
    Returns:
        dict: Parsed JSON response from the LLM containing 'pandas_code', etc.
    """
    try:
        # 1. Get Schema
        schema = get_schema()
        
        # 2. Construct Prompt
        # Format schema as a compact string representation
        schema_str = json.dumps(schema, indent=2)
        system_prompt = SYSTEM_PROMPT.format(schema=schema_str)
        
        # 3. Format conversation history for context
        history_context = ""
        if conversation_history:
            history_lines = []
            for msg in conversation_history[-6:]:  # Limit to last 6 messages for context
                role = "User" if msg.get("role") == "user" else "Assistant"
                history_lines.append(f"{role}: {msg.get('text', '')}")
            if history_lines:
                history_context = "\n\nRecent conversation history:\n" + "\n".join(history_lines) + "\n"
        
        # 4. Call Gemini
        model = genai.GenerativeModel("gemini-3-flash-preview")
        chat = model.start_chat()
        
        # Combine system prompt, history, and user question
        full_prompt = f"{system_prompt}{history_context}\n\nUser Question: {question}"
        
        response = chat.send_message(full_prompt)
        response_text = response.text
        
        # 4. Clean and Parse Response
        # Strip markdown fences if present
        cleaned_text = re.sub(r'^```json\s*', '', response_text)
        cleaned_text = re.sub(r'^```\s*', '', cleaned_text)
        cleaned_text = re.sub(r'\s*```$', '', cleaned_text)
        cleaned_text = cleaned_text.strip()
        
        return json.loads(cleaned_text)
        
    except Exception as e:
        # Fallback error handling
        return {
            "error": f"AI Service Error: {str(e)}"
        }
