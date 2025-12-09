# Tivrag - Integrated CRM & Google Services Platform

A modern web application that combines powerful CRM capabilities with Google services integration. Search through Gmail and Google Drive while managing your customer relationships, sales pipeline, and tasks. Built with React and FastAPI.

## Features

### Core Features
- 🔐 **User Authentication**: Simple signup and login system (no email verification required)
- 🔗 **Google OAuth Integration**: Connect your Gmail and Google Drive accounts securely
- 📧 **Email Search**: Find all emails from a specific person
- 📄 **Document Search**: Find all Google Drive documents from a specific person
- 🤖 **AI Analysis**: Analyze emails and documents with AI-powered insights
- 🎨 **Modern UI**: Beautiful, responsive interface with smooth animations

### CRM Features (NEW!)
- 👥 **Contact Management**: Store and organize customer/lead information
- 💼 **Sales Pipeline**: Visual kanban board for deal management with 6 stages
- ✅ **Task Management**: Track to-dos with priorities and due dates
- 📝 **Notes & Activities**: Log interactions and maintain activity history
- ✉️ **Email Integration**: Send emails directly to contacts via Gmail API
- 📊 **Analytics Dashboard**: Real-time metrics, charts, and insights
- 🔍 **Search & Filter**: Find contacts, deals, and tasks quickly
- 📱 **Responsive Design**: Works seamlessly on desktop and mobile

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: ORM for database management
- **SQLite**: Lightweight database
- **Google APIs**: Gmail and Drive integration
- **JWT**: Secure authentication tokens
- **bcrypt**: Password hashing

### Frontend
- **React 18**: UI framework
- **Vite**: Fast build tool
- **React Router**: Client-side routing
- **Axios**: HTTP client

## Project Structure

```
tivrag/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── database.py          # Database models and setup
│   ├── google_services.py   # Google API integration
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── pages/          # React pages
│   │   ├── App.jsx         # Main app component
│   │   ├── api.js          # API client
│   │   └── main.jsx        # Entry point
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 16+
- Google Cloud Project with Gmail and Drive APIs enabled

### Step 1: Google Cloud Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select an existing one)
3. Enable the following APIs:
   - Gmail API
   - Google Drive API
4. Go to "Credentials" → "Create Credentials" → "OAuth client ID"
5. Configure OAuth consent screen:
   - User Type: External
   - Add scopes: `gmail.readonly`, `drive.readonly`
6. Create OAuth 2.0 Client ID:
   - Application type: Web application
   - Authorized redirect URIs: `http://localhost:5175/configuration/callback`
7. Download the credentials or note the Client ID and Client Secret

### Step 2: Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create a virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables (optional)
export GOOGLE_CLIENT_ID="your-client-id"
export GOOGLE_CLIENT_SECRET="your-client-secret"

# Or edit google_services.py directly and replace:
# - YOUR_CLIENT_ID with your actual client ID
# - YOUR_CLIENT_SECRET with your actual client secret

# Run the server
python main.py
```

The backend will start at `http://localhost:8002`

### Step 3: Frontend Setup

```bash
# Open a new terminal and navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```

The frontend will start at `http://localhost:5175`

## Usage

### 1. Sign Up / Login
- Visit `http://localhost:5175`
- Create a new account or log in with existing credentials

### 2. Connect Google Services
- Navigate to the **Configuration** page
- Click "Connect Google Services"
- You'll be redirected to Google to authorize the application
- Grant permissions for Gmail (read-only) and Google Drive (read-only)
- You'll be redirected back to the Configuration page

### 3. Search for Content
- Navigate to the **Workplace** page
- Create a new project and enter the email address of the person you want to search for
- Click "Create Project & Search"
- View all emails and documents from that person
- Use AI Assistant to analyze the content

### 4. Use CRM Features
- Navigate to the **CRM** page
- **Contacts Tab**: Add your customers and leads
- **Deals Tab**: Track sales opportunities through the pipeline
- **Tasks Tab**: Create and manage to-do items
- **Notes Tab**: Log activities and interactions
- **Dashboard**: View analytics and metrics

## API Endpoints

### Authentication
- `POST /api/signup` - Create a new account
- `POST /api/login` - Log in to an account
- `GET /api/me` - Get current user info

### Google Services
- `GET /api/google/auth-url` - Get Google OAuth authorization URL
- `POST /api/google/callback` - Handle OAuth callback
- `GET /api/google/status` - Check connection status
- `DELETE /api/google/disconnect` - Disconnect Google services

### Search & Projects
- `POST /api/projects` - Create a new project
- `GET /api/projects` - Get all projects
- `POST /api/projects/{id}/search` - Search emails and documents for a project
- `GET /api/projects/{id}/threads` - Get project threads
- `POST /api/projects/{id}/threads` - Create a new thread
- `POST /api/analyze` - Analyze content with AI

### CRM Endpoints
- **Contacts**: `GET|POST|PUT|DELETE /api/crm/contacts`
- **Deals**: `GET|POST|PUT|DELETE /api/crm/deals`
- **Tasks**: `GET|POST|PUT|DELETE /api/crm/tasks`
- **Notes**: `GET|POST /api/crm/notes`
- **Email**: `POST /api/crm/contacts/{id}/send-email`
- **Analytics**: `GET /api/crm/analytics/dashboard`

## Security Notes

⚠️ **Important**: This is a development setup. For production:

1. Change the `SECRET_KEY` in `backend/main.py`
2. Use HTTPS for all connections
3. Store credentials securely (use environment variables or secret management)
4. Add rate limiting
5. Implement proper error handling and logging
6. Use a production database (PostgreSQL, MySQL, etc.)
7. Add CORS restrictions for specific domains
8. Implement token refresh mechanism

## Database

The application uses SQLite for simplicity. The database file (`tivrag.db`) will be created automatically in the `backend` directory when you first run the application.

### Tables

**Core Tables:**
- **users**: User accounts (id, username, password, created_at)
- **google_credentials**: OAuth tokens for Google services
- **projects**: Search projects with cached results
- **threads**: Conversation threads for AI analysis
- **chat_messages**: Chat history with AI assistant

**CRM Tables:**
- **contacts**: Customer and lead information
- **deals**: Sales pipeline opportunities
- **tasks**: To-do items and assignments
- **notes**: Activity logs and notes
- **email_logs**: Sent email tracking

## Troubleshooting

### Google OAuth Issues
- Make sure redirect URI matches exactly: `http://localhost:5175/configuration/callback`
- Check that Gmail and Drive APIs are enabled in Google Cloud Console
- Verify that OAuth consent screen is configured properly

### Backend Connection Issues
- Ensure the backend is running on port 8002
- Check CORS settings in `main.py`
- Verify database file permissions

### Frontend Issues
- Clear browser cache and localStorage
- Check browser console for errors
- Ensure Node.js version is 16 or higher

## Development

### Backend Development
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python main.py
```

### Frontend Development
```bash
cd frontend
npm run dev
```

## Building for Production

### Frontend
```bash
cd frontend
npm run build
```

The built files will be in `frontend/dist/`

### Backend
Use a production ASGI server like Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

## License

This project is created for demonstration purposes.

## Documentation

For detailed information about the CRM features, see:
- **[CRM User Guide](CRM_USER_GUIDE.md)** - Complete guide for using CRM features
- **[CRM Implementation Summary](CRM_IMPLEMENTATION_SUMMARY.md)** - Technical implementation details

## Future Enhancements

### General
- [ ] Email verification for signup
- [ ] Password reset functionality
- [ ] Multi-account support
- [ ] Real-time notifications
- [ ] Mobile native apps

### CRM
- [ ] CSV import/export for contacts
- [ ] Email templates
- [ ] Advanced reporting and forecasting
- [ ] Calendar integration
- [ ] Custom fields
- [ ] Deal automation and workflows
- [ ] Team collaboration features

## Support

For issues and questions, please create an issue in the repository.

