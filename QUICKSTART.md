# Quick Start Guide

## Prerequisites
- Python 3.8+
- Node.js 16+
- Google Cloud Project with OAuth credentials

## 🚀 Quick Start

### Automated Setup (Recommended)

**macOS/Linux:**
```bash
./start.sh
```

**Windows:**
```bash
start.bat
```

### Manual Setup

#### 1. Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure Google OAuth (see below)

python main.py
```

#### 2. Frontend Setup (New Terminal)
```bash
cd frontend
npm install
npm run dev
```

## 🔑 Google OAuth Configuration

### Step 1: Create Google Cloud Project
1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project

### Step 2: Enable APIs
- Gmail API
- Google Drive API

### Step 3: Create OAuth Credentials
1. Go to **Credentials** → **Create Credentials** → **OAuth client ID**
2. Configure OAuth consent screen (External)
3. Add test users if needed
4. Create Web application credentials
5. Add redirect URI: `http://localhost:5175/configuration/callback`

### Step 4: Update Application
Edit `backend/google_services.py`:
```python
self.client_id = "YOUR_ACTUAL_CLIENT_ID"
self.client_secret = "YOUR_ACTUAL_CLIENT_SECRET"
```

**Or** set environment variables:
```bash
export GOOGLE_CLIENT_ID="your-client-id"
export GOOGLE_CLIENT_SECRET="your-client-secret"
```

## 📱 Using the Application

### 1. Sign Up
- Open http://localhost:3000
- Click "Sign Up"
- Create username and password

### 2. Connect Google Services
- Go to **Configuration**
- Click "Connect Google Services"
- Authorize the application in Google
- Return to Configuration page (automatic)

### 3. Search for Content
- Go to **Workplace**
- Enter person's email address
- Click Search
- View results

## 🔗 URLs
- **Frontend**: http://localhost:5175
- **Backend**: http://localhost:8002
- **API Docs**: http://localhost:8002/docs

## 🛠️ Common Issues

### Issue: "Google services not connected"
**Solution**: Go to Configuration page and connect Google services first

### Issue: OAuth redirect error
**Solution**: Verify redirect URI is exactly `http://localhost:5175/configuration/callback`

### Issue: Backend connection failed
**Solution**: 
- Check backend is running on port 8002
- Check CORS settings
- Try restarting backend

### Issue: No results found
**Solution**:
- Verify email address is correct
- Ensure person has sent you emails or shared documents
- Check Google account is connected

## 📂 Project Structure
```
tivrag/
├── backend/           # FastAPI backend
│   ├── main.py       # Main application
│   ├── database.py   # Database models
│   └── google_services.py
├── frontend/         # React frontend
│   └── src/
│       ├── pages/    # Page components
│       └── api.js    # API client
└── README.md
```

## 🔐 Security Note
This is a development setup. Change `SECRET_KEY` in `backend/main.py` for production use.

## 📝 API Endpoints

### Auth
- `POST /api/signup` - Create account
- `POST /api/login` - Login
- `GET /api/me` - Get user info

### Google
- `GET /api/google/auth-url` - Get OAuth URL
- `POST /api/google/callback` - Handle callback
- `GET /api/google/status` - Check connection
- `DELETE /api/google/disconnect` - Disconnect

### Search
- `POST /api/search` - Search emails & documents
  ```json
  {
    "query": "all",
    "person": "email@example.com"
  }
  ```

## 💡 Tips
- Use full email addresses for best results
- Both Gmail and Drive are searched simultaneously
- Results are limited to 50 items each
- Tokens expire - reconnect if needed

## 🎨 Features
✅ User authentication (signup/login)
✅ Google OAuth integration
✅ Gmail search by sender
✅ Google Drive search by owner
✅ Modern, responsive UI
✅ Secure credential storage

## 🐛 Debugging

### Enable verbose logging (Backend)
```python
# In main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check browser console (Frontend)
- Press F12 to open DevTools
- Check Console tab for errors
- Check Network tab for API calls

### Test API directly
```bash
# Get auth token
curl -X POST http://localhost:8002/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}'

# Use token
curl http://localhost:8002/api/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 📧 Support
For issues, refer to the main README.md or check the application logs.

