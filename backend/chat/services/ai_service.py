# backend/chat/services/ai_service.py

"""
MongoDB-based AI query generation service.
Generates MongoDB aggregation pipelines instead of Pandas code.
"""

import google.generativeai as genai
from decouple import config
import json
import re
from .schema_service import get_schema
from .mongo_query_engine import get_mongo_engine

# Configure Gemini
genai.configure(api_key=config("GEMINI_API_KEY"))

# Model priority list - try them in order
# User requested "Gemini 2.5 Pro" - Confirmed availability
MODELS = ["gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.0-flash", "gemma-3-27b-it"]

# MongoDB System Prompt (from SYSTEM_PROMPT_MONGODB.py)
SYSTEM_PROMPT = """
You are a cricket statistics assistant for Men's T20I data stored in MongoDB.

Available Collections:
- `deliverywise`: Ball-by-ball delivery data (one document per delivery)
- `matchwise`: Match-level summary data (one document per match)

{schema}

Generate ONLY valid MongoDB aggregation pipelines. Return as JSON:

{{
    "pipeline": [<valid MongoDB aggregation stages>],
    "collection": "deliverywise | matchwise",
    "answer_template": "<response text with {{result}} placeholder>",
    "chart_suggestion": {{
        "type": "bar|line|pie|null",
        "title": "...",
        "x_axis": "...",
        "y_axis": "..."
    }}
}}

**CRITICAL: Collections & Fields**

deliverywise Collection Fields:
- `match_id`, `innings_number`, `over_number`, `ball_number`
- `batter`, `bowler`, `non_striker`
- `batting_team`, `bowling_team`
- `batsman_runs`, `extra_runs`, `total_runs`
- `player_dismissed`, `dismissal_type`, `fielder_name`
- **NOTE**: `date` is NOT in `deliverywise`. Join with `matchwise` for dates.

matchwise Collection Fields:
- `match_id`, `date` (YYYY-MM-DD string)
- `team_1`, `team_2`
- `toss_winner`, `toss_decision`
- `team_1_total_runs`, `team_2_total_runs`
- `winner`, `margin_runs`, `margin_wickets`
- `ground_name`, `ground_city`
- `player_of_the_match`
- **NOTE**: `team_1` and `team_2` typically represent the countries.

**CRITICAL RULES:**

1. Generate ONLY valid MongoDB aggregation pipeline (list of stages)
2. Use $match, $group, $sort, $limit, $project, $lookup only
3. Stats queries: Group + sum/count, sort descending, limit 1
4. Always return both identifier AND value
5. **Null Handling**:
   - For categorical fields (e.g., `player_of_the_match`, `winner`, `city`), ALWAYS filter out nulls: `{"$match": {"field": {"$ne": null}}}` BEFORE grouping.
6. **Country/Nationality**:
   - If asked for a player's country, use `bowling_team` (for bowlers) or `batting_team` (for batters) from `deliverywise`.
   - Example: `{"$match": {"bowler": "Player Name"}}`, `{"$project": {"country": "$bowling_team"}}`, `{"$limit": 1}`.
7. **Team vs Opponent Logic (CRITICAL)**:
   - **"Playing for Team X"**:
     - Batter: `{"batting_team": "Team X"}`
     - Bowler: `{"bowling_team": "Team X"}`
   - **"Playing against Team Y"**:
     - Batter: `{"bowling_team": "Team Y"}` (The team bowling to them is the opponent)
     - Bowler: `{"batting_team": "Team Y"}` (The team they are bowling to is the opponent)
   - **Result/Match Filtering**:
     - Prefer filtering `deliverywise` directly for team specific stats: `{"$match": {"batting_team": "Australia"}}`.
     - Do NOT use `matchwise.team_1` or `team_2` unless filtering for a match where *either* team played.
8. **Breaking Down by Opponent (CRITICAL)**:
   - **"Against which team?"** means group by the *opponent*:
     - **Batter**: Group by `bowling_team` (The teams bowling to them).
     - **Bowler**: Group by `batting_team` (The teams they are bowling to).
     - Example (Bowler vs Teams): `{"$group": {"_id": "$batting_team", "wickets": {"$sum": 1}}}`.

6. **Date/Team/Venue Filtering**:
   - **START with `matchwise`** collection if filtering by date, team, or venue.
   - Filter `matchwise` first, THEN `$lookup` `deliverywise`.
   - Resulting collection in JSON should be "matchwise".
   
   Example (Most runs in 2023):
   ```json
   {
       "pipeline": [
           { "$match": { "date": { "$gte": "2023-01-01", "$lt": "2024-01-01" } } },
           {
               "$lookup": {
                   "from": "deliverywise",
                   "localField": "match_id",
                   "foreignField": "match_id",
                   "as": "deliveries"
               }
           },
           { "$unwind": "$deliveries" },
           {
               "$group": {
                   "_id": "$deliveries.batter",
                   "total_runs": { "$sum": "$deliveries.batsman_runs" }
               }
           },
           { "$sort": { "total_runs": -1 } },
           { "$limit": 1 }
       ],
       "collection": "matchwise"
   }
   ```
6. Return as JSON with pipeline, collection, answer_template

**Common Patterns:**

Top Scorers:
[
  {"$group": {"_id": "$batter", "total_runs": {"$sum": "$batsman_runs"}}},
  {"$sort": {"total_runs": -1}},
  {"$limit": 1}
]

Top Wicket-Takers:
[
  {"$match": {"player_dismissed": {"$ne": null}}},
  {"$group": {"_id": "$bowler", "wickets": {"$sum": 1}}},
  {"$sort": {"wickets": -1}},
  {"$limit": 1}
]

Year-Filtered (2023):
[
  {"$match": {"date": {"$gte": ISODate("2023-01-01"), "$lt": ISODate("2024-01-01")}}},
  {"$group": {"_id": "$batter", "total_runs": {"$sum": "$batsman_runs"}}},
  {"$sort": {"total_runs": -1}},
  {"$limit": 1}
]

Against Team (Pakistan):
[
  {"$match": {"bowling_team": "Pakistan"}},
  {"$group": {"_id": "$batter", "total_runs": {"$sum": "$batsman_runs"}}},
  {"$sort": {"total_runs": -1}},
  {"$limit": 1}
]
"""


def extract_recent_player(conversation_history: list) -> str:
    """Extract most recent player from conversation history."""
    if not conversation_history:
        return None
    
    for msg in reversed(conversation_history):
        if msg.get("role") == "assistant":
            text = msg.get("text", "")
            # Match player names: "Name with X" or "Name scored/took"
            match = re.search(r'([A-Z]\w*(?:\s+[A-Z]\w*){0,2})\s+(?:with|scored|took|plays)', text)
            if match:
                return match.group(1)
    return None


def get_generated_query(question: str, conversation_history: list = None) -> dict:
    """
    Generate MongoDB aggregation pipeline from natural language question.
    
    Args:
        question: User's question
        conversation_history: Previous messages (role, text)
    
    Returns:
        dict with pipeline, collection, answer_template, chart_suggestion
    """
    selected_model = None
    last_error = None

    try:
        # 1. Get schema
        schema = get_schema()
        schema_str = json.dumps(schema, indent=2)
        system_prompt = SYSTEM_PROMPT.replace("{schema}", schema_str)
        
        # 2. Build conversation context
        context_parts = []
        
        if conversation_history:
            # Add last 4 messages for context
            context_msgs = conversation_history[-4:]
            for msg in context_msgs:
                role = "User" if msg.get("role") == "user" else "Assistant"
                context_parts.append(f"{role}: {msg.get('text', '')}")
            
            # 3. Inject recent player context
            recent_player = extract_recent_player(conversation_history)
            if recent_player:
                pronouns = ['he', 'she', 'him', 'her', 'his', 'they', 'their']
                if any(p in question.lower() for p in pronouns):
                    context_parts.append(f"\n⚠️ Recent player: {recent_player}")
        
        context_str = "\n".join(context_parts) if context_parts else ""
        full_prompt = f"{system_prompt}\n{context_str}\n\nQuestion: {question}"
        
        errors = {}
        
        # 4. Call AI Model with Fallback
        for model_name in MODELS:
            try:
                print(f"Trying model: {model_name}")
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(full_prompt)
                
                if response and response.text:
                    selected_model = model_name
                    response_text = response.text.strip()
                    break # Success!
                    
            except Exception as e:
                error_str = str(e)
                print(f"Model {model_name} failed: {error_str}")
                errors[model_name] = error_str
                last_error = e
                continue
        
        if not selected_model:
            # Check if failures were due to rate limits
            rate_limited_models = []
            for name, err in errors.items():
                if "429" in err or "ResourceExhausted" in err or "quota" in err.lower():
                    rate_limited_models.append(name)
            
            if rate_limited_models:
                models_str = ", ".join(rate_limited_models)
                return {"error": f"Rate limit exceeded for {models_str}. Please try again in a moment."}
                
            return {"error": f"All models failed. Last error: {last_error}"}

        # 5. Parse response
        # Remove markdown fences if present
        response_text = re.sub(r'^```json\s*|\s*```$', '', response_text)
        
        try:
            result = json.loads(response_text)
        except json.JSONDecodeError:
            # Try regex extraction
            match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if match:
                result = json.loads(match.group(0))
            else:
                return {"error": f"Invalid JSON response from {selected_model}: {response_text[:100]}"}
        
        # 6. Validate pipeline
        pipeline = result.get("pipeline")
        collection = result.get("collection", "deliverywise")
        
        if not pipeline or not isinstance(pipeline, list):
            return {"error": "Invalid pipeline: must be a list of MongoDB stages"}
        
        if collection not in ["deliverywise", "matchwise"]:
            return {"error": f"Invalid collection: {collection}"}
        
        # 7. Validate pipeline structure (basic check)
        for stage in pipeline:
            if not isinstance(stage, dict) or len(stage) != 1:
                return {"error": "Invalid pipeline stage format"}
            stage_op = list(stage.keys())[0]
            if not stage_op.startswith("$"):
                return {"error": f"Invalid stage operator: {stage_op}"}
        
        return result
        
    except Exception as e:
        return {"error": f"AI Service Error: {str(e)}"}