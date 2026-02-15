CRICKET_FILTERS = {
    # --- TIME-BASED FILTERS ---
    "in_2023": {
        "name": "Year 2023",
        "description": "Matches in 2023 only",
        "applies_to": "all",
        "mongodb_match": {
            "date": {
                "$gte": "2023-01-01",
                "$lt": "2024-01-01"
            }
        },
        "note": "Use matchwise collection for date filtering or lookup"
    },
    
    "in_2024": {
        "name": "Year 2024",
        "description": "Matches in 2024 only",
        "applies_to": "all",
        "mongodb_match": {
            "date": {
                "$gte": "2024-01-01",
                "$lt": "2025-01-01"
            }
        }
    },

    "in_2022": {
        "name": "Year 2022",
        "description": "Matches in 2022 only",
        "applies_to": "all",
        "mongodb_match": {
            "date": {
                "$gte": "2022-01-01",
                "$lt": "2023-01-01"
            }
        }
    },
    
    # --- POWERPLAY / PHASE FILTERS ---
    "first_6_overs": {
        "name": "First 6 Overs (Powerplay)",
        "description": "Powerplay overs only (0.1 to 5.6)",
        "applies_to": ["batting", "bowling"],
        "mongodb_match": {
            "over_number": {"$lte": 6}
        },
        "critical_note": "Powerplay = first 6 overs in T20I (Overs 1-6)"
    },
    
    "death_overs": {
        "name": "Death Overs",
        "description": "Final overs (16-20)",
        "applies_to": ["batting", "bowling"],
        "mongodb_match": {
            "over_number": {"$gte": 15}
        },
        "critical_note": "Overs 16-20 in T20I"
    },
    
    "middle_overs": {
        "name": "Middle Overs",
        "description": "Overs 7-15",
        "applies_to": ["batting", "bowling"],
        "mongodb_match": {
            "over_number": {"$gt": 6, "$lt": 16} 
        }
    },
    
    # --- OPPONENT FILTERS ---
    "vs_india": {
        "name": "vs India",
        "description": "Playing against India",
        "applies_to": ["batting", "bowling"],
        "note": "Context dependent: If batting, bowling_team=India. If bowling, batting_team=India",
        "batting_filter": {"bowling_team": "India"},
        "bowling_filter": {"batting_team": "India"}
    },
    
    "vs_pakistan": {
        "name": "vs Pakistan",
        "description": "Playing against Pakistan",
        "applies_to": ["batting", "bowling"],
        "batting_filter": {"bowling_team": "Pakistan"},
        "bowling_filter": {"batting_team": "Pakistan"}
    },
    
    "vs_australia": {
        "name": "vs Australia",
        "description": "Playing against Australia",
        "applies_to": ["batting", "bowling"],
        "batting_filter": {"bowling_team": "Australia"},
        "bowling_filter": {"batting_team": "Australia"}
    },

    "vs_england": {
        "name": "vs England",
        "description": "Playing against England",
        "applies_to": ["batting", "bowling"],
        "batting_filter": {"bowling_team": "England"},
        "bowling_filter": {"batting_team": "England"}
    },

    "vs_new_zealand": {
        "name": "vs New Zealand",
        "description": "Playing against New Zealand",
        "applies_to": ["batting", "bowling"],
        "batting_filter": {"bowling_team": "New Zealand"},
        "bowling_filter": {"batting_team": "New Zealand"}
    },
    
    # --- BOWLING TYPE FILTERS ---
    "vs_pace_bowlers": {
        "name": "vs Pace Bowlers",
        "description": "Against pace bowling only",
        "applies_to": ["batting"],
        "mongodb_match": {"bowler_style": {"$in": ["Right-arm fast", "Left-arm fast", "Right-arm fast-medium", "Left-arm fast-medium", "Right-arm medium-fast", "Left-arm medium-fast", "Right-arm medium", "Left-arm medium"]}}
    },
    
    "vs_spinners": {
        "name": "vs Spinners",
        "description": "Against spin bowling only",
        "applies_to": ["batting"],
        "mongodb_match": {"bowler_style": {"$in": ["Right-arm legbreak", "Left-arm chinaman", "Right-arm offbreak", "Left-arm orthodox", "Legbreak", "Legbreak googly"]}}
    },

    # --- INNINGS FILTERS ---
    "first_innings": {
        "name": "First Innings",
        "description": "Batting/Bowling in the 1st innings",
        "applies_to": "all",
        "mongodb_match": {"innings_number": 1}
    },
    
    "second_innings": {
        "name": "Second Innings (Chasing)",
        "description": "Batting/Bowling in the 2nd innings",
        "applies_to": "all",
        "mongodb_match": {"innings_number": 2}
    }
}
