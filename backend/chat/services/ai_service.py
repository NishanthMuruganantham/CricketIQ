# backend/chat/services/ai_service.py

"""
MongoDB-based AI query generation service.
Generates MongoDB aggregation pipelines instead of Pandas code.
"""

import google.generativeai as genai
from decouple import config
import json
import re
import logging
from .function_calling_service import CricketFunctionCaller

# Configure Gemini
genai.configure(api_key=config("GEMINI_API_KEY"))

logger = logging.getLogger(__name__)

# Model priority list - favoring models with strong tool use
MODELS = ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash-001", "gemini-flash-latest", "gemini-pro-latest"]

def get_system_prompt(metrics_list, filters_list):
    return f"""
    You are a cricket statistics expert assistant.
    
    When user asks a cricket question, use the `calculate_cricket_metric` function.
    
    IMPORTANT: You don't generate MongoDB queries. Instead:
    1. Identify the cricket metric they're asking for.
    2. Identify applicable filters from the user's question.
    3. Call `calculate_cricket_metric` with these parameters.
    
    AVAILABLE METRICS:
    {json.dumps(metrics_list, indent=2)}
    
    AVAILABLE FILTERS:
    {json.dumps(filters_list, indent=2)}
    
    RULES:
    1. Always use function calling - NEVER generate MongoDB queries manually.
    2. Select metric from provided enum.
    3. Select filters from provided enum.
    4. Use 'batter' or 'bowler' arguments for specific player names.
    5. If the user refers to a player by pronoun (he/him/she/her), use the player's name from context.
    6. If metric/filter not available, politely explain what IS available.
    """

def extract_recent_player(conversation_history: list) -> str:
    """Extract most recent player from conversation history."""
    if not conversation_history:
        return None
    
    for msg in reversed(conversation_history):
        if msg.get("role") == "assistant":
            text = msg.get("text", "")
            # Match player names: "Name with X" or "Name scored/took"
            match = re.search(r'([A-Z]\w*(?:\s+[A-Z]\w*){0,2})\s+(?:with|scored|took|plays)', text)
            if match:
                return match.group(1)
    return None

def get_generated_query(question: str, conversation_history: list = None) -> dict:
    """
    Generate response using Gemini Function Calling.
    """
    try:
        # 1. Initialize Function Caller
        function_caller = CricketFunctionCaller()
        tools_def = function_caller.get_tools_definition()
        tools = tools_def.get("function_declarations", []) # Gemini expecting list of functions
        
        # 2. Build Context
        context_parts = []
        if conversation_history:
            # Add last 4 messages for context
            context_msgs = conversation_history[-4:]
            for msg in context_msgs:
                role = "User" if msg.get("role") == "user" else "Assistant"
                context_parts.append(f"{role}: {msg.get('text', '')}")
            
            # Inject recent player context
            recent_player = extract_recent_player(conversation_history)
            if recent_player:
                pronouns = ['he', 'she', 'him', 'her', 'his', 'they', 'their']
                if any(p in question.lower() for p in pronouns):
                    context_parts.append(f"\n⚠️ Recent player: {recent_player}")
        
        context_str = "\n".join(context_parts) if context_parts else ""
        
        # 3. Build System Prompt
        metrics_keys = list(function_caller.metrics.keys())
        filters_keys = list(function_caller.filters.keys())
        system_prompt = get_system_prompt(metrics_keys, filters_keys)
        
        full_prompt = f"{system_prompt}\n{context_str}\n\nQuestion: {question}"
        
        # 4. Call Model
        selected_model = None
        last_error = None
        
        for model_name in MODELS:
            try:
                logger.info(f"Trying model: {model_name}")
                model = genai.GenerativeModel(model_name, tools=[function_caller.get_tools_definition()])
                
                # We use content generation with tools
                response = model.generate_content(full_prompt)
                
                # Check for tool calls
                if response.parts:
                    for part in response.parts:
                         if part.function_call:
                             selected_model = model_name
                             fc = part.function_call
                             if fc.name == "calculate_cricket_metric":
                                 # Execute safe query
                                 args = dict(fc.args)
                                 logger.info(f"Model chose tool: {fc.name} with args {args}")
                                 
                                 execution_result = function_caller.execute_function_call(**args)
                                 
                                 if execution_result.get("status") == "error":
                                     return {"error": execution_result.get("message")}
                                 
                                 # Return in format expected by views.py (or adapted)
                                 # We send the pre-executed result
                                 return {
                                     "executed_result": execution_result,
                                     "answer_template": f"Stats for {{result}}", # Generic, views.py handles formatting
                                     "collection": "deliverywise", # Placeholder
                                     "pipeline": execution_result.get("pipeline", [])
                                 }
                
                # If no tool call, maybe it answered directly (e.g. "I can't help")
                if response.text:
                     return {
                         "error": response.text # Treat direct text as "error" or handled message? 
                                                # For now, if it didn't call tool, it failed to query.
                     }
                    
            except Exception as e:
                logger.error(f"Model {model_name} failed: {e}")
                last_error = e
                continue
                
        return {"error": f"Unable to process query. Last error: {last_error}"}

    except Exception as e:
        logger.error(f"AI Service Critical Error: {e}")
        return {"error": f"System Error: {str(e)}"}