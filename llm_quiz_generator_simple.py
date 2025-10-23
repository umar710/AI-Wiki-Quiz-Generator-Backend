import os
import google.generativeai as genai
import json
from dotenv import load_dotenv
from models import QuizOutput

load_dotenv()

class LLMQuizGenerator:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        
        # Use the available Gemini 2.0 models from your list
        model_names = [
            'models/gemini-2.0-flash',           # Fast and capable
            'models/gemini-2.0-flash-001',       # Specific version
            'models/gemini-2.0-flash-lite',      # Lite version
            'models/gemini-2.0-flash-lite-001',  # Lite specific version
            'models/gemini-2.0-pro-exp',         # Pro experimental
            'models/gemini-flash-latest',        # Latest flash
            'models/gemini-pro-latest',          # Latest pro
        ]
        
        self.model = None
        working_model = None
        
        for model_name in model_names:
            try:
                print(f"🔄 Trying to initialize model: {model_name}")
                self.model = genai.GenerativeModel(model_name)
                # Test with a simple prompt
                test_response = self.model.generate_content("Say 'Hello' in one word.")
                if test_response.text:
                    working_model = model_name
                    print(f"✅ Successfully initialized working model: {model_name}")
                    break
            except Exception as e:
                print(f"❌ Failed to initialize {model_name}: {e}")
                continue
        
        if not working_model:
            raise ValueError("No working Gemini model found from available options.")
    
    def generate_quiz(self, title: str, content: str) -> QuizOutput:
        try:
            # Optimized prompt for Gemini 2.0
            prompt = f"""
            Create an educational quiz based on this Wikipedia article. Return ONLY valid JSON.

            ARTICLE TITLE: {title}
            
            ARTICLE CONTENT: {content[:5000]}
            
            Generate a quiz with this exact JSON structure:
            {{
                "title": "string (the article title)",
                "summary": "string (2-3 paragraph concise summary of the article)",
                "key_entities": [
                    {{
                        "name": "string (important person, concept, or thing)",
                        "description": "string (brief description)",
                        "relevance": "string (why this is important to the topic)"
                    }}
                ],
                "related_topics": ["string", "string", "string"],
                "questions": [
                    {{
                        "question": "string (multiple choice question)",
                        "options": ["option A", "option B", "option C", "option D"],
                        "correct_answer": "string (the correct option)",
                        "explanation": "string (educational explanation)"
                    }}
                ]
            }}
            
            Requirements:
            - Create 5-7 multiple choice questions
            - Include 3-4 key entities  
            - Include 3-4 related topics
            - Questions should test understanding, not just recall
            - Make explanations educational and clear
            - Return ONLY the JSON object, no other text or markdown
            """
            
            print("🔄 Sending request to Gemini API...")
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            print("✅ Received response from Gemini API")
            
            # Clean the response
            response_text = response_text.replace('```json', '').replace('```', '').strip()
            
            print(f"Response preview: {response_text[:200]}...")
            
            # Parse JSON response
            quiz_dict = json.loads(response_text)
            
            # Validate required structure
            required_fields = ['title', 'summary', 'key_entities', 'related_topics', 'questions']
            for field in required_fields:
                if field not in quiz_dict:
                    raise ValueError(f"Missing required field: {field}")
            
            print(f"✅ Successfully generated quiz with {len(quiz_dict['questions'])} questions")
            return QuizOutput(**quiz_dict)
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {e}")
            print(f"Raw response: {response_text}")
            raise Exception(f"Failed to parse AI response as JSON: {str(e)}")
        except Exception as e:
            print(f"❌ Quiz generation error: {e}")
            raise Exception(f"Failed to generate quiz: {str(e)}")

quiz_generator = LLMQuizGenerator()