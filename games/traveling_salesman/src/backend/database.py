import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ==========================================
# Database Connection Configuration
# ==========================================
DATABASE_URL = os.getenv(
    "TSP_DATABASE_URL",
    "mysql+mysqlconnector://tspuser:StrongPass123!@localhost/tsp_game"
)

# ==========================================
# SQLAlchemy Engine
# ==========================================
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# ==========================================
# Session Factory
# ==========================================
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ==========================================
# Base Model Class
# ==========================================
Base = declarative_base()

# ==========================================
# Dependency Injection
# ==========================================
def get_db():
    """
    Creates a new database session for a request and closes it when done.
    
    This function is used as a FastAPI usage dependency.

    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
