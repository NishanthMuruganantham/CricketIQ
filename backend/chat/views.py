from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ChatRequestSerializer, ChatResponseSerializer
from .services import ai_service
from .services.query_engine import engine
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class ChatView(APIView):
    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        question = serializer.validated_data['question']
        
        try:
            # 1. Get AI generated query
            ai_response = ai_service.get_generated_query(question)
            
            if "error" in ai_response:
                return Response(
                    {"answer": f"Error generating query: {ai_response['error']}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            pandas_code = ai_response.get("pandas_code")
            answer_template = ai_response.get("answer_template", "{result}")
            chart_suggestion = ai_response.get("chart_suggestion", {})

            # 2. Execute Query
            # engine is imported singleton
            execution_result = engine.execute(pandas_code)

            if isinstance(execution_result, dict) and "error" in execution_result:
                return Response(
                    {"answer": f"Error executing query: {execution_result['error']}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # 3. Process Result & Format Response
            result_data = execution_result.get("data")
            result_type = execution_result.get("type")
            
            final_answer = answer_template
            chart_data = None
            
            # Simple answer formatting
            if result_type == "value":
                final_answer = final_answer.replace("{result}", str(result_data))
                
            elif result_type in ["dataframe", "series"]:
                # If it's a list of records (DataFrame) or dict (Series)
                # We can't easily put it in a string template without being messy.
                # Usually the template says "Here is the data: {result}"
                # For now, let's just JSON dump it if it's complex, or use the count.
                final_answer = final_answer.replace("{result}", "the data below") # Generic fallback
                
                # Chart Population
                if chart_suggestion and chart_suggestion.get("type"):
                    chart_data = {
                        "type": chart_suggestion["type"],
                        "title": chart_suggestion.get("title", "Analysis"),
                        "labels": [],
                        "values": []
                    }
                    
                    # Logic to extract labels/values based on data shape
                    if isinstance(result_data, list) and len(result_data) > 0:
                        # Assumption: DataFrame records. Need to identify X and Y?
                        # This is tricky without knowing columns.
                        # Naive approach: First column is label, second is value.
                        # Or use chart_suggestion x_axis / y_axis hints if AI provided them (it does in PROMPT)
                        
                        x_col = chart_suggestion.get("x_axis")
                        y_col = chart_suggestion.get("y_axis")
                        
                        if x_col and y_col:
                            # Try to extract
                            chart_data["labels"] = [str(row.get(x_col)) for row in result_data]
                            chart_data["values"] = [row.get(y_col) for row in result_data]
                        else:
                            # Fallback: keys/values of the first row ??? No, that's one record.
                            # Fallback: use first two keys of the first record
                            keys = list(result_data[0].keys())
                            if len(keys) >= 2:
                                chart_data["labels"] = [str(row.get(keys[0])) for row in result_data]
                                chart_data["values"] = [row.get(keys[1]) for row in result_data]
                    
                    elif isinstance(result_data, dict):
                        # Series converted to dict
                        chart_data["labels"] = list(result_data.keys())
                        chart_data["values"] = list(result_data.values())

            response_data = {
                "answer": final_answer,
                "query_executed": pandas_code,
                "chart_data": chart_data
            }
            
            return Response(response_data)

        except Exception as e:
            logger.error(f"ChatView Error: {e}", exc_info=True)
            return Response(
                {"answer": "An unexpected error occurred processing your request."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
