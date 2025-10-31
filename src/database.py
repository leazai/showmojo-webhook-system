"""
Database configuration and connection management for ShowMojo Webhook System
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, ForeignKey, TIMESTAMP, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/showmojo_db")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=10, max_overflow=20)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


class Event(Base):
    """Model for webhook events"""
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String(255), unique=True, nullable=False, index=True)
    action = Column(String(100), nullable=False, index=True)
    actor = Column(String(100))
    team_member_name = Column(String(255))
    team_member_uid = Column(String(100))
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, index=True)
    received_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    raw_payload = Column(JSON, nullable=False)

    # Relationship
    showings = relationship("Showing", back_populates="event", cascade="all, delete-orphan")


class Showing(Base):
    """Model for showings"""
    __tablename__ = "showings"

    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String(100), unique=True, nullable=False, index=True)
    event_id = Column(String(255), ForeignKey("events.event_id", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), index=True)
    showtime = Column(TIMESTAMP(timezone=True), index=True)
    showing_time_zone = Column(String(100))
    showing_time_zone_utc_offset = Column(Integer)
    name = Column(String(255))
    phone = Column(String(50))
    email = Column(String(255), index=True)
    notes = Column(Text)
    listing_uid = Column(String(100), index=True)
    listing_full_address = Column(Text)
    is_self_show = Column(Boolean)
    confirmed_at = Column(TIMESTAMP(timezone=True))
    canceled_at = Column(TIMESTAMP(timezone=True))
    self_show_code_distributed_at = Column(TIMESTAMP(timezone=True))
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    event = relationship("Event", back_populates="showings")


class Listing(Base):
    """Model for listings"""
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String(100), unique=True, nullable=False, index=True)
    full_address = Column(Text, nullable=False, index=True)
    first_seen_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    last_seen_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    total_showings = Column(Integer, default=0)


class Prospect(Base):
    """Model for prospects"""
    __tablename__ = "prospects"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255))
    phone = Column(String(50), index=True)
    first_contact_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    last_contact_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    total_showings = Column(Integer, default=0)


def get_db():
    """
    Dependency function to get database session
    Yields a database session and ensures it's closed after use
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables
    Creates all tables defined in the models
    """
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


if __name__ == "__main__":
    # Create tables when run directly
    init_db()
