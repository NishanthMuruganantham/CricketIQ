import os
import sys
import django
from decouple import config

# Apply Django setup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from chat.services.ai_service import get_generated_query

def test_query(question):
    print(f"\n--- Testing Question: {question} ---")
    try:
        result = get_generated_query(question)
        if "error" in result:
            print(f"ERROR: {result['error']}")
        else:
            print("SUCCESS!")
            print(f"Template: {result['answer_template']}")
            print(f"Executed Result Data (First 2 items if list):")
            data = result.get('executed_result', {}).get('data')
            if isinstance(data, list):
                print(data[:2])
            else:
                print(data)
            print("Pipeline:")
            print(result.get('pipeline'))
            
    except Exception as e:
        print(f"EXCEPTION: {e}")

if __name__ == "__main__":
    # Test specific question requiring dynamic batter filter
    test_query("How many runs did Suryakumar Yadav score in the death overs?")
