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
        self.model = genai.GenerativeModel('gemini-pro')
    
    def generate_quiz(self, title: str, content: str) -> QuizOutput:
        try:
            prompt = f"""
            Create an educational quiz based on this Wikipedia article in strict JSON format:
            
            Title: {title}
            
            Content: {content[:8000]}
            
            Generate the following structure:
            {{
                "title": "Article Title",
                "summary": "2-3 paragraph summary",
                "key_entities": [
                    {{
                        "name": "Entity name",
                        "description": "Brief description",
                        "relevance": "Why important"
                    }}
                ],
                "related_topics": ["topic1", "topic2", "topic3"],
                "questions": [
                    {{
                        "question": "Quiz question",
                        "options": ["option1", "option2", "option3", "option4"],
                        "correct_answer": "correct option",
                        "explanation": "Why this is correct"
                    }}
                ]
            }}
            
            Requirements:
            - Generate 5-8 questions
            - 3-5 key entities
            - 3-5 related topics
            - Questions should test genuine understanding
            - Return ONLY valid JSON, no other text
            """
            
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean the response (remove markdown code blocks if present)
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            # Parse JSON response
            quiz_dict = json.loads(response_text)
            return QuizOutput(**quiz_dict)
            
        except Exception as e:
            raise Exception(f"Failed to generate quiz: {str(e)}")

quiz_generator = LLMQuizGenerator()