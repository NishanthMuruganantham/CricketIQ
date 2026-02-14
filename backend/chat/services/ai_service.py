import google.generativeai as genai
from decouple import config
import json
import re
from .schema_service import get_schema
from .query_engine import engine

# Configure Gemini
genai.configure(api_key=config("GEMINI_API_KEY"))

# Single, proven model
PRIMARY_MODEL = "gemma-3-27b-it"

SYSTEM_PROMPT = """
You are a cricket statistics assistant for Men's T20I data.

Available DataFrames:
- `match_df`: Match-level data (one row per match)
- `ball_df`: Ball-by-ball data (one row per delivery)
- Linked via `match_id`

{schema}

Return ONLY valid JSON (no markdown, no fences):
{{
    "pandas_code": "<expression using match_df, ball_df, pd>",
    "answer_template": "<response text with {{result}} placeholder>",
    "chart_suggestion": {{"type": "bar|line|pie|null", "title": "...", "x_axis": "...", "y_axis": "..."}}
}}

**CRITICAL RULES:**

1. **ball_df (deliverywise_data.csv) columns:**
   - `match_id`, `innings_number`, `over_number`, `ball_number`
   - `batter`, `bowler`, `non_striker`
   - `batting_team`, `bowling_team`
   - `batsman_runs` (runs off bat), `extra_runs` (all extras), `total_runs` (bat + extras)
   - `wide_runs`, `no_ball_runs`, `bye_runs`, `leg_bye_runs`, `penalty_runs`
   - `player_dismissed`, `dismissal_type`, `fielder_name`
   - NO `date` (only in match_df)

2. **match_df (matchwise_data.csv) columns:**
   - `match_id`, `date` (YYYY-MM-DD), `event_name`
   - `team_1`, `team_2` (the two teams)
   - `toss_winner`, `toss_decision` (bat/field)
   - `team_1_total_runs`, `team_2_total_runs`
   - `winner`, `margin_runs`, `margin_wickets`, `winning_method`
   - `ground_name`, `ground_city`
   - `player_of_the_match`

3. **Key facts:**
   - Batter stats: Use `batsman_runs` (runs off bat), NOT `total_runs` for actual batting performance
   - Wickets: Filter on `player_dismissed` (not null) + count by `bowler`
   - Bowling team: Use `bowling_team` from ball_df (NOT team_1/team_2 which are match-level)
   - Batting team: Use `batting_team` from ball_df
   - Year filtering: Must merge with match_df first (date only there)
   - Over/ball tracking: `over_number` is 0-indexed (Over 1 = over_number 0)

4. **For year filtering:** Merge and extract year
   ```python
   pd.merge(ball_df, match_df[['match_id', 'date']], on='match_id').assign(year=lambda x: x['date'].str[:4])
   ```

5. **Stats queries:** Use `.nlargest(1)` to return both key + value
   - ✅ "SA Yadav with 733 runs"
   - ❌ "SA Yadav" (incomplete)

6. **Lookup queries:** Only identifier needed
   - ✅ "India"
   - ❌ "India with 773" (irrelevant stat)

7. **Follow-ups with pronouns ("he", "she", "they") or referring to a previous player:**
   - Resolve to the MOST RECENT player from conversation
   - Use exact player name in query
   - For "which team" / "country" / "from": look up batting_team from ball_df using Pattern 11
   - Example: If last answer was "S Sesazi with 630", and user asks "which team is he from?", use:
     `ball_df[ball_df['batter']=='S Sesazi']['batting_team'].value_counts().idxmax()`

8. **Follow-ups with "Who/Which" (no pronouns):**
   - This is a general query about ALL players
   - Do NOT use previous player

9. **Ranking queries ("next", "second", "2nd"):**
   - Use `.nlargest(2).tail(1)` to get 2nd result (preserves player name + value)

10. **"Against them" queries:**
    - Extract team from previous answer
    - Use that team in filter: `ball_df[ball_df['bowling_team']=='Team']`

**COMMON PATTERNS (Copy these exactly):**

**1. Top batters by runs (any format):**
```python
ball_df.groupby('batter')['batsman_runs'].sum().nlargest(5)
```

**2. Top wicket-takers (overall):**
```python
ball_df[ball_df['player_dismissed'].notna()].groupby('bowler').size().nlargest(5)
```

**3. Most runs against a specific team (that team is bowling):**
```python
ball_df[ball_df['bowling_team']=='Pakistan'].groupby('batter')['batsman_runs'].sum().nlargest(1)
```

**4. Most wickets against a specific team (that team is batting):**
```python
ball_df[(ball_df['batting_team']=='Pakistan') & (ball_df['player_dismissed'].notna())].groupby('bowler').size().nlargest(1)
```

**5. Specific player's runs against a team:**
```python
ball_df[(ball_df['batter']=='Player Name') & (ball_df['bowling_team']=='Team Name')]['batsman_runs'].sum()
```

**6. Which team did player score most runs against:**
```python
ball_df[ball_df['batter']=='Player Name'].groupby('bowling_team')['batsman_runs'].sum().nlargest(1)
```

**7. Which team did bowler take most wickets against:**
```python
ball_df[(ball_df['bowler']=='Player Name') & (ball_df['player_dismissed'].notna())].groupby('batting_team').size().nlargest(1)
```

**8. Year-filtered (e.g., 2023):**
```python
pd.merge(ball_df, match_df[['match_id', 'date']], on='match_id').assign(year=lambda x: x['date'].str[:4]).query("year == '2023'").groupby('batter')['batsman_runs'].sum().nlargest(1)
```

**9. Batter performance in specific innings:**
```python
ball_df[(ball_df['batter']=='Name') & (ball_df['innings_number']==1)]['batsman_runs'].sum()
```

**10. Runs in specific over:**
```python
ball_df[(ball_df['match_id']==12345) & (ball_df['innings_number']==1) & (ball_df['over_number']==5)]['total_runs'].sum()
```

**11. Which team/country does a player play for:**
```python
ball_df[ball_df['batter']=='Player Name']['batting_team'].value_counts().idxmax()
```
"""


def extract_recent_player(conversation_history: list) -> str:
    """Extract most recent player from last assistant message."""
    if not conversation_history:
        return None
    
    for msg in reversed(conversation_history):
        if msg.get("role") == "assistant":
            text = msg.get("text", "")
            # Match player names: "Name with X" or "Name scored/took/plays"
            match = re.search(r'([A-Z]\w*(?:\s+[A-Z]\w*){0,2})\s+(?:with|scored|took|plays)', text)
            if match:
                return match.group(1)
    return None


def get_generated_query(question: str, conversation_history: list = None) -> dict:
    """
    Generate pandas query from natural language question.
    
    Args:
        question: User's question
        conversation_history: Previous messages (role, text)
    
    Returns:
        dict with pandas_code, answer_template, chart_suggestion
    """
    try:
        # 1. Get schema
        schema = get_schema()
        schema_str = json.dumps(schema, indent=2)
        system_prompt = SYSTEM_PROMPT.format(schema=schema_str)
        
        # 2. Build conversation context
        context_parts = []
        
        if conversation_history:
            # Add last 4 messages for context (enough but not noisy)
            context_msgs = conversation_history[-4:]
            for msg in context_msgs:
                role = "User" if msg.get("role") == "user" else "Assistant"
                context_parts.append(f"{role}: {msg.get('text', '')}")
            
            # 3. Inject recent player context
            recent_player = extract_recent_player(conversation_history)
            if recent_player:
                # Check if question has pronouns
                pronouns = ['he', 'she', 'him', 'her', 'his', 'they', 'their']
                if any(p in question.lower() for p in pronouns):
                    context_parts.append(f"\n⚠️ Recent player: {recent_player}")
        
        context_str = "\n".join(context_parts) if context_parts else ""
        full_prompt = f"{system_prompt}\n{context_str}\n\nQuestion: {question}"
        
        # 4. Call Gemini (single model, no fallback complexity)
        model = genai.GenerativeModel(PRIMARY_MODEL)
        response = model.generate_content(full_prompt)
        
        if not response or not response.text:
            return {"error": "Empty response from Gemini"}
        
        # 5. Parse response
        response_text = response.text.strip()
        
        # Remove markdown fences if present
        response_text = re.sub(r'^```json\s*|\s*```$', '', response_text)
        
        try:
            result = json.loads(response_text)
        except json.JSONDecodeError:
            # If standard parse fails, try to extract JSON object
            match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if match:
                result = json.loads(match.group(0))
            else:
                return {"error": f"Invalid JSON response: {response_text[:100]}"}
        
        # 6. Validate generated code can execute
        pandas_code = result.get("pandas_code")
        if pandas_code:
            exec_result = engine.execute(pandas_code)
            if "error" in exec_result:
                return {"error": f"Generated code invalid: {exec_result['error']}"}
        
        return result
        
    except Exception as e:
        return {"error": f"AI Service Error: {str(e)}"}
