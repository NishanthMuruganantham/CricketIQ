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
        conversation_history = serializer.validated_data.get('conversation_history', [])
        
        try:
            # 1. Get AI generated query (with conversation context)
            ai_response = ai_service.get_generated_query(question, conversation_history)
            
            if "error" in ai_response:
                return Response(
                    {"answer": f"Error generating query: {ai_response['error']}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            pandas_code = ai_response.get("pandas_code")
            answer_template = ai_response.get("answer_template", "{result}")
            chart_suggestion = ai_response.get("chart_suggestion", {})

            # 2. Execute Query
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
            
            # Answer formatting with support for dictionary-style placeholders
            if result_type == "value":
                # Simple value: replace {result}
                final_answer = final_answer.replace("{result}", str(result_data))
                
            elif result_type in ["dataframe", "series"]:
                # Handle dictionary-style placeholders like {result[key]}, {result['key']}, or {result.key}
                if isinstance(result_data, dict):
                    import re
                    
                    def get_value(data, key):
                        """Try to get value with string key first, then try integer key."""
                        if key in data:
                            return str(data[key])
                        # Try converting to int for numeric keys
                        try:
                            int_key = int(key)
                            if int_key in data:
                                return str(data[int_key])
                        except (ValueError, TypeError):
                            pass
                        return f"[missing: {key}]"
                    
                    # Pattern 1: {result[key]}, {result['key']}, {result["key"]}
                    bracket_pattern = r"\{result\[(?:['\"])?([^\]'\"]+)(?:['\"])?\]\}"
                    def replace_bracket_key(match):
                        return get_value(result_data, match.group(1))
                    final_answer = re.sub(bracket_pattern, replace_bracket_key, final_answer)
                    
                    # Pattern 2: {result.key} - dot notation (simple keys only)
                    dot_pattern = r"\{result\.(\w+)\}"
                    def replace_dot_key(match):
                        return get_value(result_data, match.group(1))
                    final_answer = re.sub(dot_pattern, replace_dot_key, final_answer)
                    
                    # Pattern 3: {result.index[N]} - pandas index accessor
                    index_pattern = r"\{result\.index\[(\d+)\]\}"
                    def replace_index(match):
                        idx = int(match.group(1))
                        keys = list(result_data.keys())
                        if idx < len(keys):
                            return str(keys[idx])
                        return f"[missing index: {idx}]"
                    final_answer = re.sub(index_pattern, replace_index, final_answer)
                    
                    # Pattern 4: {result.iloc[N]} - pandas positional accessor
                    iloc_pattern = r"\{result\.iloc\[(\d+)\]\}"
                    def replace_iloc(match):
                        idx = int(match.group(1))
                        values = list(result_data.values())
                        if idx < len(values):
                            return str(values[idx])
                        return f"[missing iloc: {idx}]"
                    final_answer = re.sub(iloc_pattern, replace_iloc, final_answer)
                    
                    # Pattern 5: {result.values[N]} - pandas values accessor
                    values_pattern = r"\{result\.values\[(\d+)\]\}"
                    def replace_values(match):
                        idx = int(match.group(1))
                        values = list(result_data.values())
                        if idx < len(values):
                            return str(values[idx])
                        return f"[missing values: {idx}]"
                    final_answer = re.sub(values_pattern, replace_values, final_answer)
                    
                    # Also replace plain {result} if present
                    # Format single-item Series results as "Key with Value"
                    if len(result_data) == 1:
                        key, value = list(result_data.items())[0]
                        if isinstance(value, (int, float)):
                            result_str = f"{key} with {value:,}"
                        else:
                            result_str = f"{key} - {value}"
                    else:
                        # Multiple results: format as comma-separated list
                        result_str = ", ".join([f"{k} ({v:,})" if isinstance(v, (int, float)) else f"{k} ({v})" for k, v in result_data.items()])
                    final_answer = final_answer.replace("{result}", result_str)
                    
                elif isinstance(result_data, list) and len(result_data) == 1:
                    # Single record: handle {result[key]}, {result['key']}, or {result.key}
                    import re
                    record = result_data[0]
                    
                    def get_value(data, key):
                        """Try to get value with string key first, then try integer key."""
                        if key in data:
                            return str(data[key])
                        try:
                            int_key = int(key)
                            if int_key in data:
                                return str(data[int_key])
                        except (ValueError, TypeError):
                            pass
                        return f"[missing: {key}]"
                    
                    bracket_pattern = r"\{result\[(?:['\"])?([^\]'\"]+)(?:['\"])?\]\}"
                    def replace_bracket_key(match):
                        return get_value(record, match.group(1))
                    final_answer = re.sub(bracket_pattern, replace_bracket_key, final_answer)
                    
                    dot_pattern = r"\{result\.(\w+)\}"
                    def replace_dot_key(match):
                        return get_value(record, match.group(1))
                    final_answer = re.sub(dot_pattern, replace_dot_key, final_answer)
                    
                    # Pattern 3: {result.index[N]} - pandas index accessor
                    index_pattern = r"\{result\.index\[(\d+)\]\}"
                    def replace_index(match):
                        idx = int(match.group(1))
                        keys = list(record.keys())
                        if idx < len(keys):
                            return str(keys[idx])
                        return f"[missing index: {idx}]"
                    final_answer = re.sub(index_pattern, replace_index, final_answer)
                    
                    # Pattern 4: {result.iloc[N]} - pandas positional accessor
                    iloc_pattern = r"\{result\.iloc\[(\d+)\]\}"
                    def replace_iloc(match):
                        idx = int(match.group(1))
                        values = list(record.values())
                        if idx < len(values):
                            return str(values[idx])
                        return f"[missing iloc: {idx}]"
                    final_answer = re.sub(iloc_pattern, replace_iloc, final_answer)
                    
                    # Pattern 5: {result.values[N]} - pandas values accessor
                    values_pattern = r"\{result\.values\[(\d+)\]\}"
                    def replace_values(match):
                        idx = int(match.group(1))
                        values = list(record.values())
                        if idx < len(values):
                            return str(values[idx])
                        return f"[missing values: {idx}]"
                    final_answer = re.sub(values_pattern, replace_values, final_answer)
                    
                    final_answer = final_answer.replace("{result}", str(record))
                    
                else:
                    # Fallback for lists/complex data
                    final_answer = final_answer.replace("{result}", "the data below")
                
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
                    
                    # Only include chart if there are 3+ data points
                    if len(chart_data.get("labels", [])) < 3:
                        chart_data = None

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
