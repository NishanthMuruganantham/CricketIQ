import google.generativeai as genai
from decouple import config
from django.conf import settings
import json
from .schema_service import get_schema
import re
from .query_engine import engine

# Configure Gemini
genai.configure(api_key=config("GEMINI_API_KEY"))

def detect_topic_shift(question: str) -> bool:
    """
    Detects if a follow-up question has shifted topic from a specific player 
    to a general context.
    
    Returns True if:
    1. Question contains general 'who'/'which' keywords
    2. AND Question does NOT contain specific pronouns (he/him/she/her)
    3. AND Question is NOT a ranking query relative to the player ("next to him")
    """
    q_lower = question.lower()
    
    # Keywords indicating a general question
    general_indicators = [
        "who ", "who's", "whose",
        "which player", "which bowler", "which batter", "which batsman",
        "top scorer", "highest wicket", "most runs", "most wickets"
    ]
    
    # Pronouns indicating we are still talking about the specific player
    player_pronouns = [" he ", " him ", " his ", " she ", " her ", " hers ", " they ", " their "]
    
    # Ranking queries that ARE relative to the player (not a topic shift)
    ranking_indicators = ["next to", "after ", "second", "2nd", "3rd", "third"]
    
    is_general = any(ind in q_lower for ind in general_indicators)
    has_pronoun = any(pronoun in q_lower for pronoun in player_pronouns)
    is_ranking = any(rank in q_lower for rank in ranking_indicators)
    
    # It is a topic shift if:
    # - It looks like a general question ("who took most...")
    # - AND it avoids pronouns ("he", "him")
    # - AND it's not asking for a relative ranking ("next to him")
    if is_general and not has_pronoun and not is_ranking:
        return True
        
    return False

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
- Use chart_type: null for single-value answers or top-1 results. Only suggest charts for rankings/lists with 3+ items.
- pandas_code must be a single expression that returns a value — not multiple statements.

**CRITICAL: Column Names**

In `ball_df`:
- Batter column: `batter`
- Bowler column: `bowler`
- Bowling team (the team that is bowling): `bowling_team`
- Batting team (the team that is batting): `batting_team`
- Runs by batter: `batsman_runs`
- Dismissed player: `player_dismissed`
- Match ID: `match_id`
- Date: NOT in ball_df (only in match_df)

In `match_df`:
- Match ID: `match_id`
- Team 1: `team_1`
- Team 2: `team_2`
- Winner: `winner`
- Date: `date` (YYYY-MM-DD format)
- Other metadata: See schema below

**IMPORTANT: For bowler statistics, use `bowling_team` from ball_df (NOT team_1 or team_2 from match_df)**

**IMPORTANT: `date` column is ONLY in `match_df`, NOT in `ball_df`**
- To filter ball_df by year: First merge with match_df, extract year, then filter
- Example: `pd.merge(ball_df, match_df[['match_id', 'date']], on='match_id').assign(year=lambda x: x['date'].str[:4])`

**Type 1: STATS questions (most/highest/best)** → Include BOTH identifier AND value
- Use `.nlargest(1)` to return key + value
- ✅ "SA Yadav scored 741 runs" | ❌ "SA Yadav" (missing count)

**Type 2: LOOKUP questions (which team/country/from)** → Only the identifier matters
- Use `.iloc[0]` or direct lookup
- ✅ "SA Yadav plays for India" | ❌ "India with 773" (irrelevant stat)

**Simple Query Patterns (Use these!):**

For "which team did X take most wickets against":
```python
# Count wickets per bowling team
ball_df[(ball_df['bowler']=='Player Name') & (ball_df['player_dismissed'].notna())].groupby('bowling_team').size().nlargest(1)
```

For "top N bowlers against team X":
```python
ball_df[(ball_df['bowling_team']=='Team Name') & (ball_df['player_dismissed'].notna())].groupby('bowler').size().nlargest(N)
```

For "batting team's runs against bowling team":
```python
ball_df[(ball_df['bowling_team']=='Bowling Team Name')].groupby('batting_team')['batsman_runs'].sum().nlargest(1)
```

**FOLLOW-UP QUERIES (Pronouns like "he", "she", "they"):**
When a follow-up question uses pronouns:
1. Look at conversation history to identify the player
2. Use player's exact name in the pandas query
3. NEVER use pronouns in pandas code

Example:
- User: "Who scored the most runs in 2023?" → Answer: "SA Yadav with 733"
- User: "Which team he scored most against?" → Extract "SA Yadav" from context

**Answer templates:**

For `.nlargest(1)` results (dict with one key-value):
```python
"answer_template": "Player Name took the most wickets against {{result}} which was historic."
```

For single values:
```python
"answer_template": "The answer is {{result}}."
```

**Summary:**
- Use `.nlargest(1)` for ranking queries (returns key + value)
- Use `.nsmallest(1)` for minimum queries
- Avoid `.idxmax()` and `.idxmin()` — they only return the key
- Always think: "What context would the user want?"

**FOLLOW-UP CONVERSATION HANDLING - CRITICAL CONTEXT EXTRACTION:**

When the user asks a follow-up question (Q2, Q3, Q4...):

1. **Check for pronouns (he, she, they, him, her, his, their):**
   - These refer to a PLAYER mentioned in conversation history
   - IMPORTANT: Look at the MOST RECENT answer (the last assistant message)
   - Extract the player name from that most recent answer
   - IGNORE earlier mentions of other players
   
   Example:
   - Q1: "Who scored most?" → A: "SA Yadav with 733"
   - Q2: "Who's next?" → A: "S Sesazi with 630"
   - Q3: "He is from which team?"
     → "he" should refer to S Sesazi (from Q2's answer, the MOST RECENT)
     → NOT SA Yadav (from Q1's answer)
     → Use: ball_df[ball_df['batter']=='S Sesazi'].groupby('batting_team').size().nlargest(1)

2. **How to Extract Player Name:**
   - Look at the LAST message in conversation_history where role=="assistant"
   - Find the player name (usually appears as: "Player Name with X runs/wickets")
   - That is your player name for pronoun resolution

3. **If it starts with "Who"/"Which" and has NO pronouns:**
   - This is asking about a DIFFERENT player/bowler
   - Generate query about ALL players
   - Do NOT assume previous player

4. **Check for "next", "second", "runner-up":**
   - User wants the 2nd ranked player
   - Use .nlargest(2).iloc[1] to get the 2nd result
   - Then use that player in subsequent queries

5. **If it mentions a team ("against them", "against Pakistan"):**
   - Extract the team from the previous answer
   - Use the same team in this query

Example Conversation (CORRECT):
- Q1: "Who scored most runs in 2023?" → A: "SA Yadav with 733" → Recent player: "SA Yadav"
- Q2: "Who's next best?" → A: "S Sesazi with 630" → Recent player updated to: "S Sesazi"
- Q3: "He is from which team?" → "he" = S Sesazi (most recent!) → Query about S Sesazi ✅
- Q4: "No not him, next best" → asking for 2nd ranked → S Sesazi with 630 ✅
"""

def extract_recent_player(conversation_history: list) -> str:
    """
    Extract the most recently mentioned player from conversation history.
    Looks at the last assistant message and finds a player name pattern.
    """
    if not conversation_history:
        return None
    
    # Find the last assistant message
    for msg in reversed(conversation_history):
        if msg.get("role") == "assistant":
            text = msg.get("text", "")
            # Look for pattern: "Name with X runs/wickets"
            # \w* instead of \w+ to handle single-letter initials like "S Sesazi"
            match = re.search(r'([A-Z]\w*(?:\s+[A-Z]\w*)+)\s+(?:with|scored|took|plays|has)', text)
            if match:
                return match.group(1)
    
    return None

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

        # 2b. Inject recent player context for pronoun resolution
        if conversation_history:
            recent_player = extract_recent_player(conversation_history)
            pronoun_words = ['he', 'she', 'him', 'her', 'his', 'they', 'their', 'hers']
            if recent_player and any(pronoun in question.lower().split() for pronoun in pronoun_words):
                history_context += f"\n🎯 **RECENT CONTEXT: The most recently discussed player is {recent_player}. Pronouns (he/she/him/her/they) refer to this player.**\n"

        # 5. Injection: Topic Shift Detection
        # If the user is asking a general question after a conversation, force the AI to notice it.
        if conversation_history and detect_topic_shift(question):
             history_context += "\n⚠️ **IMPORTANT: User has shifted from player-specific to GENERAL context.** Answer about ALL players/teams, not the previous player.\n"
        
        # 4. Call Gemini with Fallback Strategy
        models_to_try = [
            "gemma-3-27b-it",         # User requested Primary
            "gemini-2.5-flash-lite",  # Fast & cheap
            "gemini-2.5-flash", 
            "gemini-1.5-flash",
            "gemini-1.5-pro",
            "gemini-1.5-pro-latest",
        ]
        
        final_result = None
        last_error = None
        
        for model_name in models_to_try:
            try:
                print(f"Trying model: {model_name}...", flush=True)
                model = genai.GenerativeModel(model_name)
                chat = model.start_chat()
                
                # Combine system prompt, history, and user question
                full_prompt = f"{system_prompt}{history_context}\n\nUser Question: {question}"
                
                response = chat.send_message(full_prompt)
                
                if response and response.text:
                    response_text = response.text
                    # Try to parse immediately to validate quality
                    try:
                        # 1. Try standard clean
                        cleaned_text = re.sub(r'^```json\s*', '', response_text)
                        cleaned_text = re.sub(r'^```\s*', '', cleaned_text)
                        cleaned_text = re.sub(r'\s*```$', '', cleaned_text)
                        cleaned_text = cleaned_text.strip()
                        final_result = json.loads(cleaned_text)
                        
                        # VALIDATE CODE EXECUTION
                        code = final_result.get("pandas_code")
                        if code:
                            exec_result = engine.execute(code)
                            if "error" in exec_result:
                                raise Exception(f"Generated code failed validation: {exec_result['error']}")

                        print(f"Success with {model_name}", flush=True)
                        break
                    except json.JSONDecodeError:
                        # 2. Robust fallback: regex search for outer JSON object
                        print(f"Standard JSON parse failed for {model_name}, trying regex extraction...", flush=True)
                        match = re.search(r'\{.*\}', response_text, re.DOTALL)
                        if match:
                            final_result = json.loads(match.group(0))
                            
                            # VALIDATE CODE EXECUTION (Regex Path)
                            code = final_result.get("pandas_code")
                            if code:
                                exec_result = engine.execute(code)
                                if "error" in exec_result:
                                    raise Exception(f"Generated code failed validation: {exec_result['error']}")

                            print(f"Success with {model_name} (via regex)", flush=True)
                            break
                        else:
                            raise Exception(f"Invalid JSON response: {response_text[:100]}...")
                            
            except Exception as e:
                print(f"Error with {model_name}: {e}", flush=True)
                last_error = e
                continue
                
        if not final_result:
            raise Exception(f"All models failed. Last error: {last_error}")
            
        return final_result
        
    except Exception as e:
        # Fallback error handling
        return {
            "error": f"AI Service Error: {str(e)}"
        }
