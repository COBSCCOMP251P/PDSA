from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, Float, func
from sqlalchemy.orm import relationship
from .database import Base

class GameRound(Base):
    """ORM model for completed game rounds."""

    __tablename__ = "game_rounds"

    id = Column(Integer, primary_key=True, index=True)
    player_name = Column(String(50), nullable=False)
    home_city = Column(String(1), nullable=False)
    selected_cities = Column(Text, nullable=False)
    brute_force_distance = Column(Float, nullable=False)
    nearest_neighbor_distance = Column(Float, nullable=False)
    dp_distance = Column(Float, nullable=False)
    player_distance = Column(Float, nullable=False)
    player_score = Column(Integer, nullable=False)
    timestamp = Column(DateTime, server_default=func.now())

    # Relationship to time measurements.
    algorithm_times = relationship(
        "AlgorithmTime", back_populates="game_round", cascade="all, delete-orphan"
    )

class AlgorithmTime(Base):
    """ORM model for algorithm runtime measurements."""

    __tablename__ = "algorithm_times"

    id = Column(Integer, primary_key=True, index=True)
    round_id = Column(Integer, ForeignKey("game_rounds.id", ondelete="CASCADE"), nullable=False)
    brute_force_time = Column(Float, nullable=False)
    nearest_neighbor_time = Column(Float, nullable=False)
    dp_time = Column(Float, nullable=False)

    # Back-reference to game round.
    game_round = relationship("GameRound", back_populates="algorithm_times")
