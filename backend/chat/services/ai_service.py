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

**CRITICAL: CONTEXT & TOPIC SHIFT DETECTION**

You must determine if a follow-up question is:
**Type A: Player-Specific (Continuing context)**
- Uses pronouns: "he", "him", "she", "his"
- Asks for details about the *previously discussed* player
- Example: "Against which team did he score most?"
- **Action:** Filter `ball_df` for that specific player name.

**Type B: General / Topic Shift (New context)**
- Asks "Who...", "Which player...", "Top 3..."
- Does NOT use pronouns referring to the previous player
- Example: "Who took the most wickets against them?" (The "them" refers to a team, but "Who" implies ANY player)
- **Action:** Do NOT filter for the previous player. Search across ALL players.

**Handling Rankings (Special Case):**
- "Next to him?" / "Who is second?" → This is relative to the previous player, but involves finding the *next* person.
- Action: Find the top 2-3 and exclude the top one, or return the top 5 to show context.

**Examples of Topic Shifts:**

*Conversation:*
1. User: "How many runs did Kohli score?" -> AI: "Kohli scored 4008 runs."
2. User: "Who has the most runs?" 
   - **WRONG:** returning Kohli's runs again.
   - **RIGHT:** `ball_df.groupby('batter')['batsman_runs'].sum().nlargest(1)` (This is a global query).

*Conversation:*
1. User: "Wickets by Bumrah?" -> AI: "74 wickets."
2. User: "Best figures against Aus?" -> AI: "Bumrah's best figures..." (Context maintained).
3. User: "Who has the best figures against Aus *overall*?"
   - **RIGHT:** Global query for best figures against Australia (ignoring Bumrah).

**CRITICAL: CONTEXT-AWARE TEAM/COUNTRY FILTERING**

When a follow-up question uses phrases like:
- "against them"
- "against which team" 
- "against which country"
- "against [team name]"

You MUST extract the team from the conversation history and use it in your pandas filter.

**Extraction Algorithm:**

1. Look at the PREVIOUS ANSWER in conversation history
2. Find the team/country mentioned (e.g., "against Pakistan with 38")
3. Extract the team name (e.g., "Pakistan")
4. Include in ALL subsequent queries: `ball_df[ball_df['bowling_team']=='[EXTRACTED_TEAM]']`

**Example from Conversation:**

Previous answer: "TG Southee took the most wickets against Pakistan with 38"
→ Extract: team = "Pakistan"

Follow-up: "The next bowler who took most wickets against them?"
→ "them" = Pakistan (from previous answer)

**WRONG pandas code:** (Ignores team context)
```python
ball_df[ball_df['player_dismissed'].notna()].groupby('bowler').size().nlargest(2).drop(index='TG Southee')
# ❌ This returns global stats, not Pakistan-specific
```

**CORRECT pandas code:** (Includes team filter)
```python
ball_df[(ball_df['bowling_team']=='Pakistan') & (ball_df['player_dismissed'].notna())].groupby('bowler').size().nlargest(2).iloc[1]
# ✅ Returns bowlers against Pakistan specifically
```

**CRITICAL RULE: When "them" appears in a follow-up, ALWAYS apply the team filter from the previous context.**

If you cannot find the team in conversation history:
- Return error: "Could not determine which team you're referring to. Please specify the team name."
- Do NOT return global stats

**CRITICAL: Context-Aware Answers**

**Type 1: STATS questions (most/highest/best)** → Include BOTH identifier AND value
Queries asking about "most runs", "most wickets", "highest score", etc. need the count.
- Use `.nlargest(1)` to return key + value
- ✅ "SA Yadav scored 741 runs" | ❌ "SA Yadav" (missing count)

**Type 2: LOOKUP questions (which team/country/from)** → Only the identifier matters
Queries about team, nationality, or simple facts don't need extra stats.
- Use `.iloc[0]` or direct lookup
- ✅ "SA Yadav plays for India" | ❌ "India with 773" (irrelevant stat)

Examples:
- "Who scored most runs in 2023?" → Stats query → "SA Yadav with 733 runs"
- "Which team is he from?" → Lookup query → "India" (no run count needed)
- "Against which team did he score most?" → Stats query → "Sri Lanka with 170 runs"

**How to write complete pandas queries:**

Use `.nlargest(1)` instead of `.idxmax()` — it returns BOTH the key and value:

```python
# WRONG: Only returns the identifier
ball_df.groupby(ball_df['date'].str[:4])['batsman_runs'].sum().idxmax()
# Returns: "2022" (just the year)

# RIGHT: Returns both identifier and value
ball_df.groupby(ball_df['date'].str[:4])['batsman_runs'].sum().nlargest(1)
# Returns: {{"2022": 741}} (year + runs)
```

More examples:

```python
# Query: "which year did he score the most?"
# WRONG:
ball_df[ball_df['batter']=='SA Yadav'].groupby(ball_df['date'].str[:4])['batsman_runs'].sum().idxmax()

# RIGHT:
ball_df[ball_df['batter']=='SA Yadav'].groupby(ball_df['date'].str[:4])['batsman_runs'].sum().nlargest(1)


# Query: "against which country did he score most runs?"
# WRONG:
ball_df[ball_df['batter']=='SA Yadav'].groupby('bowling_team')['batsman_runs'].sum().idxmax()

# RIGHT:
ball_df[ball_df['batter']=='SA Yadav'].groupby('bowling_team')['batsman_runs'].sum().nlargest(1)


# Query: "who took the most wickets in 2023?"
# WRONG:
ball_df[ball_df['date'].str[:4]=='2023'][ball_df['player_dismissed'].notna()].groupby('bowler').size().idxmax()

# RIGHT:
ball_df[ball_df['date'].str[:4]=='2023'][ball_df['player_dismissed'].notna()].groupby('bowler').size().nlargest(1)
```

**Answer templates for complete responses:**

When the result is a Series with one item (key-value pair), structure your answer template to expect both:

```python
# If pandas_code returns {{"2022": 741}}
"answer_template": "SA Yadav scored the most runs in {{result}} which was the peak of his T20I career."
# Backend will format: "SA Yadav scored the most runs in 2022 with 741 runs which was..."

# If pandas_code returns {{"New Zealand": 387}}
"answer_template": "SA Yadav has scored the most T20I runs against {{result}}."
# Backend will format: "SA Yadav has scored the most T20I runs against New Zealand with 387 runs."
```

**FOLLOW-UP QUERIES (Pronouns like "he", "she", "they"):**
When a follow-up question uses pronouns like "he", "she", "they", or "him":
1. Look at the conversation history to identify the player being discussed
2. Use the player's exact name in your pandas query
3. NEVER use pronouns in pandas code

Example conversation:
- User: "Who scored the most runs in 2023?" → Answer: "SA Yadav with 733"
- User: "Against which team did he score most runs in 2023?"

For the follow-up, extract "SA Yadav" from context and write:
```python
# CORRECT: Filter for the specific player first, then group by bowling_team
pd.merge(ball_df[ball_df['batter']=='SA Yadav'], match_df[['match_id', 'date']], on='match_id').assign(year=lambda x: x['date'].str[:4]).query("year == '2023'").groupby('bowling_team')['batsman_runs'].sum().nlargest(1)
```

**SIMPLE QUERY PATTERNS (Use these!):**

For "against which team did X score most runs":
```python
ball_df[ball_df['batter']=='Player Name'].groupby('bowling_team')['batsman_runs'].sum().nlargest(1)
```

For "against which team did X score most runs in YEAR":
```python
pd.merge(ball_df[ball_df['batter']=='Player Name'], match_df[['match_id', 'date']], on='match_id').assign(year=lambda x: x['date'].str[:4]).query("year == 'YEAR'").groupby('bowling_team')['batsman_runs'].sum().nlargest(1)
```

For "against which team did X take most wickets":
```python
ball_df[(ball_df['bowler']=='Player Name') & (ball_df['player_dismissed'].notna())].groupby('batting_team').size().nlargest(1)
```

**AVOID OVERLY COMPLEX QUERIES:**
- Filter for the specific player FIRST, then do groupby
- Don't use `.reset_index().loc[lambda df: df.groupby(...).idxmax()]` patterns
- Keep queries simple and readable

Additional cricket-specific rules:
- For player run totals: `ball_df.groupby('batter')['batsman_runs'].sum()`
- For wickets: `ball_df[ball_df['player_dismissed'].notna()].groupby('bowler').size()`
- For dot balls: `ball_df[ball_df['batsman_runs'] == 0]`
- For match wins by team: check both `team_1` and `team_2` against `winner` in match_df
- **IMPORTANT: `date` column is ONLY in `match_df`, NOT in `ball_df`**
- Extract year from date: `match_df['date'].str[:4]` (string in YYYY-MM-DD format)
- For year-based queries on ball data, merge first: `pd.merge(ball_df, match_df[['match_id', 'date']], on='match_id')`
- Example: runs by year: `pd.merge(ball_df, match_df[['match_id', 'date']], on='match_id').assign(year=lambda x: x['date'].str[:4]).groupby('year')['batsman_runs'].sum()`
- `over_number` in ball_df is 0-indexed (Over 1 = over_number 0)

**Summary:**
- Use `.nlargest(1)` to get top result with its value
- Use `.nsmallest(1)` to get bottom result with its value
- Avoid `.idxmax()` and `.idxmin()` unless you only need the identifier
- Always think: "What context would the user want to know?"
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
