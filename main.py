from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import json
from typing import List

from database import get_db, Quiz
from models import URLRequest, QuizHistoryItem, QuizOutput
from scraper import scrape_wikipedia
from llm_quiz_generator_simple import quiz_generator

app = FastAPI(title="AI Wiki Quiz Generator", version="1.0.0")

# CORS configuration for production with your exact Vercel URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "https://ai-wiki-quiz-generator-frontend.vercel.app",  # Your exact domain
        "https://*.vercel.app",  # All Vercel subdomains
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"],  # Specific headers
)

# Your existing routes continue below...
@app.get("/")
async def root():
    return {"message": "AI Wiki Quiz Generator API is running!"}

@app.post("/generate_quiz", response_model=QuizOutput)
async def generate_quiz(request: URLRequest, db: Session = Depends(get_db)):
    try:
        scraped_data = scrape_wikipedia(request.url)
        quiz_data = quiz_generator.generate_quiz(
            scraped_data["title"], 
            scraped_data["content"]
        )
        
        db_quiz = Quiz(
            url=request.url,
            title=scraped_data["title"],
            scraped_content=scraped_data["content"],
            full_quiz_data=json.dumps(quiz_data.dict())
        )
        db.add(db_quiz)
        db.commit()
        db.refresh(db_quiz)
        
        return quiz_data
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/history", response_model=List[QuizHistoryItem])
async def get_quiz_history(db: Session = Depends(get_db)):
    quizzes = db.query(Quiz).order_by(Quiz.date_generated.desc()).all()
    return quizzes

@app.get("/quiz/{quiz_id}", response_model=QuizOutput)
async def get_quiz_by_id(quiz_id: int, db: Session = Depends(get_db)):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    try:
        quiz_data = json.loads(quiz.full_quiz_data)
        return QuizOutput(**quiz_data)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid quiz data format")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)