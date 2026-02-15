CRICKET_METRICS = {
    # --- BATTING METRICS ---
    "batting_average": {
        "name": "Batting Average",
        "description": "Runs per dismissal",
        "category": "batting",
        "better_when": "higher",
        "formula": "SUM(batsman_runs) / COUNT(dismissals_only)",
        "explanation": "Only count innings where player was OUT. Exclude not-outs.",
        "minimum_threshold": {
            "metric": "dismissals",
            "value": 5,
            "explanation": "Need at least 5 dismissals to be statistically valid"
        },
        "mongodb_query_template": [
            {"$match": {"player_dismissed": {"$ne": None}}},
            {"$group": {
                "_id": "$batter",
                "runs": {"$sum": "$batsman_runs"},
                "dismissals": {"$sum": 1}
            }},
            {"$project": {
                "_id": 1,
                "runs": 1,
                "dismissals": 1,
                "average": {"$divide": ["$runs", "$dismissals"]}
            }},
            {"$match": {"dismissals": {"$gte": 5}}},
            {"$sort": {"average": -1}}
        ],
        "example": "Player: 500 runs in 8 dismissals (2 not-outs) = 62.5 average",
        "critical_notes": [
            "NOT runs/innings - only dismissals count",
            "Not-outs don't count as dismissals",
            "Minimum 5 dismissals for validity"
        ]
    },
    
    "strike_rate": {
        "name": "Strike Rate",
        "description": "Runs per 100 balls faced",
        "category": "batting",
        "better_when": "higher",
        "formula": "(SUM(batsman_runs) / COUNT(balls)) * 100",
        "explanation": "All balls count, including not-outs.",
        "minimum_threshold": {
            "metric": "balls",
            "value": 20,
            "explanation": "Need at least 20 balls for valid sample"
        },
        "mongodb_query_template": [
            {"$group": {
                "_id": "$batter",
                "runs": {"$sum": "$batsman_runs"},
                "balls": {"$sum": 1}
            }},
            {"$project": {
                "_id": 1,
                "runs": 1,
                "balls": 1,
                "strike_rate": {
                    "$multiply": [
                        {"$divide": ["$runs", "$balls"]},
                        100
                    ]
                }
            }},
            {"$match": {"balls": {"$gte": 20}}},
            {"$sort": {"strike_rate": -1}}
        ],
        "example": "100 runs in 80 balls = 125 strike rate",
        "critical_notes": [
            "All deliveries count",
            "Not-outs included in balls faced",
            "Minimum 20 balls for validity"
        ]
    },

    "total_runs": {
        "name": "Total Runs",
        "description": "Total runs scored",
        "category": "batting",
        "better_when": "higher",
        "formula": "SUM(batsman_runs)",
        "explanation": "Total runs matched by filter conditions",
        "minimum_threshold": {
            "metric": "runs",
            "value": 1,
            "explanation": "Exclude players with 0 runs"
        },
        "mongodb_query_template": [
            {"$group": {
                "_id": "$batter",
                "total_runs": {"$sum": "$batsman_runs"},
                "innings": {"$sum": 1}
            }},
            {"$match": {"total_runs": {"$gt": 0}}},
            {"$sort": {"total_runs": -1}}
        ],
        "example": "Player A: 450 runs",
        "critical_notes": ["Simple sum of runs"]
    },

    "highest_score": {
        "name": "Highest Score",
        "description": "Highest individual score in an innings",
        "category": "batting",
        "better_when": "higher",
        "formula": "MAX(sum_runs_per_innings)",
        "explanation": "Highest runs scored by a batter in a single match innings",
        "minimum_threshold": None,
        "mongodb_query_template": [
            {"$group": {
                "_id": {"batter": "$batter", "match_id": "$match_id"},
                "runs": {"$sum": "$batsman_runs"}
            }},
            {"$group": {
                "_id": "$_id.batter",
                "highest_score": {"$max": "$runs"}
            }},
            {"$sort": {"highest_score": -1}}
        ],
        "example": "Player A: 122 runs",
        "critical_notes": ["Need to group by match_id first"]
    },

    # --- BOWLING METRICS ---
    "bowling_average": {
        "name": "Bowling Average",
        "description": "Runs conceded per wicket",
        "category": "bowling",
        "better_when": "lower",
        "formula": "SUM(runs_conceded) / COUNT(wickets)",
        "explanation": "Total runs conceded divided by wickets taken. Lower is better.",
        "minimum_threshold": {
            "metric": "wickets",
            "value": 10,
            "explanation": "Need at least 10 wickets for meaningful average"
        },
        "mongodb_query_template": [
            {"$match": {"player_dismissed": {"$ne": None}}},
            {"$group": {
                "_id": "$bowler",
                "runs_conceded": {"$sum": "$total_runs"},
                "wickets": {"$sum": 1}
            }},
            {"$project": {
                "_id": 1,
                "runs_conceded": 1,
                "wickets": 1,
                "average": {"$divide": ["$runs_conceded", "$wickets"]}
            }},
            {"$match": {"wickets": {"$gte": 10}}},
            {"$sort": {"average": 1}}
        ],
        "example": "80 runs in 5 wickets = 16.0 bowling average",
        "critical_notes": [
            "Lower is better (opposite of batting avg)",
            "Only count dismissals",
            "Can't compare fast bowlers vs spinners directly"
        ]
    },
    
    "economy_rate": {
        "name": "Economy Rate",
        "description": "Runs conceded per over",
        "category": "bowling",
        "better_when": "lower",
        "formula": "SUM(runs_conceded) / COUNT(overs_bowled)",
        "explanation": "Total runs conceded per over bowled. Lower means tighter bowling.",
        "minimum_threshold": {
            "metric": "overs",
            "value": 5,
            "explanation": "Need at least 5 overs for validity"
        },
        "mongodb_query_template": [
            # Group by over to count overs bowled
            {"$group": {
                "_id": {"bowler": "$bowler", "over": "$over_number", "match_id": "$match_id"},
                "runs": {"$sum": "$total_runs"}
            }},
            {"$group": {
                "_id": "$_id.bowler",
                "total_runs": {"$sum": "$runs"},
                "overs": {"$sum": 1}
            }},
            {"$project": {
                "_id": 1,
                "total_runs": 1,
                "overs": 1,
                "economy": {"$divide": ["$total_runs", "$overs"]}
            }},
            {"$match": {"overs": {"$gte": 5}}},
            {"$sort": {"economy": 1}}
        ],
        "example": "35 runs in 5 overs = 7.0 economy rate",
        "critical_notes": [
            "Count distinct overs, not balls",
            "Lower is better",
            "More reliable than average for short samples"
        ]
    },

    "most_wickets": {
        "name": "Most Wickets",
        "description": "Total wickets taken",
        "category": "bowling",
        "better_when": "higher",
        "formula": "COUNT(player_dismissed)",
        "explanation": "Total number of wickets taken",
        "minimum_threshold": {
            "metric": "wickets",
            "value": 1,
            "explanation": "Exclude players with 0 wickets"
        },
        "mongodb_query_template": [
            {"$match": {"player_dismissed": {"$ne": None}}},
            {"$group": {
                "_id": "$bowler",
                "wickets": {"$sum": 1}
            }},
            {"$match": {"wickets": {"$gt": 0}}},
            {"$sort": {"wickets": -1}}
        ],
        "example": "Player A: 45 wickets",
        "critical_notes": ["Only count valid dismissals"]
    }
}
