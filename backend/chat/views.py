"""Chat views - handles the /api/chat/ POST endpoint."""
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class ChatView(APIView):
    """
    POST endpoint for chat functionality.
    
    Receives user questions and orchestrates:
    schema → AI → query engine → response
    """
    
    def post(self, request):
        """Handle POST request with user question."""
        # TODO: Implement orchestration logic
        # 1. Get question from request
        # 2. Get schema from schema_service
        # 3. Send to AI service
        # 4. Execute pandas code via query_engine
        # 5. Return structured response
        return Response(
            {"message": "Chat endpoint skeleton - not yet implemented"},
            status=status.HTTP_501_NOT_IMPLEMENTED
        )
