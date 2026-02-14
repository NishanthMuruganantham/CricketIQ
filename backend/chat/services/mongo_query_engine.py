# backend/chat/services/mongo_query_engine.py

"""
MongoDB-based query execution engine.
Replaces Pandas DataFrame operations with MongoDB aggregation pipelines.
"""

from pymongo import MongoClient
from pymongo.errors import PyMongoError
import os
import json
import certifi
from decouple import config

class MongoQueryEngine:
    """Execute MongoDB aggregation pipelines for cricket data queries."""
    
    def __init__(self, mongo_uri: str = None):
        """
        Initialize MongoDB connection.
        
        Args:
            mongo_uri: MongoDB connection string (defaults to env var MONGO_URI)
        """
        self.mongo_uri = mongo_uri or config("MONGO_URI", default="mongodb://localhost:27017")
        self.db_name = config("MONGO_DB", default="cricketiq")
        self.collection_deliverywise = config("MONGO_COLLECTION_DELIVERYWISE", default="deliverywise")
        self.collection_matchwise = config("MONGO_COLLECTION_MATCHWISE", default="matchwise")
        
        # Map logical names to actual collection names
        self.collection_map = {
            "deliverywise": self.collection_deliverywise,
            "matchwise": self.collection_matchwise,
        }
        
        try:
            self.client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=5000, tlsCAFile=certifi.where())
            self.db = self.client[self.db_name]
            
            # Verify connection
            self.client.admin.command('ping')
            print(f"✅ MongoDB connection successful (db: {self.db_name})")
            
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            raise
    
    def get_collections(self):
        """Get references to collections."""
        return {
            "deliverywise": self.db[self.collection_deliverywise],
            "matchwise": self.db[self.collection_matchwise]
        }
    
    def execute(self, pipeline: list, collection: str = "deliverywise") -> dict:
        """
        Execute MongoDB aggregation pipeline.
        
        Args:
            pipeline: MongoDB aggregation pipeline (list of stages)
            collection: Collection to query ("deliverywise" or "matchwise")
        
        Returns:
            dict with result data or error
        """
        try:
            if not isinstance(pipeline, list):
                return {"error": "Pipeline must be a list of MongoDB stages"}
            
            if collection not in self.collection_map:
                return {"error": f"Unknown collection: {collection}"}
            
            actual_collection_name = self.collection_map[collection]
            col = self.db[actual_collection_name]
            result = list(col.aggregate(pipeline))
            
            # Normalize result format for API response
            if len(result) == 1:
                # Single document result
                doc = result[0]
                # Remove MongoDB's internal _id if present
                if '_id' in doc and isinstance(doc['_id'], str):
                    # Keep _id if it's meaningful (e.g., player name from groupby)
                    return {"type": "dict", "data": doc}
                else:
                    # Remove _id for cleaner responses
                    doc.pop('_id', None)
                    return {"type": "dict", "data": doc}
            
            elif len(result) == 0:
                return {"type": "empty", "data": None}
            
            else:
                # Multiple documents
                # Clean up _id fields from aggregation results
                for doc in result:
                    if '_id' in doc and not isinstance(doc['_id'], str):
                        doc.pop('_id', None)
                
                return {"type": "list", "data": result}
        
        except PyMongoError as e:
            return {"error": f"MongoDB error: {str(e)}"}
        except Exception as e:
            return {"error": f"Query execution error: {str(e)}"}
    
    def validate_pipeline(self, pipeline: list) -> bool:
        """
        Validate MongoDB aggregation pipeline structure.
        
        Args:
            pipeline: MongoDB aggregation pipeline
        
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(pipeline, list):
            return False
        
        if len(pipeline) == 0:
            return False
        
        # Check all stages are dicts with single key (stage operator)
        valid_stages = [
            "$match", "$group", "$sort", "$limit", "$project",
            "$lookup", "$unwind", "$skip", "$facet", "$bucket"
        ]
        
        for stage in pipeline:
            if not isinstance(stage, dict):
                return False
            if len(stage) != 1:
                return False
            if not any(op in stage for op in valid_stages):
                return False
        
        return True
    
    def create_indexes(self):
        """Create recommended indexes for fast queries."""
        try:
            deliverywise = self.db[self.collection_deliverywise]
            matchwise = self.db[self.collection_matchwise]
            
            print("📊 Creating indexes...")
            
            # Deliverywise indexes
            deliverywise.create_index([("batter", 1)])
            deliverywise.create_index([("bowler", 1)])
            deliverywise.create_index([("bowling_team", 1)])
            deliverywise.create_index([("batting_team", 1)])
            deliverywise.create_index([("match_id", 1), ("innings_number", 1)])
            deliverywise.create_index([("player_dismissed", 1)])
            deliverywise.create_index([("date", 1)])  # For year filtering
            
            # Matchwise indexes
            matchwise.create_index([("date", 1)])
            matchwise.create_index([("team_1", 1)])
            matchwise.create_index([("team_2", 1)])
            matchwise.create_index([("winner", 1)])
            matchwise.create_index([("match_id", 1)])
            
            print("✅ Indexes created successfully")
        
        except Exception as e:
            print(f"⚠️ Index creation warning: {e}")
    
    def close(self):
        """Close MongoDB connection."""
        self.client.close()


# Singleton instance
_engine = None

def get_mongo_engine() -> MongoQueryEngine:
    """Get or create MongoDB query engine instance."""
    global _engine
    if _engine is None:
        _engine = MongoQueryEngine()
    return _engine