import sys
import os
import django
from django.conf import settings

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from chat.services.ai_service import get_generated_query
import google.generativeai as genai
from decouple import config

genai.configure(api_key=config("GEMINI_API_KEY"))

def list_available_models():
    print("\n--- Available Models ---")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(m.name)
    except Exception as e:
        print(f"Error listing models: {e}")

def test_query(question):
    print(f"\n--- Testing Question: {question} ---")
    result = get_generated_query(question)
    
    if "error" in result:
        print(f"ERROR: {result['error']}")
    else:
        print("SUCCESS!")
        print(f"Template: {result.get('answer_template')}")
        print("Executed Result Data (First 2 items if list):")
        exec_res = result.get('executed_result', {})
        data = exec_res.get('data')
        if isinstance(data, list):
            print(data[:2])
        else:
            print(data)
            
        print("Pipeline:")
        print(result.get('pipeline'))

if __name__ == "__main__":
    list_available_models()
    
    questions = [
        "Who has the highest batting average in 2023?",
        "What is Virat Kohli's strike rate against Pakistan?",
        "How many runs did Suryakumar Yadav score in the death overs?",
        "Best bowling average for spinners in 2024?"
    ]
    
    for q in questions:
        test_query(q)
