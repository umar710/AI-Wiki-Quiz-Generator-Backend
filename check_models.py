import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def list_available_models():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in .env file")
        return
    
    genai.configure(api_key=api_key)
    
    print("🔍 Checking available models...")
    available_models = []
    
    try:
        for model in genai.list_models():
            if 'generateContent' in model.supported_generation_methods:
                available_models.append(model.name)
                print(f"✅ {model.name}")
        
        if not available_models:
            print("❌ No models with generateContent support found")
        else:
            print(f"\n🎯 Available models: {available_models}")
            
    except Exception as e:
        print(f"❌ Error listing models: {e}")

if __name__ == "__main__":
    list_available_models()