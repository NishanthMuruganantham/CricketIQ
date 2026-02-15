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
            
            # Helper function for template rendering
            import re
            def render_template(template_str, data):
                def replace_match(match):
                    expression = match.group(1).strip()
                    if not expression.startswith('result'):
                        return match.group(0)
                    
                    # Remove 'result'
                    token_str = expression[6:]
                    if not token_str: # just {{result}}
                         return str(data)

                    # Parse .key or [index]
                    tokens = re.findall(r'\.([\w_]+)|\[(\d+)\]', token_str)
                    
                    current_obj = data
                    try:
                        for key, index in tokens:
                            if index:
                                current_obj = current_obj[int(index)]
                            elif key:
                                if isinstance(current_obj, dict):
                                    current_obj = current_obj.get(key, "N/A")
                                else:
                                    # Fallback if accessing attribute of non-dict
                                    return "N/A"
                        return str(current_obj)
                    except (IndexError, KeyError, TypeError, AttributeError):
                        return "N/A"

                return re.sub(r'\{\{(.*?)\}\}', replace_match, template_str)

            # Apply robust templating first (handles {{result[0].name}} etc.)
            if result_data is not None:
                final_answer = render_template(final_answer, result_data)

            # Fallback formatting for {result} placeholder (backward compatibility)
            if "{result}" in final_answer:
                result_str = "No data found"
                
                if result_type == "dict" and result_data:
                    # Single document
                    if "_id" in result_data:
                        name = result_data["_id"]
                        val = next((v for k, v in result_data.items() if k != "_id" and isinstance(v, (int, float))), None)
                        result_str = f"{name} with {val:,}" if val is not None else str(name)
                    else:
                        parts = [f"{k}: {v:,}" if isinstance(v, (int, float)) else f"{k}: {v}" for k, v in result_data.items()]
                        result_str = ", ".join(parts)
                
                elif result_type == "list" and result_data:
                    # List of documents
                    formatted = []
                    for doc in result_data:
                        if isinstance(doc, dict) and "_id" in doc:
                            name = doc["_id"]
                            val = next((v for k, v in doc.items() if k != "_id" and isinstance(v, (int, float))), None)
                            formatted.append(f"{name} ({val:,})" if val is not None else str(name))
                        else:
                            formatted.append(str(doc))
                    result_str = ", ".join(formatted)
                
                elif result_type == "empty":
                    result_str = "No data found"

                final_answer = final_answer.replace("{result}", result_str)

            
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
