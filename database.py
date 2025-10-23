import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Database configuration for Render PostgreSQL
def get_database_url():
    # Use Render's DATABASE_URL environment variable
    database_url = os.getenv("DATABASE_URL")
    
    if database_url:
        # Ensure it uses postgresql:// format for SQLAlchemy
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        return database_url
    else:
        # Fallback to SQLite for local development
        return "sqlite:///./quiz_history.db"

DATABASE_URL = get_database_url()

print(f"Database URL: {DATABASE_URL.split('@')[0]}@***")  # Log without password

# Create engine with PostgreSQL optimizations
if DATABASE_URL.startswith("postgresql://"):
    engine = create_engine(
        DATABASE_URL,
        pool_size=5,           # Number of permanent connections
        max_overflow=10,       # Number of connections beyond pool_size
        pool_pre_ping=True,    # Verify connection before use
        pool_recycle=300,      # Recycle connections after 5 minutes
        echo=False            # Set to True for debugging SQL queries
    )
    print("✅ Using PostgreSQL database")
else:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    print("✅ Using SQLite database (development)")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Quiz(Base):
    __tablename__ = "quizzes"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, index=True)
    title = Column(String)
    date_generated = Column(DateTime, default=datetime.utcnow)
    scraped_content = Column(Text)
    full_quiz_data = Column(Text)

# Create tables
try:
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")
except Exception as e:
    print(f"❌ Error creating database tables: {e}")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()