import json
import logging
from cricket.metrics import CRICKET_METRICS
from cricket.filters import CRICKET_FILTERS
from .mongo_query_engine import get_mongo_engine

logger = logging.getLogger(__name__)

class CricketFunctionCaller:
    """
    Handles function calling - model selects metric + filters,
    we execute the query safely.
    """
    
    def __init__(self):
        self.metrics = CRICKET_METRICS
        self.filters = CRICKET_FILTERS
    
    def get_tools_definition(self):
        """Return function schema for Gemini function calling."""
        return {
            "function_declarations": [{
                "name": "calculate_cricket_metric",
                "description": "Calculate cricket statistic (batting avg, strike rate, etc) based on filters.",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "metric": {
                            "type": "STRING",
                            "description": "Metric to calculate",
                            "enum": list(self.metrics.keys())
                        },
                        "filters": {
                            "type": "ARRAY",
                            "description": "List of filters to apply",
                            "items": {
                                "type": "STRING",
                                "enum": list(self.filters.keys())
                            }
                        },
                        "group_by": {
                            "type": "STRING",
                            "description": "Field to group results by (e.g. batter, bowler, batting_team)",
                            "enum": ["batter", "bowler", "batting_team", "bowling_team", "match_id"]
                        },
                        "limit": {
                            "type": "INTEGER",
                            "description": "Number of top results to return",
                        },
                        "batter": {
                            "type": "STRING",
                            "description": "Name of the batter to filter by (e.g. 'Virat Kohli')"
                        },
                        "bowler": {
                            "type": "STRING",
                            "description": "Name of the bowler to filter by"
                        }
                    },
                    "required": ["metric"]
                }
            }]
        }
    
    def execute_function_call(self, metric, filters=None, group_by="batter", limit=1, batter=None, bowler=None):
        """
        Execute cricket metric calculation.
        """
        if filters is None:
            filters = []
            
        # 1. Validate metric
        if metric not in self.metrics:
            return {
                "error": f"Unknown metric: {metric}",
                "available_metrics": list(self.metrics.keys())
            }
        
        metric_def = self.metrics[metric]
        category = metric_def.get("category", "batting")
        
        # 2. Start with base pipeline (Deep Copy)
        pipeline = json.loads(json.dumps(metric_def["mongodb_query_template"]))
        collection_name = "deliverywise"
        
        # 3. Process Filters
        query_filters = {}
        needs_match_lookup = False
        
        for filter_name in filters:
            if filter_name not in self.filters:
                logger.warning(f"Unknown filter: {filter_name}")
                continue
            
            filter_def = self.filters[filter_name]
            
            # Merge "mongodb_match"
            if "mongodb_match" in filter_def:
                match_criteria = filter_def["mongodb_match"]
                
                # Check if this filter requires matchwise data (e.g. date)
                # We do this by checking keys
                for key, val in match_criteria.items():
                    if key == "date" or key == "venue" or key == "ground_name":
                        needs_match_lookup = True
                        # Remap key to match_details.date
                        query_filters[f"match_details.{key}"] = val
                    else:
                        query_filters[key] = val
            
            # Handle batting/bowling specific filters
            if category == "batting" and "batting_filter" in filter_def:
                query_filters.update(filter_def["batting_filter"])
            elif category == "bowling" and "bowling_filter" in filter_def:
                query_filters.update(filter_def["bowling_filter"])
        
        
        # 3.5 Process Dynamic Filters
        # 3.5 Process Dynamic Filters
        if batter:
            query_filters["batter"] = batter
        
        metric_info = self.metrics.get(metric)
        if not metric_info:
            return f"Metric {metric} not supported.", []
        
        # 4. Inject Lookup if needed
        if needs_match_lookup:
            pipeline.insert(0, {"$unwind": "$match_details"})
            pipeline.insert(0, {
                "$lookup": {
                    "from": "matchwise",
                    "localField": "match_id",
                    "foreignField": "match_id",
                    "as": "match_details"
                }
            })
            
        # 5. Inject Filters ($match)
        # We insert the combined match filters. 
        # If we added a lookup, we insert after unwind (index 2).
        # Otherwise insert at 0.
        insertion_index = 2 if needs_match_lookup else 0
        
        if query_filters:
            pipeline.insert(insertion_index, {"$match": query_filters})

        # 6. Apply Limit
        # Check if user asked for more than default
        user_limit = int(limit) if limit else 1
        
        # Update or append limit
        limit_updated = False
        for stage in pipeline:
            if "$limit" in stage:
                stage["$limit"] = user_limit
                limit_updated = True
                break
        
        if not limit_updated:
            pipeline.append({"$limit": user_limit})
            
        # 7. Execute
        try:
            logger.info(f"Executing Function Call: {metric} | Filters: {filters}")
            engine = get_mongo_engine()
            result = engine.execute(pipeline, collection_name)
            
            # Clean up result for AI context
            # If result["type"] == "list", we might want to flatten it or just return it
            
            response_data = {
                "status": "success",
                "metric": metric_def["name"],
                "filters_applied": filters,
                "type": result.get("type"),
                "data": result.get("data"),
                "explanation": metric_def.get("explanation"),
                "formula": metric_def.get("formula"),
                "pipeline": pipeline
            }
            return response_data
            
        except Exception as e:
            logger.error(f"Execution failed: {str(e)}")
            return {"status": "error", "message": f"Query execution failed: {str(e)}"}

