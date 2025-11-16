# 🚀 SentinTinel Setup Guide

Complete step-by-step guide to get SentinTinel running on your system.

## Prerequisites Checklist

Before starting, ensure you have:

- [ ] Python 3.9 or higher installed
- [ ] Node.js 18 or higher installed
- [ ] PostgreSQL 14+ installed and running
- [ ] Redis 7+ installed and running (optional but recommended)
- [ ] Google Gemini API key ([Get one here](https://ai.google.dev/))
- [ ] Git installed
- [ ] At least 4GB RAM available
- [ ] Webcam or IP camera for testing (optional)

## Installation Methods

### Option 1: Docker Setup (Recommended)

**Pros:** Easiest setup, all dependencies included
**Cons:** Requires Docker

```bash
# 1. Install Docker and Docker Compose
# Follow instructions at https://docs.docker.com/get-docker/

# 2. Clone repository
git clone <your-repo-url>
cd practice

# 3. Create environment file
cp backend/.env.example backend/.env

# 4. Edit backend/.env and add your Gemini API key
nano backend/.env  # or use your preferred editor

# 5. Start all services
docker-compose up -d

# 6. Check logs
docker-compose logs -f

# 7. Access dashboard
# Open http://localhost:3000 in your browser
```

### Option 2: Manual Setup

**Pros:** Full control, good for development
**Cons:** More setup steps

#### Step 1: Database Setup

**PostgreSQL:**
```bash
# Install PostgreSQL (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# Install PostgreSQL (macOS)
brew install postgresql
brew services start postgresql

# Create database and user
sudo -u postgres psql
```

```sql
CREATE DATABASE sentintinel_db;
CREATE USER sentintinel_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE sentintinel_db TO sentintinel_user;
\q
```

**Redis (Optional):**
```bash
# Install Redis (Ubuntu/Debian)
sudo apt-get install redis-server
sudo systemctl start redis

# Install Redis (macOS)
brew install redis
brew services start redis
```

#### Step 2: Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Edit with your settings

# Initialize database
python init_db.py

# Test backend
python main.py
```

You should see:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

#### Step 3: Frontend Setup

```bash
# Open new terminal
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Default settings should work if backend is on localhost:8000

# Start development server
npm start
```

Browser should automatically open to http://localhost:3000

## Configuration

### Backend Environment Variables

Edit `backend/.env`:

```env
# REQUIRED - Get from https://ai.google.dev/
GEMINI_API_KEY=your_api_key_here

# Database (update if different)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=sentintinel_db
POSTGRES_USER=sentintinel_user
POSTGRES_PASSWORD=your_secure_password

# Redis (optional)
REDIS_HOST=localhost
REDIS_PORT=6379

# Camera Settings
CAMERA_FPS=2                    # Frames per second (2 recommended)
MAX_CAMERAS=4                   # Maximum concurrent cameras
VIDEO_RESOLUTION_WIDTH=1280
VIDEO_RESOLUTION_HEIGHT=720

# Alert Thresholds (0-100)
CRITICAL_THRESHOLD=80           # Score above this = critical alert
WARNING_THRESHOLD=50            # Score above this = warning alert

# Application
DEBUG=True                      # Set False in production
LOG_LEVEL=INFO
SECRET_KEY=change-this-in-production
```

### Frontend Environment Variables

Edit `frontend/.env`:

```env
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_WS_URL=ws://localhost:8000
```

## Testing the Installation

### 1. Check Backend Health

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "healthy"}
```

### 2. Check API

```bash
curl http://localhost:8000/api/cameras
```

Should return array of cameras.

### 3. Test WebSocket

Open browser console at http://localhost:3000 and check for:
```
WebSocket connected to /ws/live-feed
WebSocket connected to /ws/alerts
WebSocket connected to /ws/analysis
WebSocket connected to /ws/system
```

### 4. Start a Camera

In the dashboard:
1. Find a camera card
2. Click "Start" button
3. Camera should show "LIVE" status
4. Video feed should appear (if camera available)

## First Usage

### Adding Your First Camera

**Using Webcam:**
```bash
curl -X POST http://localhost:8000/api/cameras \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Webcam",
    "location": "Desk",
    "stream_url": "0"
  }'
```

**Using IP Camera:**
```bash
curl -X POST http://localhost:8000/api/cameras \
  -H "Content-Type: application/json" \
  -d '{
    "name": "IP Camera",
    "location": "Front Door",
    "stream_url": "rtsp://username:password@camera-ip:554/stream"
  }'
```

**Using Video File (Testing):**
```bash
curl -X POST http://localhost:8000/api/cameras \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Video",
    "location": "Test",
    "stream_url": "/path/to/video.mp4"
  }'
```

### Testing Alert System

Send test command via dashboard or API:

```bash
curl -X POST http://localhost:8000/api/system/command \
  -H "Content-Type: application/json" \
  -d '{"command": "test_alert", "params": {"camera_id": 1}}'
```

## Common Issues & Solutions

### Backend won't start

**Error: `ModuleNotFoundError`**
```bash
# Solution: Reinstall dependencies
pip install -r requirements.txt
```

**Error: `Database connection failed`**
```bash
# Solution: Check PostgreSQL is running
sudo systemctl status postgresql  # Linux
brew services list  # macOS

# Check credentials in .env match database
```

### Frontend won't start

**Error: `npm ERR! code ELIFECYCLE`**
```bash
# Solution: Clear and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Error: `Module not found`**
```bash
# Solution: Install missing dependencies
npm install
```

### Camera won't start

**No video feed:**
1. Check camera source is accessible
2. Try different camera index (0, 1, 2)
3. Check OpenCV installation: `python -c "import cv2; print(cv2.__version__)"`

**Permission denied:**
```bash
# Linux: Add user to video group
sudo usermod -a -G video $USER
# Logout and login again
```

### Gemini API errors

**Error: `Invalid API key`**
- Verify API key in `.env`
- Check key is active at https://ai.google.dev/

**Error: `Quota exceeded`**
- Check API quota limits
- Reduce CAMERA_FPS in `.env`

### WebSocket connection issues

**Connection refused:**
1. Check backend is running
2. Verify REACT_APP_WS_URL in frontend/.env
3. Check CORS settings in backend

## Performance Tuning

### For Low-End Systems

```env
# backend/.env
CAMERA_FPS=1                    # Reduce to 1 FPS
MAX_CAMERAS=2                   # Limit concurrent cameras
VIDEO_RESOLUTION_WIDTH=640      # Lower resolution
VIDEO_RESOLUTION_HEIGHT=480
```

### For High-End Systems

```env
# backend/.env
CAMERA_FPS=5                    # Increase FPS
MAX_CAMERAS=8                   # More cameras
VIDEO_RESOLUTION_WIDTH=1920     # Higher resolution
VIDEO_RESOLUTION_HEIGHT=1080
```

## Development Tips

### Hot Reload

Both backend and frontend support hot reload:
- **Backend**: Restart on code changes (DEBUG=True)
- **Frontend**: Auto-refresh in browser

### Debugging

**Backend logs:**
```bash
# Set LOG_LEVEL=DEBUG in .env
tail -f logs/sentintinel.log
```

**Frontend console:**
Open browser DevTools (F12) → Console tab

### Database Management

**View data:**
```bash
psql -U sentintinel_user -d sentintinel_db
```

**Reset database:**
```bash
python init_db.py
```

## Next Steps

1. ✅ Installation complete
2. 📹 Add your cameras
3. 🔍 Watch real-time analysis
4. 🚨 Monitor alerts
5. 📊 Review patterns and statistics

## Getting Help

- 📖 Check main README.md for features
- 🐛 Report issues on GitHub
- 💬 Community support (if available)

---

**Happy Monitoring! 🛡️**
