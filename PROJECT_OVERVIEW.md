# 🎯 Tivrag - Project Overview

## What is Tivrag?

Tivrag is a web application that helps you search through your Gmail emails and Google Drive documents from specific people. It's perfect for finding all communications and files you've received from a particular contact.

## ✨ Key Features

### 🔐 Authentication System
- Simple signup/login (no email verification required)
- Secure password hashing with bcrypt
- JWT token-based authentication
- Protected routes and API endpoints

### 🔗 Google Integration
- OAuth 2.0 secure authentication
- Gmail API integration (read-only)
- Google Drive API integration (read-only)
- Automatic token refresh handling

### 🔍 Search Capabilities
- Search emails by sender email address
- Search Drive documents by owner email
- View email subjects, snippets, dates
- View document names, types, modification dates
- Direct links to documents

### 🎨 Modern UI
- Beautiful gradient design
- Responsive layout
- Smooth animations
- Easy-to-use interface
- Real-time feedback

## 📁 Complete Project Structure

```
tivrag/
│
├── 📄 README.md                    # Comprehensive documentation
├── 📄 QUICKSTART.md                # Quick start guide
├── 📄 PROJECT_OVERVIEW.md          # This file
├── 🚀 start.sh                     # Launch script (macOS/Linux)
├── 🚀 start.bat                    # Launch script (Windows)
├── 📝 .gitignore                   # Git ignore rules
│
├── 🔧 backend/                     # FastAPI Backend
│   ├── main.py                     # Main application with all endpoints
│   ├── database.py                 # SQLAlchemy models and database setup
│   ├── google_services.py          # Google API integration logic
│   └── requirements.txt            # Python dependencies
│
└── 💻 frontend/                    # React Frontend
    ├── index.html                  # HTML entry point
    ├── package.json                # Node.js dependencies
    ├── vite.config.js              # Vite configuration
    │
    └── src/
        ├── main.jsx                # React entry point
        ├── App.jsx                 # Main app with routing
        ├── api.js                  # API client and endpoints
        ├── index.css               # Global styles
        │
        └── pages/
            ├── Signup.jsx          # User registration page
            ├── Login.jsx           # User login page
            ├── Auth.css            # Auth pages styles
            ├── Dashboard.jsx       # Home dashboard
            ├── Dashboard.css       # Dashboard styles
            ├── Configuration.jsx   # Google services connection
            ├── Configuration.css   # Configuration styles
            ├── ConfigurationCallback.jsx  # OAuth callback handler
            ├── ConfigurationCallback.css  # Callback styles
            ├── Workplace.jsx       # Search interface
            └── Workplace.css       # Workplace styles
```

## 🛠️ Technology Stack

### Backend Technologies
| Technology | Purpose |
|------------|---------|
| **FastAPI** | Modern Python web framework |
| **SQLAlchemy** | ORM for database operations |
| **SQLite** | Lightweight database |
| **bcrypt** | Password hashing |
| **PyJWT** | JWT token generation |
| **Google API Client** | Gmail & Drive integration |
| **Uvicorn** | ASGI server |

### Frontend Technologies
| Technology | Purpose |
|------------|---------|
| **React 18** | UI framework |
| **Vite** | Build tool & dev server |
| **React Router** | Client-side routing |
| **Axios** | HTTP client |

## 🎯 User Flow

```
1. User visits app → Redirected to Login
                    ↓
2. Sign Up / Login → Get JWT token → Redirect to Dashboard
                    ↓
3. Dashboard → Navigate to Configuration
                    ↓
4. Configuration → Click "Connect Google" → Google OAuth flow
                    ↓
5. Return to app → Credentials stored in database
                    ↓
6. Navigate to Workplace → Enter person's email
                    ↓
7. Click Search → Backend calls Gmail & Drive APIs
                    ↓
8. Results displayed → Emails & Documents shown
                    ↓
9. Click document link → Opens in new tab
```

## 📊 Database Schema

### Users Table
```sql
id          INTEGER PRIMARY KEY
username    VARCHAR UNIQUE
password    VARCHAR (hashed)
created_at  DATETIME
```

### Google Credentials Table
```sql
id              INTEGER PRIMARY KEY
user_id         INTEGER (foreign key)
access_token    VARCHAR
refresh_token   VARCHAR
token_expiry    DATETIME
scopes          VARCHAR (JSON)
created_at      DATETIME
updated_at      DATETIME
```

## 🔌 API Architecture

### Authentication Flow
```
Client → POST /api/signup → Server
                          ↓
                    Hash password
                          ↓
                    Save to database
                          ↓
                    Generate JWT token
                          ↓
Client ← Return token ← Server
```

### Google OAuth Flow
```
1. Client → GET /api/google/auth-url → Server
                                      ↓
                                Generate OAuth URL
                                      ↓
2. Client ← Return URL ← Server
           ↓
3. User clicks → Redirects to Google
                                      ↓
4. User authorizes → Google redirects back with code
                                      ↓
5. Client → POST /api/google/callback (with code) → Server
                                                    ↓
                                            Exchange code for tokens
                                                    ↓
                                            Save tokens to database
                                                    ↓
6. Client ← Success response ← Server
```

### Search Flow
```
Client → POST /api/search (with person email) → Server
                                                ↓
                                        Get user's credentials
                                                ↓
                                        Call Gmail API
                                                ↓
                                        Call Drive API
                                                ↓
                                        Format results
                                                ↓
Client ← Return emails + documents ← Server
```

## 🔒 Security Features

- ✅ Password hashing with bcrypt (10 salt rounds)
- ✅ JWT token authentication with expiry (7 days)
- ✅ HTTP Bearer token authorization
- ✅ CORS protection (configurable origins)
- ✅ OAuth 2.0 for Google services
- ✅ Secure credential storage in database
- ✅ Protected API endpoints
- ✅ Token refresh handling

## 🚀 Getting Started (Summary)

1. **Install Prerequisites**: Python 3.8+, Node.js 16+
2. **Setup Google Cloud**: Create project, enable APIs, get OAuth credentials
3. **Configure App**: Update `google_services.py` with credentials
4. **Run**: Execute `./start.sh` (or `start.bat` on Windows)
5. **Use**: Open http://localhost:3000

## 📝 API Endpoints Summary

### Auth Endpoints
- `POST /api/signup` - Register new user
- `POST /api/login` - Authenticate user
- `GET /api/me` - Get current user (requires token)

### Google Endpoints
- `GET /api/google/auth-url` - Get OAuth URL
- `POST /api/google/callback` - Handle OAuth callback
- `GET /api/google/status` - Check connection status
- `DELETE /api/google/disconnect` - Remove connection

### Search Endpoints
- `POST /api/search` - Search emails and documents

## 🎨 UI Pages

1. **Signup Page** - User registration with validation
2. **Login Page** - User authentication
3. **Dashboard** - Welcome page with quick actions
4. **Configuration** - Google services connection management
5. **Workplace** - Search interface and results display
6. **Callback Page** - OAuth flow completion handler

## 🔄 Development Workflow

### Backend Development
```bash
cd backend
source venv/bin/activate
python main.py
# Server runs on http://localhost:8002
# API docs at http://localhost:8002/docs
```

### Frontend Development
```bash
cd frontend
npm run dev
# Server runs on http://localhost:5175
# Hot reload enabled
```

## 📈 Future Enhancements

### Planned Features
- [ ] Email/document previews
- [ ] Advanced filters (date range, file type)
- [ ] Export results to CSV/PDF
- [ ] Multiple Google account support
- [ ] Search history
- [ ] Favorites/bookmarks
- [ ] Real-time notifications
- [ ] Email threading
- [ ] Attachment downloads
- [ ] Shared folder access

### Technical Improvements
- [ ] PostgreSQL for production
- [ ] Redis for caching
- [ ] Background job queue
- [ ] Rate limiting
- [ ] API versioning
- [ ] Unit tests
- [ ] E2E tests
- [ ] Docker deployment
- [ ] CI/CD pipeline
- [ ] Monitoring & logging

## 🐛 Known Limitations

- Search limited to 50 results per service
- No email content preview (only snippets)
- No attachment search
- Single Google account per user
- No email or document deletion
- OAuth tokens must be manually refreshed after expiry
- Development-only security settings

## 💡 Tips for Users

1. **Email Search**: Use the complete email address for best results
2. **Document Search**: Only finds documents owned by that person
3. **Connection Issues**: Try disconnecting and reconnecting Google services
4. **No Results**: Verify the email address and check Google account permissions
5. **Performance**: Initial search may take a few seconds

## 📚 Learning Resources

If you want to learn more about the technologies used:

- **FastAPI**: https://fastapi.tiangolo.com/
- **React**: https://react.dev/
- **Google APIs**: https://developers.google.com/gmail/api
- **OAuth 2.0**: https://oauth.net/2/

## 🎉 Credits

Built with modern web technologies and best practices for a seamless user experience.

---

**Ready to start?** Check out [QUICKSTART.md](QUICKSTART.md) for immediate setup instructions!

