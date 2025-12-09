from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

SQLALCHEMY_DATABASE_URL = "sqlite:///./tivrag.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class GoogleCredentials(Base):
    __tablename__ = "google_credentials"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    access_token = Column(String)
    refresh_token = Column(String)
    token_expiry = Column(DateTime)
    scopes = Column(String)  # JSON string of scopes
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    name = Column(String)
    search_email = Column(String)
    include_gmail = Column(Boolean, default=True)
    include_drive = Column(Boolean, default=True)
    date_from = Column(DateTime)
    date_to = Column(DateTime)
    search_results = Column(Text)  # JSON string of cached results
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Thread(Base):
    __tablename__ = "threads"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, index=True)
    user_id = Column(Integer, index=True)
    title = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(Integer, index=True)
    project_id = Column(Integer, index=True)
    user_id = Column(Integer, index=True)
    role = Column(String)  # 'user' or 'assistant'
    content = Column(Text)
    parse_emails = Column(Boolean, default=False)
    parse_documents = Column(Boolean, default=False)
    parsed_count = Column(String)  # JSON string of parsed counts
    created_at = Column(DateTime, default=datetime.utcnow)

# CRM Models
class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    name = Column(String, index=True)
    email = Column(String, index=True)
    phone = Column(String)
    company = Column(String)
    status = Column(String, default="lead")  # lead, prospect, customer, inactive
    tags = Column(String)  # JSON string of tags
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Deal(Base):
    __tablename__ = "deals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    contact_id = Column(Integer, ForeignKey('contacts.id'), index=True)
    title = Column(String)
    value = Column(Float, default=0.0)
    stage = Column(String, default="lead")  # lead, qualified, proposal, negotiation, closed_won, closed_lost
    probability = Column(Integer, default=0)  # 0-100
    expected_close_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    assigned_to_contact_id = Column(Integer, ForeignKey('contacts.id'), index=True)
    title = Column(String)
    description = Column(Text)
    due_date = Column(DateTime)
    priority = Column(String, default="medium")  # low, medium, high
    status = Column(String, default="pending")  # pending, in_progress, completed, cancelled
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    related_to_contact_id = Column(Integer, ForeignKey('contacts.id'), index=True)
    related_to_deal_id = Column(Integer, ForeignKey('deals.id'), index=True)
    content = Column(Text)
    note_type = Column(String, default="general")  # general, call, meeting, email, task
    created_at = Column(DateTime, default=datetime.utcnow)

class EmailLog(Base):
    __tablename__ = "email_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    sent_to_contact_id = Column(Integer, ForeignKey('contacts.id'), index=True)
    subject = Column(String)
    body = Column(Text)
    sent_at = Column(DateTime, default=datetime.utcnow)
    gmail_thread_id = Column(String)  # Gmail thread ID for tracking

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

