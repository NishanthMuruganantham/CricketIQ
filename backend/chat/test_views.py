from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from unittest.mock import patch, MagicMock

class ChatViewTest(APITestCase):

    @patch('chat.views.ai_service')
    @patch('chat.views.QueryEngine')
    def test_valid_chat_flow(self, mock_query_engine_class, mock_ai_service):
        """Test a full valid chat flow with chart data extraction."""
        
        # Mock AI Response
        mock_ai_service.get_generated_query.return_value = {
            "pandas_code": "match_df['winner'].value_counts()",
            "answer_template": "The winners are {result}",
            "chart_suggestion": {"type": "bar", "title": "Wins per Team", "x_axis": "Team", "y_axis": "Wins"}
        }

        # Mock Query Engine Execution Result (DataFrame-like list of dicts)
        # Assuming QueryEngine returns dict(type="dataframe", data=[...])
        mock_engine_instance = mock_query_engine_class.return_value
        mock_engine_instance.execute.return_value = {
            "type": "dataframe",
            "data": [
                {"Team": "India", "Wins": 10},
                {"Team": "Australia", "Wins": 8}
            ]
        }

        url = reverse('chat-ask')
        data = {'question': 'Who won matches?'}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['query_executed'], "match_df['winner'].value_counts()")
        
        # Check chart data extraction
        chart_data = response.data['chart_data']
        self.assertIsNotNone(chart_data)
        self.assertEqual(chart_data['type'], 'bar')
        self.assertEqual(chart_data['title'], 'Wins per Team')
        self.assertEqual(chart_data['labels'], ['India', 'Australia'])
        self.assertEqual(chart_data['values'], [10, 8])

    def test_invalid_request(self):
        """Test 400 Bad Request for missing question."""
        url = reverse('chat-ask')
        data = {} # Missing 'question'
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('chat.views.ai_service')
    def test_ai_service_error(self, mock_ai_service):
        """Test API handles AI service errors gracefully."""
        mock_ai_service.get_generated_query.return_value = {"error": "API Unavailable"}
        
        url = reverse('chat-ask')
        data = {'question': 'Test'}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("Error generating query", response.data['answer'])

    @patch('chat.views.ai_service')
    @patch('chat.views.QueryEngine')
    def test_query_engine_error(self, mock_query_engine_class, mock_ai_service):
        """Test API handles pandas execution errors gracefully."""
        mock_ai_service.get_generated_query.return_value = {
            "pandas_code": "bad_code",
            "answer_template": "{result}"
        }
        
        mock_engine_instance = mock_query_engine_class.return_value
        mock_engine_instance.execute.return_value = {"error": "SyntaxError"}

        url = reverse('chat-ask')
        data = {'question': 'Test'}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("Error executing query", response.data['answer'])
