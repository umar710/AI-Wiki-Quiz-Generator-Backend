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

# CORS configuration - Allow both common frontend development ports
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",    # Create React App default
        "http://localhost:5173",    # Vite default
        "http://127.0.0.1:3000",    # Localhost alternative
        "http://127.0.0.1:5173",    # Localhost alternative
        "http://localhost:8080",    # Alternative port
        "http://127.0.0.1:8080",    # Alternative port
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
async def root():
    return {"message": "AI Wiki Quiz Generator API is running!"}

@app.post("/generate_quiz", response_model=QuizOutput)
async def generate_quiz(request: URLRequest, db: Session = Depends(get_db)):
    try:
        print(f"Received request to generate quiz for URL: {request.url}")
        
        # Scrape Wikipedia content
        scraped_data = scrape_wikipedia(request.url)
        print(f"Successfully scraped content. Title: {scraped_data['title']}")
        
        # Generate quiz using LLM
        quiz_data = quiz_generator.generate_quiz(
            scraped_data["title"], 
            scraped_data["content"]
        )
        print(f"Successfully generated quiz with {len(quiz_data.questions)} questions")
        
        # Save to database
        db_quiz = Quiz(
            url=request.url,
            title=scraped_data["title"],
            scraped_content=scraped_data["content"],
            full_quiz_data=json.dumps(quiz_data.dict())
        )
        db.add(db_quiz)
        db.commit()
        db.refresh(db_quiz)
        
        print(f"Quiz saved to database with ID: {db_quiz.id}")
        return quiz_data
        
    except ValueError as e:
        print(f"ValueError in generate_quiz: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Exception in generate_quiz: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/history", response_model=List[QuizHistoryItem])
async def get_quiz_history(db: Session = Depends(get_db)):
    try:
        quizzes = db.query(Quiz).order_by(Quiz.date_generated.desc()).all()
        print(f"Retrieved {len(quizzes)} quizzes from history")
        return quizzes
    except Exception as e:
        print(f"Error retrieving history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve quiz history")

@app.get("/quiz/{quiz_id}", response_model=QuizOutput)
async def get_quiz_by_id(quiz_id: int, db: Session = Depends(get_db)):
    try:
        quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")
        
        quiz_data = json.loads(quiz.full_quiz_data)
        print(f"Retrieved quiz ID {quiz_id} from database")
        return QuizOutput(**quiz_data)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid quiz data format")
    except Exception as e:
        print(f"Error retrieving quiz {quiz_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve quiz")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "AI Wiki Quiz Generator API is running correctly",
        "timestamp": "2024-01-01T00:00:00Z"  # You might want to use actual datetime
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
