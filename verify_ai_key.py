import os
import google.generativeai as genai
from decouple import config

def verify_key():
    # Try to get from environment first
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        # Try from decouple (checks .env)
        try:
            api_key = config('GEMINI_API_KEY')
        except:
            api_key = None
            
    if not api_key:
        print("ERROR: No GEMINI_API_KEY found in environment or .env file.")
        return

    print(f"Key found (length: {len(api_key)})")
    
    try:
        genai.configure(api_key=api_key.split(',')[0].strip())
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Say 'Key is working'")
        print(f"SUCCESS: {response.text.strip()}")
    except Exception as e:
        print(f"FAILURE: {str(e)}")

if __name__ == "__main__":
    verify_key()
