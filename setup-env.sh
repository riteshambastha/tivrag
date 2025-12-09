#!/bin/bash

# Tivrag Environment Setup Script
# This script helps you set up your .env file with credentials

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║         Tivrag Environment Variables Setup                   ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if .env already exists
if [ -f "backend/.env" ]; then
    echo "⚠️  backend/.env already exists!"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup cancelled. Your existing .env file was not modified."
        exit 0
    fi
fi

echo ""
echo "Please enter your credentials (or press Enter to skip):"
echo ""

# Get Google Client ID
echo "📝 Google OAuth Client ID"
echo "   Get it from: https://console.cloud.google.com/apis/credentials"
read -p "   Enter Client ID: " GOOGLE_CLIENT_ID

# Get Google Client Secret
echo ""
echo "📝 Google OAuth Client Secret"
read -p "   Enter Client Secret: " GOOGLE_CLIENT_SECRET

# Get OpenAI API Key
echo ""
echo "📝 OpenAI API Key (optional - for AI features)"
echo "   Get it from: https://platform.openai.com/api-keys"
read -p "   Enter API Key (or press Enter to skip): " OPENAI_API_KEY

# Create backend directory if it doesn't exist
mkdir -p backend

# Create .env file
cat > backend/.env << EOF
# Google OAuth Credentials
# Get these from: https://console.cloud.google.com/apis/credentials
GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID:-YOUR_GOOGLE_CLIENT_ID}
GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET:-YOUR_GOOGLE_CLIENT_SECRET}

# OpenAI API Key (for AI analysis features)
# Get this from: https://platform.openai.com/api-keys
OPENAI_API_KEY=${OPENAI_API_KEY:-YOUR_OPENAI_API_KEY}

# Application Settings
BACKEND_PORT=8002
FRONTEND_PORT=5175
EOF

echo ""
echo "✅ Created backend/.env file successfully!"
echo ""
echo "Next steps:"
echo "  1. Review backend/.env and update any placeholders"
echo "  2. Make sure you've enabled Gmail and Drive APIs in Google Cloud"
echo "  3. Run: cd backend && pip install -r requirements.txt"
echo "  4. Start the application: ./start.sh"
echo ""
echo "📚 For more details, see ENVIRONMENT_SETUP.md"
echo ""

