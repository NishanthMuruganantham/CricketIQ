from django.test import TestCase
from chat.services import query_engine
import pandas as pd
from unittest.mock import MagicMock

class QueryEngineTest(TestCase):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Mock the data loading
        cls.mock_match_df = pd.DataFrame({
            "match_id": [1, 2, 3],
            "winner": ["Australia", "India", "Australia"],
            "margin_runs": [10, 5, 20]
        })
        cls.mock_ball_df = pd.DataFrame({
            "match_id": [1, 1, 1],
            "batter": ["Smith", "Smith", "Warner"],
            "batsman_runs": [4, 6, 1]
        })
        
        # We need to hack the engine instance in the module because it's instantiated on import.
        # Ideally, we'd mock the constructor, but since it's already instantiated,
        # let's just replace the dataframes on the existing instance.
        query_engine.engine.match_df = cls.mock_match_df
        query_engine.engine.ball_df = cls.mock_ball_df

    def test_execute_eval_expression(self):
        """Test simple pandas expression using eval."""
        code = "match_df['margin_runs'].sum()"
        response = query_engine.engine.execute(code)
        
        self.assertEqual(response["data"], 35)
        self.assertEqual(response["type"], "value")

    def test_return_dataframe(self):
        """Test returning a DataFrame."""
        code = "match_df[['match_id', 'winner']]"
        response = query_engine.engine.execute(code)
        
        self.assertEqual(response["type"], "dataframe")
        # to_dict() default is 'dict' (column-oriented), so len is number of columns (2)
        self.assertEqual(len(response["data"]), 2)
        self.assertIn("match_id", response["data"])
        self.assertIn("winner", response["data"])

    def test_return_series(self):
        """Test returning a Series."""
        code = "match_df['winner']"
        response = query_engine.engine.execute(code)
        
        self.assertEqual(response["type"], "series")
        self.assertEqual(response["data"][0], "Australia")

    def test_security_import(self):
        """Test that import is blocked."""
        code = "import os"
        response = query_engine.engine.execute(code)
        self.assertEqual(response, {"error": "Blocked operation detected."})

    def test_security_exec(self):
        """Test that exec keyword is blocked."""
        code = "exec('print(1)')"
        response = query_engine.engine.execute(code)
        self.assertEqual(response, {"error": "Blocked operation detected."})

    def test_security_dunder(self):
        """Test that dunder access is blocked."""
        code = "match_df.__class__"
        response = query_engine.engine.execute(code)
        self.assertEqual(response, {"error": "Blocked operation detected."})

    def test_syntax_error(self):
        """Test invalid syntax handling."""
        code = "match_df["  # unclosed bracket
        response = query_engine.engine.execute(code)
        self.assertIn("error", response)
        self.assertNotEqual(response["error"], "Blocked operation detected.")
