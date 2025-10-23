import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def list_available_models():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found")
        return
    
    genai.configure(api_key=api_key)
    
    print("Available models:")
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"✅ {model.name}")

if __name__ == "__main__":
    list_available_models()