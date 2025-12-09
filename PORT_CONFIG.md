# Port Configuration

This application has been configured to use custom ports:

## Configured Ports

| Service  | Port | URL |
|----------|------|-----|
| Frontend | 5175 | http://localhost:5175 |
| Backend  | 8002 | http://localhost:8002 |
| API Docs | 8002 | http://localhost:8002/docs |

## Why These Ports?

The default ports were changed because:
- Frontend default (3000/5173/5174) were already in use
- Backend default (8000/8001) were already in use

## Changed Files

The following files have been updated with the new ports:

### Backend Files
1. **backend/main.py**
   - Changed server port from 8000 → 8002
   - Updated CORS origins to include port 5175

2. **backend/google_services.py**
   - Updated OAuth redirect URI to use port 5175

### Frontend Files
3. **frontend/vite.config.js**
   - Changed dev server port from 3000 → 5175

4. **frontend/src/api.js**
   - Updated API base URL to use port 8002

### Documentation Files
5. **README.md** - All URLs updated
6. **QUICKSTART.md** - All URLs updated
7. **PROJECT_OVERVIEW.md** - All URLs updated
8. **SETUP.txt** - All URLs updated
9. **start.sh** - Launch script updated
10. **start.bat** - Launch script updated

## Google OAuth Configuration

⚠️ **IMPORTANT**: When setting up Google OAuth, you MUST use this redirect URI:

```
http://localhost:5175/configuration/callback
```

Add this exact URL to:
- Google Cloud Console → APIs & Services → Credentials
- Your OAuth 2.0 Client ID → Authorized redirect URIs

## Quick Start

### Method 1: Using Launch Script

**macOS/Linux:**
```bash
./start.sh
```

**Windows:**
```bash
start.bat
```

### Method 2: Manual Start

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python main.py
```
Backend will run on http://localhost:8002

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```
Frontend will run on http://localhost:5175

## Changing Ports Again

If you need to use different ports, update these locations:

1. **Backend Port (currently 8002)**:
   - File: `backend/main.py`
   - Line: `uvicorn.run(app, host="0.0.0.0", port=8002)`

2. **Frontend Port (currently 5175)**:
   - File: `frontend/vite.config.js`
   - Line: `port: 5175`

3. **API URL in Frontend**:
   - File: `frontend/src/api.js`
   - Line: `const API_BASE_URL = 'http://localhost:8002'`

4. **OAuth Redirect URI**:
   - File: `backend/google_services.py`
   - Line: `self.redirect_uri = "http://localhost:5175/configuration/callback"`

5. **CORS Origins**:
   - File: `backend/main.py`
   - Line: `allow_origins=["http://localhost:5175", ...]`

6. **Update Google Cloud Console**:
   - Add new redirect URI with your new frontend port

## Testing the Configuration

1. Start both servers
2. Open http://localhost:5175 in your browser
3. Sign up for a new account
4. Check that login works
5. Go to Configuration and test Google OAuth
6. Verify the redirect works properly

## Troubleshooting

### Backend won't start on 8002
- Check if port is in use: `lsof -i :8002` (Mac/Linux) or `netstat -ano | findstr :8002` (Windows)
- Kill the process or choose a different port

### Frontend won't start on 5175
- Check if port is in use: `lsof -i :5175` (Mac/Linux) or `netstat -ano | findstr :5175` (Windows)
- Kill the process or choose a different port

### OAuth redirect error
- Verify the exact redirect URI in Google Cloud Console
- It must match: `http://localhost:5175/configuration/callback`
- No trailing slash, correct port

### API connection failed
- Check backend is running: visit http://localhost:8002
- Check API docs: visit http://localhost:8002/docs
- Verify CORS settings in backend/main.py

## Environment Variables (Optional)

Instead of hardcoding ports, you can use environment variables:

```bash
# Backend
export BACKEND_PORT=8002
export GOOGLE_CLIENT_ID="your-client-id"
export GOOGLE_CLIENT_SECRET="your-client-secret"

# Frontend
export VITE_API_URL="http://localhost:8002"
export VITE_PORT=5175
```

Then modify the code to read from `os.getenv()` or `import.meta.env`.

---

**Current Configuration Summary:**
- ✅ Frontend: Port 5175
- ✅ Backend: Port 8002
- ✅ OAuth Redirect: http://localhost:5175/configuration/callback
- ✅ All documentation updated

