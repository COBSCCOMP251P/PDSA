import os  # Provides access to environment variables for DB configuration.
from sqlalchemy import create_engine  # Creates the SQLAlchemy engine.
from sqlalchemy.orm import sessionmaker, declarative_base  # Session factory and base class.

# Build the connection URL with a sensible default for local MySQL.
DATABASE_URL = os.getenv(
    "TSP_DATABASE_URL",
    "mysql+mysqlconnector://root:password@localhost:3306/tsp_game",  # Default local DSN.
)  # type: ignore[arg-type]

# Create the SQLAlchemy engine using the URL.
engine = create_engine(DATABASE_URL, pool_pre_ping=True)  # Keeps connections healthy.

# Configure session factory for dependency injection.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)  # Safe session defaults.

# Base class for model declarations.
Base = declarative_base()  # Base metadata container.


def get_db():
    """Yield a database session and ensure it is closed after use."""  # Explains dependency purpose.
    db = SessionLocal()  # Open session.
    try:
        yield db  # Provide session to request handler.
    finally:
        db.close()  # Always close to avoid leaks.


