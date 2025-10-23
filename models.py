from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

class Question(BaseModel):
    question: str = Field(description="The quiz question")
    options: List[str] = Field(description="List of 4 multiple choice options")
    correct_answer: str = Field(description="The correct answer")
    explanation: str = Field(description="Explanation of why this answer is correct")

class KeyEntity(BaseModel):
    name: str = Field(description="Name of the key entity")
    description: str = Field(description="Brief description of the entity")
    relevance: str = Field(description="Why this entity is important to the topic")

class QuizOutput(BaseModel):
    title: str = Field(description="Title of the Wikipedia article")
    summary: str = Field(description="Concise summary of the article")
    key_entities: List[KeyEntity] = Field(description="List of 3-5 key entities from the article")
    related_topics: List[str] = Field(description="List of 3-5 related topics")
    questions: List[Question] = Field(description="List of 5-10 quiz questions")

class URLRequest(BaseModel):
    url: str

class QuizHistoryItem(BaseModel):
    id: int
    url: str
    title: str
    date_generated: datetime

    class Config:
        from_attributes = True