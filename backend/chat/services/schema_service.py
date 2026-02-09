import os
import pandas as pd
from django.conf import settings

# Global cache for schema
_SCHEMA_CACHE = None

MATCH_DATA_FILE = "matchwise_data.csv"
DELIVERY_DATA_FILE = "deliverywise_data.csv"

def get_schema():
    """
    Reads CSVs and returns a dictionary with schema information.
    Caches the result after the first read.
    """
    global _SCHEMA_CACHE
    if _SCHEMA_CACHE is not None:
        return _SCHEMA_CACHE

    # Construct absolute paths
    data_dir = os.path.join(settings.BASE_DIR, "data")
    match_path = os.path.join(data_dir, MATCH_DATA_FILE)
    delivery_path = os.path.join(data_dir, DELIVERY_DATA_FILE)

    schema = {}

    # Process Match Data
    if os.path.exists(match_path):
        try:
            df = pd.read_csv(match_path)
            schema["match_df"] = {
                "columns": list(df.columns),
                "description": "Match data for cricket matches. Each row represents a match.",
                "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
                "sample_rows": df.head(5).to_dict(orient="records"),
                "row_count": len(df)
            }
        except Exception as e:
            schema["match_df"] = {"error": f"Failed to read file: {str(e)}"}
    else:
        schema["match_df"] = {"error": "File not found"}

    # Process Delivery Data
    if os.path.exists(delivery_path):
        try:
            df = pd.read_csv(delivery_path)
            schema["ball_df"] = {
                "columns": list(df.columns),
                "description": "Delivery data for cricket matches. Each row represents a delivery.",
                "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
                "sample_rows": df.head(5).to_dict(orient="records"),
                "row_count": len(df)
            }
        except Exception as e:
            schema["ball_df"] = {"error": f"Failed to read file: {str(e)}"}
    else:
        schema["ball_df"] = {"error": "File not found"}

    _SCHEMA_CACHE = schema
    return schema
