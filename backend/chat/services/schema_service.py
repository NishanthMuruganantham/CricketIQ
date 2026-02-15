# backend/chat/services/schema_service.py

"""
Schema service providing collection metadata for AI prompt context.
Returns static schema information for MongoDB collections.
"""

# Global cache for schema
_SCHEMA_CACHE = None


def get_schema():
    """
    Returns schema information for the MongoDB collections.
    Used by the AI service to provide context about available data.
    """
    global _SCHEMA_CACHE
    if _SCHEMA_CACHE is not None:
        return _SCHEMA_CACHE

    schema = {
        "deliverywise": {
            "description": "Ball-by-ball delivery data for Men's T20I cricket matches. Each document represents a single delivery.",
            "fields": [
                "match_id", "innings_number", "over_number", "ball_number",
                "batter", "bowler", "non_striker",
                "batting_team", "bowling_team",
                "batsman_runs", "extra_runs", "total_runs",
                "player_dismissed", "dismissal_type", "fielder_name",
            ],
        },
        "matchwise": {
            "description": "Match-level summary data for Men's T20I cricket matches. Each document represents a match.",
            "fields": [
                "match_id", "date",
                "team_1", "team_2",
                "toss_winner", "toss_decision",
                "team_1_total_runs", "team_2_total_runs",
                "winner", "margin_runs", "margin_wickets",
                "ground_name", "ground_city",
                "player_of_the_match",
            ],
        },
    }

    _SCHEMA_CACHE = schema
    return schema
