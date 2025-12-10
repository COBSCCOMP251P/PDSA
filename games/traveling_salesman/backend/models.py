from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, Float, func  # Core column types.
from sqlalchemy.orm import relationship  # Relationship helper.
from .database import Base  # Shared metadata base.


class GameRound(Base):
    """ORM model for completed game rounds."""  # Brief model description.

    __tablename__ = "game_rounds"  # Matches required schema.

    id = Column(Integer, primary_key=True, index=True)  # Surrogate key.
    player_name = Column(String(50), nullable=False)  # Player identifier.
    home_city = Column(String(1), nullable=False)  # Randomly chosen home city.
    selected_cities = Column(Text, nullable=False)  # Stored as comma-separated list.
    brute_force_distance = Column(Float, nullable=False)  # Exact best distance.
    nearest_neighbor_distance = Column(Float, nullable=False)  # Heuristic distance.
    dp_distance = Column(Float, nullable=False)  # DP optimal distance.
    player_distance = Column(Float, nullable=False)  # Player-entered route distance.
    player_score = Column(Integer, nullable=False)  # Computed score out of 100.
    timestamp = Column(DateTime, server_default=func.now())  # Auto timestamp.

    # Relationship to time measurements.
    algorithm_times = relationship(
        "AlgorithmTime", back_populates="game_round", cascade="all, delete-orphan"
    )  # Keeps timing rows in sync.


class AlgorithmTime(Base):
    """ORM model for algorithm runtime measurements."""  # Brief model description.

    __tablename__ = "algorithm_times"  # Matches required schema.

    id = Column(Integer, primary_key=True, index=True)  # Surrogate key.
    round_id = Column(Integer, ForeignKey("game_rounds.id", ondelete="CASCADE"), nullable=False)  # FK to round.
    brute_force_time = Column(Float, nullable=False)  # Time in seconds.
    nearest_neighbor_time = Column(Float, nullable=False)  # Time in seconds.
    dp_time = Column(Float, nullable=False)  # Time in seconds.

    # Back-reference to game round.
    game_round = relationship("GameRound", back_populates="algorithm_times")  # Enables ORM navigation.


