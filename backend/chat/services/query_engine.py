import pandas as pd
import os
from django.conf import settings

BLOCKED_KEYWORDS = ["import", "open", "os.", "sys.", "exec", "eval", "__"]

class QueryEngine:
    """Loads both CSVs once and safely executes AI-generated pandas code."""

    def __init__(self, match_csv_path: str, ball_csv_path: str):
        self.match_df = pd.read_csv(match_csv_path)
        self.ball_df = pd.read_csv(ball_csv_path)

    def get_schema(self) -> dict:
        """Returns schema for both DataFrames — fed into the AI system prompt."""
        return {
            "match_df": {
                "columns": list(self.match_df.columns),
                "dtypes": self.match_df.dtypes.astype(str).to_dict(),
                "sample": self.match_df.head(3).to_dict(),
                "shape": self.match_df.shape
            },
            "ball_df": {
                "columns": list(self.ball_df.columns),
                "dtypes": self.ball_df.dtypes.astype(str).to_dict(),
                "sample": self.ball_df.head(3).to_dict(),
                "shape": self.ball_df.shape
            }
        }

    def execute(self, pandas_code: str) -> dict:
        """Executes pandas code in a sandboxed scope. Only match_df, ball_df, and pd are available."""
        for keyword in BLOCKED_KEYWORDS:
            if keyword in pandas_code:
                return {"error": "Blocked operation detected."}

        try:
            # Only these three names are available to the AI-generated code
            safe_scope = {
                "match_df": self.match_df,
                "ball_df": self.ball_df,
                "pd": pd
            }
            # Note: __builtins__ is set to empty dict {} — this is a critical extra layer of safety.
            result = eval(pandas_code, {"__builtins__": {}}, safe_scope)

            # Normalize result for JSON serialization
            if isinstance(result, pd.Series):
                return {"type": "series", "data": result.to_dict()}
            elif isinstance(result, pd.DataFrame):
                return {"type": "dataframe", "data": result.to_dict()}
            else:
                return {"type": "value", "data": result}

        except Exception as e:
            return {"error": str(e)}

# Instantiate the engine
_data_dir = os.path.join(settings.BASE_DIR, "data")
_match_csv = os.path.join(_data_dir, "matchwise_data.csv")
_ball_csv = os.path.join(_data_dir, "deliverywise_data.csv")

# Create a singleton instance to be used by views
engine = QueryEngine(_match_csv, _ball_csv)
