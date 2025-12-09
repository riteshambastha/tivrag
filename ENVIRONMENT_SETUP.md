# Environment Variables Setup Guide

## Quick Setup

### Step 1: Create your `.env` file

Since `.env` files are ignored by git (for security), you need to create one locally:

```bash
# Navigate to the backend directory
cd backend

# Create a new .env file
touch .env
```

### Step 2: Add your credentials to `backend/.env`

Open `backend/.env` in your text editor and add:

```env
# Google OAuth Credentials
GOOGLE_CLIENT_ID=your-actual-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-actual-client-secret

# OpenAI API Key (optional - for AI features)
OPENAI_API_KEY=your-openai-api-key

# Application Settings (optional)
BACKEND_PORT=8002
FRONTEND_PORT=5175
```

### Step 3: Get your Google OAuth credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable these APIs:
   - Gmail API
   - Google Drive API
4. Go to **APIs & Services → Credentials**
5. Click **Create Credentials → OAuth client ID**
6. Choose **Web application**
7. Add authorized redirect URI:
   ```
   http://localhost:5175/configuration/callback
   ```
8. Click **Create**
9. Copy the **Client ID** and **Client Secret** to your `.env` file

### Step 4: Get your OpenAI API key (Optional)

1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create a new API key
3. Copy it to your `.env` file

### Step 5: Install the new dependency

```bash
cd backend
pip install python-dotenv
# Or reinstall all dependencies
pip install -r requirements.txt
```

## How It Works

The application now:
1. Looks for a `backend/.env` file when it starts
2. Loads all environment variables from that file
3. Uses `os.getenv()` to access these variables
4. Falls back to placeholder values if variables aren't set

## Security Notes

✅ **Good practices:**
- `.env` files are automatically ignored by git
- Never commit your `.env` file
- Never share your credentials publicly
- Rotate your keys if accidentally exposed

❌ **Don't:**
- Don't hardcode credentials in your code
- Don't commit `.env` files to version control
- Don't share your `.env` file with others

## File Structure

```
tivrag/
├── env.example          ← Template (safe to commit)
├── backend/
│   ├── .env            ← Your actual credentials (ignored by git)
│   ├── main.py         ← Loads .env automatically
│   └── google_services.py  ← Uses environment variables
```

## Troubleshooting

**Error: "Google services not connected"**
- Make sure `backend/.env` exists
- Verify your credentials are correct
- Check that you've enabled Gmail and Drive APIs in Google Cloud

**Error: "Module 'dotenv' not found"**
```bash
cd backend
pip install python-dotenv
```

**Want to use different credentials for different environments?**
- Development: `backend/.env`
- Production: Set environment variables in your hosting platform
- Testing: `backend/.env.test`

