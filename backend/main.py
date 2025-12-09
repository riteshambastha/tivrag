from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict
import bcrypt
import jwt
from datetime import datetime, timedelta
import json

from database import get_db, init_db, User, GoogleCredentials, Project, ChatMessage, Thread, Contact, Deal, Task, Note, EmailLog
from google_services import GoogleServicesManager
from document_parser import DocumentParser
from ai_analyzer import AIAnalyzer

app = FastAPI(title="Tivrag API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5175", "http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"

# Pydantic models
class SignupRequest(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    username: str

class GoogleAuthRequest(BaseModel):
    authorization_code: str

class SearchRequest(BaseModel):
    query: str
    person: str

class ProjectCreateRequest(BaseModel):
    name: str
    search_email: str
    include_gmail: bool = True
    include_drive: bool = True
    date_from: Optional[str] = None
    date_to: Optional[str] = None

class ProjectResponse(BaseModel):
    id: int
    name: str
    search_email: str
    include_gmail: bool
    include_drive: bool
    date_from: Optional[str]
    date_to: Optional[str]
    created_at: str
    updated_at: str

class EmailResult(BaseModel):
    id: str
    subject: str
    from_: str
    date: str
    snippet: str

class DocumentResult(BaseModel):
    id: str
    name: str
    type: str
    mime_type: Optional[str] = None
    modified_time: str
    web_view_link: str

class SearchResponse(BaseModel):
    emails: List[EmailResult]
    documents: List[DocumentResult]

class AnalyzeRequest(BaseModel):
    prompt: str
    project_id: int
    thread_id: Optional[int] = None
    parse_documents: bool = False
    parse_emails: bool = False

class ThreadCreateRequest(BaseModel):
    project_id: int
    title: str

class ThreadResponse(BaseModel):
    id: int
    project_id: int
    title: str
    message_count: int
    created_at: str
    updated_at: str

class ChatMessageResponse(BaseModel):
    id: int
    thread_id: int
    role: str
    content: str
    parse_emails: bool
    parse_documents: bool
    parsed_count: Optional[Dict[str, int]]
    created_at: str

class AnalyzeResponse(BaseModel):
    analysis: str
    parsed_count: Dict[str, int]
    message_id: int
    thread_id: int

# CRM Pydantic Models
class ContactCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    status: str = "lead"
    tags: Optional[str] = None
    notes: Optional[str] = None

class ContactUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[str] = None
    notes: Optional[str] = None

class ContactResponse(BaseModel):
    id: int
    user_id: int
    name: str
    email: Optional[str]
    phone: Optional[str]
    company: Optional[str]
    status: str
    tags: Optional[str]
    notes: Optional[str]
    created_at: str
    updated_at: str

class DealCreate(BaseModel):
    contact_id: int
    title: str
    value: float = 0.0
    stage: str = "lead"
    probability: int = 0
    expected_close_date: Optional[str] = None

class DealUpdate(BaseModel):
    contact_id: Optional[int] = None
    title: Optional[str] = None
    value: Optional[float] = None
    stage: Optional[str] = None
    probability: Optional[int] = None
    expected_close_date: Optional[str] = None

class DealResponse(BaseModel):
    id: int
    user_id: int
    contact_id: int
    title: str
    value: float
    stage: str
    probability: int
    expected_close_date: Optional[str]
    created_at: str
    updated_at: str

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    assigned_to_contact_id: Optional[int] = None
    due_date: Optional[str] = None
    priority: str = "medium"
    status: str = "pending"

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assigned_to_contact_id: Optional[int] = None
    due_date: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    completed: Optional[bool] = None

class TaskResponse(BaseModel):
    id: int
    user_id: int
    assigned_to_contact_id: Optional[int]
    title: str
    description: Optional[str]
    due_date: Optional[str]
    priority: str
    status: str
    completed: bool
    created_at: str
    updated_at: str

class NoteCreate(BaseModel):
    content: str
    related_to_contact_id: Optional[int] = None
    related_to_deal_id: Optional[int] = None
    note_type: str = "general"

class NoteResponse(BaseModel):
    id: int
    user_id: int
    related_to_contact_id: Optional[int]
    related_to_deal_id: Optional[int]
    content: str
    note_type: str
    created_at: str

class SendEmailRequest(BaseModel):
    subject: str
    body: str

class AnalyticsDashboardResponse(BaseModel):
    total_contacts: int
    contacts_by_status: Dict[str, int]
    deals_by_stage: Dict[str, int]
    total_deal_value: float
    tasks_summary: Dict[str, int]
    recent_activities: List[Dict]

# Initialize database
@app.on_event("startup")
def startup_event():
    init_db()

# Helper functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except Exception:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# Auth endpoints
@app.post("/api/signup", response_model=TokenResponse)
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    # Check if user exists
    existing_user = db.query(User).filter(User.username == request.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Create new user
    hashed_password = hash_password(request.password)
    new_user = User(username=request.username, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create token
    access_token = create_access_token(data={"sub": request.username})
    return TokenResponse(access_token=access_token, token_type="bearer", username=request.username)

@app.post("/api/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    # Find user
    user = db.query(User).filter(User.username == request.username).first()
    if not user or not verify_password(request.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Create token
    access_token = create_access_token(data={"sub": request.username})
    return TokenResponse(access_token=access_token, token_type="bearer", username=request.username)

@app.get("/api/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {"username": current_user.username, "id": current_user.id}

# Google services endpoints
@app.get("/api/google/auth-url")
def get_google_auth_url(current_user: User = Depends(get_current_user)):
    """Get Google OAuth URL for authorization"""
    google_manager = GoogleServicesManager()
    auth_url = google_manager.get_authorization_url()
    return {"auth_url": auth_url}

@app.post("/api/google/callback")
def google_callback(request: GoogleAuthRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Handle Google OAuth callback and store credentials"""
    try:
        google_manager = GoogleServicesManager()
        credentials = google_manager.exchange_code(request.authorization_code)
        
        # Store or update credentials in database
        existing_creds = db.query(GoogleCredentials).filter(GoogleCredentials.user_id == current_user.id).first()
        
        if existing_creds:
            existing_creds.access_token = credentials.token
            existing_creds.refresh_token = credentials.refresh_token if credentials.refresh_token else existing_creds.refresh_token
            existing_creds.token_expiry = credentials.expiry
            existing_creds.scopes = json.dumps(credentials.scopes) if credentials.scopes else None
            existing_creds.updated_at = datetime.utcnow()
        else:
            new_creds = GoogleCredentials(
                user_id=current_user.id,
                access_token=credentials.token,
                refresh_token=credentials.refresh_token,
                token_expiry=credentials.expiry,
                scopes=json.dumps(credentials.scopes) if credentials.scopes else None
            )
            db.add(new_creds)
        
        db.commit()
        return {"status": "success", "message": "Google services connected successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/google/status")
def get_google_status(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Check if user has connected Google services"""
    creds = db.query(GoogleCredentials).filter(GoogleCredentials.user_id == current_user.id).first()
    if creds:
        return {
            "connected": True,
            "scopes": json.loads(creds.scopes) if creds.scopes else [],
            "connected_at": creds.created_at.isoformat()
        }
    return {"connected": False}

@app.delete("/api/google/disconnect")
def disconnect_google(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Disconnect Google services"""
    creds = db.query(GoogleCredentials).filter(GoogleCredentials.user_id == current_user.id).first()
    if creds:
        db.delete(creds)
        db.commit()
    return {"status": "success", "message": "Google services disconnected"}

# Search endpoint
@app.post("/api/search", response_model=SearchResponse)
def search(request: SearchRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Search emails and documents from a specific person"""
    # Get user's Google credentials
    creds = db.query(GoogleCredentials).filter(GoogleCredentials.user_id == current_user.id).first()
    if not creds:
        raise HTTPException(status_code=400, detail="Google services not connected. Please connect in Configuration.")
    
    try:
        google_manager = GoogleServicesManager()
        
        # Reconstruct credentials
        from google.oauth2.credentials import Credentials
        credentials = Credentials(
            token=creds.access_token,
            refresh_token=creds.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=google_manager.client_id,
            client_secret=google_manager.client_secret,
            scopes=json.loads(creds.scopes) if creds.scopes else []
        )
        
        # Search emails and documents
        emails = google_manager.search_emails(credentials, request.person)
        documents = google_manager.search_documents(credentials, request.person)
        
        # Update credentials if refreshed
        if credentials.token != creds.access_token:
            creds.access_token = credentials.token
            creds.updated_at = datetime.utcnow()
            db.commit()
        
        return SearchResponse(emails=emails, documents=documents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

# Project Management Endpoints
@app.post("/api/projects", response_model=ProjectResponse)
def create_project(request: ProjectCreateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a new project"""
    try:
        new_project = Project(
            user_id=current_user.id,
            name=request.name,
            search_email=request.search_email,
            include_gmail=request.include_gmail,
            include_drive=request.include_drive,
            date_from=datetime.fromisoformat(request.date_from) if request.date_from else None,
            date_to=datetime.fromisoformat(request.date_to) if request.date_to else None,
            search_results=None
        )
        db.add(new_project)
        db.commit()
        db.refresh(new_project)
        
        return ProjectResponse(
            id=new_project.id,
            name=new_project.name,
            search_email=new_project.search_email,
            include_gmail=new_project.include_gmail,
            include_drive=new_project.include_drive,
            date_from=new_project.date_from.isoformat() if new_project.date_from else None,
            date_to=new_project.date_to.isoformat() if new_project.date_to else None,
            created_at=new_project.created_at.isoformat(),
            updated_at=new_project.updated_at.isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create project: {str(e)}")

@app.get("/api/projects", response_model=List[ProjectResponse])
def get_projects(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all projects for the current user"""
    projects = db.query(Project).filter(Project.user_id == current_user.id).order_by(Project.updated_at.desc()).all()
    
    return [
        ProjectResponse(
            id=p.id,
            name=p.name,
            search_email=p.search_email,
            include_gmail=p.include_gmail,
            include_drive=p.include_drive,
            date_from=p.date_from.isoformat() if p.date_from else None,
            date_to=p.date_to.isoformat() if p.date_to else None,
            created_at=p.created_at.isoformat(),
            updated_at=p.updated_at.isoformat()
        )
        for p in projects
    ]

@app.get("/api/projects/{project_id}")
def get_project(project_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get a specific project with its cached search results"""
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    response = {
        "id": project.id,
        "name": project.name,
        "search_email": project.search_email,
        "include_gmail": project.include_gmail,
        "include_drive": project.include_drive,
        "date_from": project.date_from.isoformat() if project.date_from else None,
        "date_to": project.date_to.isoformat() if project.date_to else None,
        "created_at": project.created_at.isoformat(),
        "updated_at": project.updated_at.isoformat(),
        "search_results": json.loads(project.search_results) if project.search_results else None
    }
    return response

@app.delete("/api/projects/{project_id}")
def delete_project(project_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete a project and all associated data (threads, chat messages, search results)"""
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Delete all chat messages for this project
    db.query(ChatMessage).filter(ChatMessage.project_id == project_id).delete()
    
    # Delete all threads for this project
    db.query(Thread).filter(Thread.project_id == project_id).delete()
    
    # Delete the project
    db.delete(project)
    db.commit()
    
    return {"status": "success", "message": "Project and all associated data deleted successfully"}

# Project Search Endpoint
@app.post("/api/projects/{project_id}/search")
def search_project(project_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Execute search for a project and cache results - supports multiple comma-separated emails"""
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get user's Google credentials
    creds = db.query(GoogleCredentials).filter(GoogleCredentials.user_id == current_user.id).first()
    if not creds:
        raise HTTPException(status_code=400, detail="Google services not connected. Please connect in Configuration.")
    
    try:
        # Parse multiple emails (comma-separated)
        email_addresses = [email.strip() for email in project.search_email.split(',') if email.strip()]
        
        print(f"\n=== Project Search Started ===")
        print(f"Project: {project.name}")
        print(f"Searching for {len(email_addresses)} email address(es): {email_addresses}")
        print(f"Include Gmail: {project.include_gmail}")
        print(f"Include Drive: {project.include_drive}")
        
        google_manager = GoogleServicesManager()
        
        # Reconstruct credentials
        from google.oauth2.credentials import Credentials
        credentials = Credentials(
            token=creds.access_token,
            refresh_token=creds.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=google_manager.client_id,
            client_secret=google_manager.client_secret,
            scopes=json.loads(creds.scopes) if creds.scopes else []
        )
        
        print(f"Credentials scopes: {credentials.scopes}")
        
        # Prepare date filters (Gmail uses YYYY/MM/DD format)
        date_from_str = None
        date_to_str = None
        if project.date_from:
            date_from_str = project.date_from.strftime('%Y/%m/%d')
        if project.date_to:
            date_to_str = project.date_to.strftime('%Y/%m/%d')
        
        # Aggregate results from all email addresses
        all_emails = []
        all_documents = []
        search_errors = []
        seen_email_ids = set()
        seen_doc_ids = set()
        
        # Search for each email address
        for email_addr in email_addresses:
            print(f"\n--- Searching for: {email_addr} ---")
            
            if project.include_gmail:
                try:
                    emails_from_person = google_manager.search_emails(credentials, email_addr, date_from_str, date_to_str)
                    # Deduplicate emails
                    for email in emails_from_person:
                        if email['id'] not in seen_email_ids:
                            all_emails.append(email)
                            seen_email_ids.add(email['id'])
                    print(f"Gmail: Found {len(emails_from_person)} emails from {email_addr} (Total unique: {len(all_emails)})")
                except Exception as e:
                    error_msg = f"Gmail search failed for {email_addr}: {str(e)}"
                    print(f"ERROR: {error_msg}")
                    search_errors.append(error_msg)
            
            if project.include_drive:
                try:
                    # Drive uses ISO format
                    drive_date_from = project.date_from.isoformat() if project.date_from else None
                    drive_date_to = project.date_to.isoformat() if project.date_to else None
                    docs_from_person = google_manager.search_documents(credentials, email_addr, drive_date_from, drive_date_to)
                    # Deduplicate documents
                    for doc in docs_from_person:
                        if doc['id'] not in seen_doc_ids:
                            all_documents.append(doc)
                            seen_doc_ids.add(doc['id'])
                    print(f"Drive: Found {len(docs_from_person)} documents from {email_addr} (Total unique: {len(all_documents)})")
                except Exception as e:
                    error_msg = f"Google Drive search failed for {email_addr}: {str(e)}"
                    print(f"ERROR: {error_msg}")
                    search_errors.append(error_msg)
        
        emails = all_emails
        documents = all_documents
        print(f"\n=== Search Summary ===")
        print(f"Total emails: {len(emails)}")
        print(f"Total documents: {len(documents)}")
        
        # Cache results
        results = {
            "emails": emails,
            "documents": documents,
            "searched_at": datetime.utcnow().isoformat(),
            "search_errors": search_errors
        }
        project.search_results = json.dumps(results)
        project.updated_at = datetime.utcnow()
        
        # Update credentials if refreshed
        if credentials.token != creds.access_token:
            creds.access_token = credentials.token
            creds.updated_at = datetime.utcnow()
        
        db.commit()
        
        print(f"=== Project Search Complete ===\n")
        
        # Return results with any errors
        response_data = {
            "emails": emails,
            "documents": documents
        }
        
        if search_errors:
            response_data["errors"] = search_errors
            print(f"Search completed with errors: {search_errors}")
        
        return response_data
    except Exception as e:
        error_detail = f"Search failed: {str(e)}"
        print(f"CRITICAL ERROR: {error_detail}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=error_detail)

# Document Parsing Endpoint
@app.get("/api/documents/{document_id}/parse")
def parse_document(document_id: str, mime_type: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Parse and extract content from a document"""
    # Get user's Google credentials
    creds = db.query(GoogleCredentials).filter(GoogleCredentials.user_id == current_user.id).first()
    if not creds:
        raise HTTPException(status_code=400, detail="Google services not connected.")
    
    try:
        from google.oauth2.credentials import Credentials
        google_manager = GoogleServicesManager()
        
        credentials = Credentials(
            token=creds.access_token,
            refresh_token=creds.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=google_manager.client_id,
            client_secret=google_manager.client_secret,
            scopes=json.loads(creds.scopes) if creds.scopes else []
        )
        
        content = DocumentParser.parse_document(credentials, document_id, mime_type)
        
        return {"content": content, "document_id": document_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse document: {str(e)}")

@app.get("/api/emails/{email_id}/content")
def get_email_content(email_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get full email content"""
    # Get user's Google credentials
    creds = db.query(GoogleCredentials).filter(GoogleCredentials.user_id == current_user.id).first()
    if not creds:
        raise HTTPException(status_code=400, detail="Google services not connected.")
    
    try:
        from google.oauth2.credentials import Credentials
        google_manager = GoogleServicesManager()
        
        credentials = Credentials(
            token=creds.access_token,
            refresh_token=creds.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=google_manager.client_id,
            client_secret=google_manager.client_secret,
            scopes=json.loads(creds.scopes) if creds.scopes else []
        )
        
        content = DocumentParser.get_email_body(credentials, email_id)
        
        return {"content": content, "email_id": email_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get email content: {str(e)}")

# AI Analysis Endpoint
@app.post("/api/projects/{project_id}/analyze", response_model=AnalyzeResponse)
def analyze_project(project_id: int, request: AnalyzeRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Analyze project data with AI based on user prompt"""
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if not project.search_results:
        raise HTTPException(status_code=400, detail="No search results available. Please run search first.")
    
    # Get or create thread
    thread_id = request.thread_id
    if not thread_id:
        # Create a new thread with auto-generated title
        new_thread = Thread(
            project_id=project_id,
            user_id=current_user.id,
            title=request.prompt[:50] + "..." if len(request.prompt) > 50 else request.prompt
        )
        db.add(new_thread)
        db.flush()
        thread_id = new_thread.id
    else:
        # Verify thread belongs to user
        thread = db.query(Thread).filter(Thread.id == thread_id, Thread.user_id == current_user.id).first()
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")
        thread.updated_at = datetime.utcnow()
    
    try:
        results = json.loads(project.search_results)
        emails = results.get("emails", [])
        documents = results.get("documents", [])
        
        # Initialize AI analyzer
        ai_analyzer = AIAnalyzer()
        
        # Optionally parse documents and emails for deeper analysis
        email_contents = {}
        document_contents = {}
        parsed_count = {"emails": 0, "documents": 0}
        
        if request.parse_emails:
            # Get user's Google credentials
            creds = db.query(GoogleCredentials).filter(GoogleCredentials.user_id == current_user.id).first()
            if creds:
                from google.oauth2.credentials import Credentials
                google_manager = GoogleServicesManager()
                
                credentials = Credentials(
                    token=creds.access_token,
                    refresh_token=creds.refresh_token,
                    token_uri="https://oauth2.googleapis.com/token",
                    client_id=google_manager.client_id,
                    client_secret=google_manager.client_secret,
                    scopes=json.loads(creds.scopes) if creds.scopes else []
                )
                
                # Parse up to 10 emails
                for email in emails[:10]:
                    content = DocumentParser.get_email_body(credentials, email['id'])
                    if content:
                        email_contents[email['id']] = content
                        parsed_count["emails"] += 1
        
        if request.parse_documents:
            # Get user's Google credentials
            creds = db.query(GoogleCredentials).filter(GoogleCredentials.user_id == current_user.id).first()
            if creds:
                from google.oauth2.credentials import Credentials
                google_manager = GoogleServicesManager()
                
                credentials = Credentials(
                    token=creds.access_token,
                    refresh_token=creds.refresh_token,
                    token_uri="https://oauth2.googleapis.com/token",
                    client_id=google_manager.client_id,
                    client_secret=google_manager.client_secret,
                    scopes=json.loads(creds.scopes) if creds.scopes else []
                )
                
                # Parse up to 5 documents
                for doc in documents[:5]:
                    content = DocumentParser.parse_document(credentials, doc['id'], doc.get('mime_type', ''))
                    if content:
                        document_contents[doc['id']] = content
                        parsed_count["documents"] += 1
        
        # Get conversation history for this thread
        chat_history = db.query(ChatMessage).filter(
            ChatMessage.thread_id == thread_id
        ).order_by(ChatMessage.created_at).all()
        
        # Build conversation context
        conversation_messages = []
        for msg in chat_history[-10:]:  # Last 10 messages for context
            conversation_messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Perform AI analysis with conversation context
        analysis = ai_analyzer.analyze_data(
            request.prompt,
            emails,
            documents,
            email_contents if email_contents else None,
            document_contents if document_contents else None,
            conversation_history=conversation_messages
        )
        
        # Save user message
        user_message = ChatMessage(
            thread_id=thread_id,
            project_id=project_id,
            user_id=current_user.id,
            role="user",
            content=request.prompt,
            parse_emails=request.parse_emails,
            parse_documents=request.parse_documents,
            parsed_count=json.dumps(parsed_count)
        )
        db.add(user_message)
        db.flush()
        
        # Save assistant response
        assistant_message = ChatMessage(
            thread_id=thread_id,
            project_id=project_id,
            user_id=current_user.id,
            role="assistant",
            content=analysis,
            parse_emails=False,
            parse_documents=False,
            parsed_count=json.dumps(parsed_count)
        )
        db.add(assistant_message)
        db.commit()
        db.refresh(assistant_message)
        
        return AnalyzeResponse(
            analysis=analysis, 
            parsed_count=parsed_count,
            message_id=assistant_message.id,
            thread_id=thread_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# Thread Management Endpoints
@app.post("/api/threads", response_model=ThreadResponse)
def create_thread(request: ThreadCreateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a new conversation thread in a project"""
    # Verify project ownership
    project = db.query(Project).filter(Project.id == request.project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    new_thread = Thread(
        project_id=request.project_id,
        user_id=current_user.id,
        title=request.title
    )
    db.add(new_thread)
    db.commit()
    db.refresh(new_thread)
    
    return ThreadResponse(
        id=new_thread.id,
        project_id=new_thread.project_id,
        title=new_thread.title,
        message_count=0,
        created_at=new_thread.created_at.isoformat(),
        updated_at=new_thread.updated_at.isoformat()
    )

@app.get("/api/projects/{project_id}/threads", response_model=List[ThreadResponse])
def get_threads(project_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all threads for a project"""
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    threads = db.query(Thread).filter(Thread.project_id == project_id).order_by(Thread.updated_at.desc()).all()
    
    result = []
    for thread in threads:
        message_count = db.query(ChatMessage).filter(ChatMessage.thread_id == thread.id).count()
        result.append(ThreadResponse(
            id=thread.id,
            project_id=thread.project_id,
            title=thread.title,
            message_count=message_count,
            created_at=thread.created_at.isoformat(),
            updated_at=thread.updated_at.isoformat()
        ))
    
    return result

@app.get("/api/threads/{thread_id}/messages", response_model=List[ChatMessageResponse])
def get_thread_messages(thread_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all messages in a thread"""
    thread = db.query(Thread).filter(Thread.id == thread_id, Thread.user_id == current_user.id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    messages = db.query(ChatMessage).filter(
        ChatMessage.thread_id == thread_id
    ).order_by(ChatMessage.created_at).all()
    
    return [
        ChatMessageResponse(
            id=msg.id,
            thread_id=msg.thread_id,
            role=msg.role,
            content=msg.content,
            parse_emails=msg.parse_emails,
            parse_documents=msg.parse_documents,
            parsed_count=json.loads(msg.parsed_count) if msg.parsed_count else None,
            created_at=msg.created_at.isoformat()
        )
        for msg in messages
    ]

@app.put("/api/threads/{thread_id}")
def update_thread(thread_id: int, title: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update thread title"""
    thread = db.query(Thread).filter(Thread.id == thread_id, Thread.user_id == current_user.id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    thread.title = title
    thread.updated_at = datetime.utcnow()
    db.commit()
    
    return {"status": "success", "message": "Thread updated"}

@app.delete("/api/threads/{thread_id}")
def delete_thread(thread_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete a thread and all its messages"""
    thread = db.query(Thread).filter(Thread.id == thread_id, Thread.user_id == current_user.id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    # Delete all messages in thread
    db.query(ChatMessage).filter(ChatMessage.thread_id == thread_id).delete()
    
    # Delete thread
    db.delete(thread)
    db.commit()
    
    return {"status": "success", "message": "Thread deleted"}

# Chat History Endpoints
@app.get("/api/projects/{project_id}/chat", response_model=List[ChatMessageResponse])
def get_chat_history(project_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get chat history for a project"""
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    messages = db.query(ChatMessage).filter(
        ChatMessage.project_id == project_id
    ).order_by(ChatMessage.created_at).all()
    
    return [
        ChatMessageResponse(
            id=msg.id,
            role=msg.role,
            content=msg.content,
            parse_emails=msg.parse_emails,
            parse_documents=msg.parse_documents,
            parsed_count=json.loads(msg.parsed_count) if msg.parsed_count else None,
            created_at=msg.created_at.isoformat()
        )
        for msg in messages
    ]

@app.delete("/api/projects/{project_id}/chat")
def clear_chat_history(project_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Clear chat history for a project"""
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.query(ChatMessage).filter(ChatMessage.project_id == project_id).delete()
    db.commit()
    
    return {"status": "success", "message": "Chat history cleared"}

# ==================== CRM API Endpoints ====================

# Contacts Endpoints
@app.post("/api/crm/contacts", response_model=ContactResponse)
def create_contact(contact: ContactCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a new contact"""
    db_contact = Contact(
        user_id=current_user.id,
        name=contact.name,
        email=contact.email,
        phone=contact.phone,
        company=contact.company,
        status=contact.status,
        tags=contact.tags,
        notes=contact.notes
    )
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    
    return ContactResponse(
        id=db_contact.id,
        user_id=db_contact.user_id,
        name=db_contact.name,
        email=db_contact.email,
        phone=db_contact.phone,
        company=db_contact.company,
        status=db_contact.status,
        tags=db_contact.tags,
        notes=db_contact.notes,
        created_at=db_contact.created_at.isoformat(),
        updated_at=db_contact.updated_at.isoformat()
    )

@app.get("/api/crm/contacts", response_model=List[ContactResponse])
def get_contacts(status: Optional[str] = None, search: Optional[str] = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all contacts with optional filters"""
    query = db.query(Contact).filter(Contact.user_id == current_user.id)
    
    if status:
        query = query.filter(Contact.status == status)
    
    if search:
        query = query.filter(
            (Contact.name.contains(search)) |
            (Contact.email.contains(search)) |
            (Contact.company.contains(search))
        )
    
    contacts = query.order_by(Contact.created_at.desc()).all()
    
    return [
        ContactResponse(
            id=c.id,
            user_id=c.user_id,
            name=c.name,
            email=c.email,
            phone=c.phone,
            company=c.company,
            status=c.status,
            tags=c.tags,
            notes=c.notes,
            created_at=c.created_at.isoformat(),
            updated_at=c.updated_at.isoformat()
        )
        for c in contacts
    ]

@app.get("/api/crm/contacts/{contact_id}", response_model=ContactResponse)
def get_contact(contact_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get a specific contact"""
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == current_user.id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    return ContactResponse(
        id=contact.id,
        user_id=contact.user_id,
        name=contact.name,
        email=contact.email,
        phone=contact.phone,
        company=contact.company,
        status=contact.status,
        tags=contact.tags,
        notes=contact.notes,
        created_at=contact.created_at.isoformat(),
        updated_at=contact.updated_at.isoformat()
    )

@app.put("/api/crm/contacts/{contact_id}", response_model=ContactResponse)
def update_contact(contact_id: int, contact_update: ContactUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update a contact"""
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == current_user.id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    if contact_update.name is not None:
        contact.name = contact_update.name
    if contact_update.email is not None:
        contact.email = contact_update.email
    if contact_update.phone is not None:
        contact.phone = contact_update.phone
    if contact_update.company is not None:
        contact.company = contact_update.company
    if contact_update.status is not None:
        contact.status = contact_update.status
    if contact_update.tags is not None:
        contact.tags = contact_update.tags
    if contact_update.notes is not None:
        contact.notes = contact_update.notes
    
    contact.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(contact)
    
    return ContactResponse(
        id=contact.id,
        user_id=contact.user_id,
        name=contact.name,
        email=contact.email,
        phone=contact.phone,
        company=contact.company,
        status=contact.status,
        tags=contact.tags,
        notes=contact.notes,
        created_at=contact.created_at.isoformat(),
        updated_at=contact.updated_at.isoformat()
    )

@app.delete("/api/crm/contacts/{contact_id}")
def delete_contact(contact_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete a contact"""
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == current_user.id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    db.delete(contact)
    db.commit()
    
    return {"status": "success", "message": "Contact deleted"}

# Deals Endpoints
@app.post("/api/crm/deals", response_model=DealResponse)
def create_deal(deal: DealCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a new deal"""
    # Verify contact exists and belongs to user
    contact = db.query(Contact).filter(Contact.id == deal.contact_id, Contact.user_id == current_user.id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    expected_close = None
    if deal.expected_close_date:
        try:
            expected_close = datetime.fromisoformat(deal.expected_close_date)
        except:
            pass
    
    db_deal = Deal(
        user_id=current_user.id,
        contact_id=deal.contact_id,
        title=deal.title,
        value=deal.value,
        stage=deal.stage,
        probability=deal.probability,
        expected_close_date=expected_close
    )
    db.add(db_deal)
    db.commit()
    db.refresh(db_deal)
    
    return DealResponse(
        id=db_deal.id,
        user_id=db_deal.user_id,
        contact_id=db_deal.contact_id,
        title=db_deal.title,
        value=db_deal.value,
        stage=db_deal.stage,
        probability=db_deal.probability,
        expected_close_date=db_deal.expected_close_date.isoformat() if db_deal.expected_close_date else None,
        created_at=db_deal.created_at.isoformat(),
        updated_at=db_deal.updated_at.isoformat()
    )

@app.get("/api/crm/deals", response_model=List[DealResponse])
def get_deals(stage: Optional[str] = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all deals with optional stage filter"""
    query = db.query(Deal).filter(Deal.user_id == current_user.id)
    
    if stage:
        query = query.filter(Deal.stage == stage)
    
    deals = query.order_by(Deal.created_at.desc()).all()
    
    return [
        DealResponse(
            id=d.id,
            user_id=d.user_id,
            contact_id=d.contact_id,
            title=d.title,
            value=d.value,
            stage=d.stage,
            probability=d.probability,
            expected_close_date=d.expected_close_date.isoformat() if d.expected_close_date else None,
            created_at=d.created_at.isoformat(),
            updated_at=d.updated_at.isoformat()
        )
        for d in deals
    ]

@app.get("/api/crm/deals/{deal_id}", response_model=DealResponse)
def get_deal(deal_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get a specific deal"""
    deal = db.query(Deal).filter(Deal.id == deal_id, Deal.user_id == current_user.id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    return DealResponse(
        id=deal.id,
        user_id=deal.user_id,
        contact_id=deal.contact_id,
        title=deal.title,
        value=deal.value,
        stage=deal.stage,
        probability=deal.probability,
        expected_close_date=deal.expected_close_date.isoformat() if deal.expected_close_date else None,
        created_at=deal.created_at.isoformat(),
        updated_at=deal.updated_at.isoformat()
    )

@app.put("/api/crm/deals/{deal_id}", response_model=DealResponse)
def update_deal(deal_id: int, deal_update: DealUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update a deal"""
    deal = db.query(Deal).filter(Deal.id == deal_id, Deal.user_id == current_user.id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    if deal_update.contact_id is not None:
        contact = db.query(Contact).filter(Contact.id == deal_update.contact_id, Contact.user_id == current_user.id).first()
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")
        deal.contact_id = deal_update.contact_id
    
    if deal_update.title is not None:
        deal.title = deal_update.title
    if deal_update.value is not None:
        deal.value = deal_update.value
    if deal_update.stage is not None:
        deal.stage = deal_update.stage
    if deal_update.probability is not None:
        deal.probability = deal_update.probability
    if deal_update.expected_close_date is not None:
        try:
            deal.expected_close_date = datetime.fromisoformat(deal_update.expected_close_date)
        except:
            pass
    
    deal.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(deal)
    
    return DealResponse(
        id=deal.id,
        user_id=deal.user_id,
        contact_id=deal.contact_id,
        title=deal.title,
        value=deal.value,
        stage=deal.stage,
        probability=deal.probability,
        expected_close_date=deal.expected_close_date.isoformat() if deal.expected_close_date else None,
        created_at=deal.created_at.isoformat(),
        updated_at=deal.updated_at.isoformat()
    )

@app.delete("/api/crm/deals/{deal_id}")
def delete_deal(deal_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete a deal"""
    deal = db.query(Deal).filter(Deal.id == deal_id, Deal.user_id == current_user.id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    db.delete(deal)
    db.commit()
    
    return {"status": "success", "message": "Deal deleted"}

# Tasks Endpoints
@app.post("/api/crm/tasks", response_model=TaskResponse)
def create_task(task: TaskCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a new task"""
    if task.assigned_to_contact_id:
        contact = db.query(Contact).filter(Contact.id == task.assigned_to_contact_id, Contact.user_id == current_user.id).first()
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")
    
    due = None
    if task.due_date:
        try:
            due = datetime.fromisoformat(task.due_date)
        except:
            pass
    
    db_task = Task(
        user_id=current_user.id,
        assigned_to_contact_id=task.assigned_to_contact_id,
        title=task.title,
        description=task.description,
        due_date=due,
        priority=task.priority,
        status=task.status,
        completed=False
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    return TaskResponse(
        id=db_task.id,
        user_id=db_task.user_id,
        assigned_to_contact_id=db_task.assigned_to_contact_id,
        title=db_task.title,
        description=db_task.description,
        due_date=db_task.due_date.isoformat() if db_task.due_date else None,
        priority=db_task.priority,
        status=db_task.status,
        completed=db_task.completed,
        created_at=db_task.created_at.isoformat(),
        updated_at=db_task.updated_at.isoformat()
    )

@app.get("/api/crm/tasks", response_model=List[TaskResponse])
def get_tasks(status: Optional[str] = None, priority: Optional[str] = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all tasks with optional filters"""
    query = db.query(Task).filter(Task.user_id == current_user.id)
    
    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)
    
    tasks = query.order_by(Task.due_date.asc().nullslast(), Task.created_at.desc()).all()
    
    return [
        TaskResponse(
            id=t.id,
            user_id=t.user_id,
            assigned_to_contact_id=t.assigned_to_contact_id,
            title=t.title,
            description=t.description,
            due_date=t.due_date.isoformat() if t.due_date else None,
            priority=t.priority,
            status=t.status,
            completed=t.completed,
            created_at=t.created_at.isoformat(),
            updated_at=t.updated_at.isoformat()
        )
        for t in tasks
    ]

@app.put("/api/crm/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_update: TaskUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update a task"""
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task_update.assigned_to_contact_id is not None:
        contact = db.query(Contact).filter(Contact.id == task_update.assigned_to_contact_id, Contact.user_id == current_user.id).first()
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")
        task.assigned_to_contact_id = task_update.assigned_to_contact_id
    
    if task_update.title is not None:
        task.title = task_update.title
    if task_update.description is not None:
        task.description = task_update.description
    if task_update.due_date is not None:
        try:
            task.due_date = datetime.fromisoformat(task_update.due_date)
        except:
            pass
    if task_update.priority is not None:
        task.priority = task_update.priority
    if task_update.status is not None:
        task.status = task_update.status
    if task_update.completed is not None:
        task.completed = task_update.completed
        if task.completed:
            task.status = "completed"
    
    task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(task)
    
    return TaskResponse(
        id=task.id,
        user_id=task.user_id,
        assigned_to_contact_id=task.assigned_to_contact_id,
        title=task.title,
        description=task.description,
        due_date=task.due_date.isoformat() if task.due_date else None,
        priority=task.priority,
        status=task.status,
        completed=task.completed,
        created_at=task.created_at.isoformat(),
        updated_at=task.updated_at.isoformat()
    )

@app.delete("/api/crm/tasks/{task_id}")
def delete_task(task_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete a task"""
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()
    
    return {"status": "success", "message": "Task deleted"}

# Notes Endpoints
@app.post("/api/crm/notes", response_model=NoteResponse)
def create_note(note: NoteCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a new note"""
    if note.related_to_contact_id:
        contact = db.query(Contact).filter(Contact.id == note.related_to_contact_id, Contact.user_id == current_user.id).first()
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")
    
    if note.related_to_deal_id:
        deal = db.query(Deal).filter(Deal.id == note.related_to_deal_id, Deal.user_id == current_user.id).first()
        if not deal:
            raise HTTPException(status_code=404, detail="Deal not found")
    
    db_note = Note(
        user_id=current_user.id,
        related_to_contact_id=note.related_to_contact_id,
        related_to_deal_id=note.related_to_deal_id,
        content=note.content,
        note_type=note.note_type
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    
    return NoteResponse(
        id=db_note.id,
        user_id=db_note.user_id,
        related_to_contact_id=db_note.related_to_contact_id,
        related_to_deal_id=db_note.related_to_deal_id,
        content=db_note.content,
        note_type=db_note.note_type,
        created_at=db_note.created_at.isoformat()
    )

@app.get("/api/crm/notes", response_model=List[NoteResponse])
def get_notes(contact_id: Optional[int] = None, deal_id: Optional[int] = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all notes with optional filters"""
    query = db.query(Note).filter(Note.user_id == current_user.id)
    
    if contact_id:
        query = query.filter(Note.related_to_contact_id == contact_id)
    if deal_id:
        query = query.filter(Note.related_to_deal_id == deal_id)
    
    notes = query.order_by(Note.created_at.desc()).all()
    
    return [
        NoteResponse(
            id=n.id,
            user_id=n.user_id,
            related_to_contact_id=n.related_to_contact_id,
            related_to_deal_id=n.related_to_deal_id,
            content=n.content,
            note_type=n.note_type,
            created_at=n.created_at.isoformat()
        )
        for n in notes
    ]

# Email Integration Endpoints
@app.post("/api/crm/contacts/{contact_id}/send-email")
def send_email_to_contact(contact_id: int, email_request: SendEmailRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Send an email to a contact via Gmail API"""
    # Get contact
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == current_user.id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    if not contact.email:
        raise HTTPException(status_code=400, detail="Contact does not have an email address")
    
    # Get user's Google credentials
    google_creds = db.query(GoogleCredentials).filter(GoogleCredentials.user_id == current_user.id).first()
    if not google_creds:
        raise HTTPException(status_code=400, detail="Google credentials not found. Please connect your Google account.")
    
    # Create credentials object
    from google.oauth2.credentials import Credentials as GoogleCreds
    credentials = GoogleCreds(
        token=google_creds.access_token,
        refresh_token=google_creds.refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=GoogleServicesManager().client_id,
        client_secret=GoogleServicesManager().client_secret,
        scopes=json.loads(google_creds.scopes)
    )
    
    # Send email
    try:
        google_manager = GoogleServicesManager()
        result = google_manager.send_email(
            credentials=credentials,
            to=contact.email,
            subject=email_request.subject,
            body=email_request.body
        )
        
        # Log the email
        email_log = EmailLog(
            user_id=current_user.id,
            sent_to_contact_id=contact_id,
            subject=email_request.subject,
            body=email_request.body,
            sent_at=datetime.utcnow(),
            gmail_thread_id=result.get('thread_id')
        )
        db.add(email_log)
        db.commit()
        
        return {
            "status": "success",
            "message": "Email sent successfully",
            "message_id": result.get('message_id'),
            "thread_id": result.get('thread_id')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

@app.get("/api/crm/contacts/{contact_id}/emails")
def get_contact_emails(contact_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get email history for a contact"""
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == current_user.id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    emails = db.query(EmailLog).filter(
        EmailLog.sent_to_contact_id == contact_id,
        EmailLog.user_id == current_user.id
    ).order_by(EmailLog.sent_at.desc()).all()
    
    return [
        {
            'id': e.id,
            'subject': e.subject,
            'body': e.body,
            'sent_at': e.sent_at.isoformat(),
            'gmail_thread_id': e.gmail_thread_id
        }
        for e in emails
    ]

# Analytics Endpoint
@app.get("/api/crm/analytics/dashboard", response_model=AnalyticsDashboardResponse)
def get_analytics_dashboard(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get CRM analytics dashboard data"""
    
    # Total contacts
    total_contacts = db.query(Contact).filter(Contact.user_id == current_user.id).count()
    
    # Contacts by status
    contacts = db.query(Contact).filter(Contact.user_id == current_user.id).all()
    contacts_by_status = {}
    for contact in contacts:
        status = contact.status or 'unknown'
        contacts_by_status[status] = contacts_by_status.get(status, 0) + 1
    
    # Deals by stage
    deals = db.query(Deal).filter(Deal.user_id == current_user.id).all()
    deals_by_stage = {}
    total_deal_value = 0.0
    for deal in deals:
        stage = deal.stage or 'unknown'
        deals_by_stage[stage] = deals_by_stage.get(stage, 0) + 1
        total_deal_value += deal.value or 0.0
    
    # Tasks summary
    tasks = db.query(Task).filter(Task.user_id == current_user.id).all()
    tasks_summary = {
        'total': len(tasks),
        'pending': 0,
        'in_progress': 0,
        'completed': 0,
        'overdue': 0
    }
    
    now = datetime.utcnow()
    for task in tasks:
        status = task.status or 'pending'
        tasks_summary[status] = tasks_summary.get(status, 0) + 1
        
        # Check for overdue tasks
        if task.due_date and task.due_date < now and not task.completed:
            tasks_summary['overdue'] += 1
    
    # Recent activities (last 10 notes)
    recent_notes = db.query(Note).filter(Note.user_id == current_user.id).order_by(Note.created_at.desc()).limit(10).all()
    recent_activities = []
    
    for note in recent_notes:
        activity = {
            'id': note.id,
            'type': note.note_type,
            'content': note.content[:100] + '...' if len(note.content) > 100 else note.content,
            'created_at': note.created_at.isoformat(),
            'contact_id': note.related_to_contact_id,
            'deal_id': note.related_to_deal_id
        }
        
        # Get related contact name if available
        if note.related_to_contact_id:
            contact = db.query(Contact).filter(Contact.id == note.related_to_contact_id).first()
            if contact:
                activity['contact_name'] = contact.name
        
        # Get related deal title if available
        if note.related_to_deal_id:
            deal = db.query(Deal).filter(Deal.id == note.related_to_deal_id).first()
            if deal:
                activity['deal_title'] = deal.title
        
        recent_activities.append(activity)
    
    return AnalyticsDashboardResponse(
        total_contacts=total_contacts,
        contacts_by_status=contacts_by_status,
        deals_by_stage=deals_by_stage,
        total_deal_value=total_deal_value,
        tasks_summary=tasks_summary,
        recent_activities=recent_activities
    )

@app.get("/")
def root():
    return {"message": "Tivrag API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)

