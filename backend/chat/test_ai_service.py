from django.test import TestCase
from unittest.mock import patch, MagicMock
from chat.services import ai_service
import json

class AIServiceTest(TestCase):
    
    @patch('chat.services.ai_service.genai.GenerativeModel')
    @patch('chat.services.ai_service.get_schema')
    def test_get_generated_query_success(self, mock_get_schema, mock_model_class):
        """Test successful generation of query from mocked Gemini response."""
        
        # Mock Schema
        mock_get_schema.return_value = {
            "match_df": {"columns": ["match_id", "winner"]},
            "ball_df": {"columns": ["match_id", "batter", "runs"]}
        }
        
        # Mock Gemini Response
        mock_chat = MagicMock()
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "pandas_code": "match_df['winner'].value_counts()",
            "answer_template": "Winner counts: {result}",
            "chart_suggestion": {"type": "bar"}
        })
        mock_chat.send_message.return_value = mock_response
        
        mock_model_instance = MagicMock()
        mock_model_instance.start_chat.return_value = mock_chat
        mock_model_class.return_value = mock_model_instance
        
        # Execute
        result = ai_service.get_generated_query("Who won the most matches?")
        
        # Assertions
        self.assertIn("pandas_code", result)
        self.assertEqual(result["pandas_code"], "match_df['winner'].value_counts()")
        
        # Verify prompt construction (schema injection)
        mock_model_instance.start_chat.assert_called_once()
        args, _ = mock_chat.send_message.call_args
        prompt_sent = args[0]
        # self.assertIn("SYSTEM_PROMPT", str(ai_service.SYSTEM_PROMPT)[:20]) 
        self.assertIn("You are a cricket statistics assistant", str(ai_service.SYSTEM_PROMPT)) # Check prompt template content
        self.assertIn("match_id", prompt_sent) # Check schema content in prompt

    @patch('chat.services.ai_service.genai.GenerativeModel')
    def test_get_generated_query_markdown_cleaning(self, mock_model_class):
        """Test that markdown fences are stripped from response."""
        
        mock_chat = MagicMock()
        mock_response = MagicMock()
        # Response with markdown fences
        mock_response.text = "```json\n{\"pandas_code\": \"test\"}\n```" 
        mock_chat.send_message.return_value = mock_response
        
        mock_model_instance = MagicMock()
        mock_model_instance.start_chat.return_value = mock_chat
        mock_model_class.return_value = mock_model_instance
        
        result = ai_service.get_generated_query("test")
        self.assertEqual(result["pandas_code"], "test")

    @patch('chat.services.ai_service.genai.GenerativeModel')
    def test_gemini_error_handling(self, mock_model_class):
        """Test handling of API errors."""
        
        mock_model_class.side_effect = Exception("API connection failed")
        
        result = ai_service.get_generated_query("test")
        self.assertIn("error", result)
        self.assertIn("API connection failed", result["error"])
