from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ChatRequestSerializer
from .services import ai_service
from .services.mongo_query_engine import get_mongo_engine
import json
import logging

logger = logging.getLogger(__name__)

class ChatView(APIView):
    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        question = serializer.validated_data['question']
        conversation_history = serializer.validated_data.get('conversation_history', [])
        
        try:
            # 1. Get AI-generated MongoDB pipeline
            ai_response = ai_service.get_generated_query(question, conversation_history)
            
            if "error" in ai_response:
                # Return error as a chat message so the user sees the specific reason (e.g., rate limit)
                return Response(
                    {"answer": f"⚠️ {ai_response['error']}"},
                    status=status.HTTP_200_OK
                )

            pipeline = ai_response.get("pipeline")
            collection = ai_response.get("collection", "deliverywise")
            answer_template = ai_response.get("answer_template", "{result}")
            chart_suggestion = ai_response.get("chart_suggestion", {})

            # 2. Execute MongoDB pipeline
            mongo_engine = get_mongo_engine()
            execution_result = mongo_engine.execute(pipeline, collection)

            if "error" in execution_result:
                return Response(
                    {"answer": f"Error executing query: {execution_result['error']}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # 3. Process Result & Format Response
            result_data = execution_result.get("data")
            result_type = execution_result.get("type")
            
            final_answer = answer_template
            chart_data = None
            
            # Format answer based on result type
            if result_type == "dict":
                # Single document result
                if result_data:
                    # Handle {{key}} placeholders
                    for key, value in result_data.items():
                        # Replace {{key}}
                        placeholder = "{{" + key + "}}"
                        final_answer = final_answer.replace(placeholder, str(value))
                        # Replace {{result.key}}
                        placeholder_result = "{{result." + key + "}}"
                        final_answer = final_answer.replace(placeholder_result, str(value))
                    
                    # Handle {result} placeholder
                    if "_id" in result_data:
                        name = result_data["_id"]
                        numeric_val = None
                        for k, v in result_data.items():
                            if k != "_id" and isinstance(v, (int, float)):
                                numeric_val = v
                                break
                        
                        if numeric_val is not None:
                            result_str = f"{name} with {numeric_val:,}"
                        else:
                            result_str = str(name)
                        final_answer = final_answer.replace("{result}", result_str)
                    else:
                        # No _id field — use all key-value pairs
                        parts = []
                        for k, v in result_data.items():
                            if isinstance(v, (int, float)):
                                parts.append(f"{k}: {v:,}")
                            else:
                                parts.append(f"{k}: {v}")
                        result_str = ", ".join(parts) if parts else str(result_data)
                        final_answer = final_answer.replace("{result}", result_str)
            
            elif result_type == "list":
                # Multiple documents
                if result_data and len(result_data) == 1:
                    doc = result_data[0]
                    # Handle {{key}} and {{result.key}} placeholders
                    for key, value in doc.items():
                        # Replace {{key}}
                        placeholder = "{{" + key + "}}"
                        final_answer = final_answer.replace(placeholder, str(value))
                        # Replace {{result.key}}
                        placeholder_result = "{{result." + key + "}}"
                        final_answer = final_answer.replace(placeholder_result, str(value))
                        # Replace {{result.0.key}}
                        placeholder_result_idx = "{{result.0." + key + "}}"
                        final_answer = final_answer.replace(placeholder_result_idx, str(value))
                    
                    if "_id" in doc:
                        name = doc["_id"]
                        numeric_val = None
                        for k, v in doc.items():
                            if k != "_id" and isinstance(v, (int, float)):
                                numeric_val = v
                                break
                        if numeric_val is not None:
                            result_str = f"{name} with {numeric_val:,}"
                        else:
                            result_str = str(name)
                        final_answer = final_answer.replace("{result}", result_str)
                    else:
                        # No _id field — format nicely
                        parts = []
                        for k, v in doc.items():
                            if isinstance(v, (int, float)):
                                parts.append(f"{k}: {v:,}")
                            else:
                                parts.append(f"{k}: {v}")
                        
                        # If only one value, just show the value (cleaner for "country", "winner", etc.)
                        if len(parts) == 1:
                            result_str = str(list(doc.values())[0])
                        else:
                            result_str = ", ".join(parts)
                            
                        final_answer = final_answer.replace("{result}", result_str)
                elif result_data and len(result_data) > 1:
                    # Multiple items: format as list
                    formatted = []
                    for doc in result_data:
                        if "_id" in doc:
                            name = doc["_id"]
                            for k, v in doc.items():
                                if k != "_id" and isinstance(v, (int, float)):
                                    formatted.append(f"{name} ({v:,})")
                                    break
                            else:
                                formatted.append(str(name))
                        else:
                            formatted.append(str(doc))
                    result_str = ", ".join(formatted)
                    final_answer = final_answer.replace("{result}", result_str)
                else:
                    final_answer = final_answer.replace("{result}", "No data found")
            
            elif result_type == "empty":
                final_answer = final_answer.replace("{result}", "No data found")
            
            # Chart population
            if chart_suggestion and chart_suggestion.get("type"):
                if result_type == "list" and result_data and len(result_data) >= 3:
                    chart_data = {
                        "type": chart_suggestion["type"],
                        "title": chart_suggestion.get("title", "Analysis"),
                        "labels": [],
                        "values": []
                    }
                    
                    x_col = chart_suggestion.get("x_axis")
                    y_col = chart_suggestion.get("y_axis")
                    
                    for doc in result_data:
                        if x_col and x_col in doc:
                            chart_data["labels"].append(str(doc[x_col]))
                        elif "_id" in doc:
                            chart_data["labels"].append(str(doc["_id"]))
                        
                        if y_col and y_col in doc:
                            chart_data["values"].append(doc[y_col])
                        else:
                            for k, v in doc.items():
                                if k != "_id" and isinstance(v, (int, float)):
                                    chart_data["values"].append(v)
                                    break
                    
                    # Only include chart if there are 3+ data points
                    if len(chart_data.get("labels", [])) < 3:
                        chart_data = None
                
                elif result_type == "dict" and result_data:
                    # Single dict — not enough for a chart
                    chart_data = None

            response_data = {
                "answer": final_answer,
                "query_executed": json.dumps(pipeline, indent=2),
                "chart_data": chart_data
            }
            
            return Response(response_data)

        except Exception as e:
            logger.error(f"ChatView Error: {e}", exc_info=True)
            return Response(
                {"answer": "An unexpected error occurred processing your request."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
