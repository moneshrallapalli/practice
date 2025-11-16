# 🚀 Quick Start Guide

This guide will get SentinTinel running in under 5 minutes!

## Prerequisites

Before starting, ensure you have:
- [ ] Google Gemini API key ([Get one here](https://ai.google.dev/))
- [ ] PostgreSQL installed (or use Docker)
- [ ] Python 3.9+ and Node.js 18+ (or use Docker)

## 🎯 Choose Your Method

### Option 1: Docker (Recommended - Easiest)

**Best for:** Quick setup, no local dependencies needed

```bash
# 1. Add your API key
cp backend/.env.example backend/.env
# Edit backend/.env and add your GEMINI_API_KEY

# 2. Start everything
./start-docker.sh

# 3. Open http://localhost:3000
```

**Stop:**
```bash
./stop-docker.sh
```

---

### Option 2: Native Installation

**Best for:** Development, customization

#### Linux/Mac:

```bash
# 1. Add your API key
cp backend/.env.example backend/.env
# Edit backend/.env and add your GEMINI_API_KEY

# 2. Start everything
./start.sh

# 3. Open http://localhost:3000
```

**Stop:**
```bash
./stop.sh
```

#### Windows:

```batch
REM 1. Add your API key
copy backend\.env.example backend\.env
REM Edit backend\.env and add your GEMINI_API_KEY

REM 2. Start everything
start.bat

REM 3. Open http://localhost:3000
```

**Stop:**
```batch
stop.bat
```

---

## 📝 What the Scripts Do

### Start Scripts

The start scripts will:
1. ✅ Check all prerequisites (Python, Node.js, etc.)
2. ✅ Start PostgreSQL and Redis (if needed)
3. ✅ Create virtual environment (first run only)
4. ✅ Install dependencies (first run only)
5. ✅ Initialize database (first run only)
6. ✅ Start backend server (port 8000)
7. ✅ Start frontend server (port 3000)
8. ✅ Open dashboard in your browser

### Stop Scripts

The stop scripts will:
1. ✅ Gracefully stop frontend
2. ✅ Gracefully stop backend
3. ✅ Optionally stop PostgreSQL/Redis (asks first)
4. ✅ Clean up processes

---

## 🎬 First Time Setup

### 1. Get Gemini API Key

1. Visit https://ai.google.dev/
2. Click "Get API Key"
3. Create or select a project
4. Copy your API key

### 2. Configure Environment

```bash
# Edit backend/.env
nano backend/.env  # or use any text editor

# Replace this line:
GEMINI_API_KEY=your_api_key_here

# With your actual key:
GEMINI_API_KEY=AIzaSyD...your-actual-key
```

### 3. Start the System

**Docker:**
```bash
./start-docker.sh
```

**Native:**
```bash
./start.sh  # Linux/Mac
start.bat   # Windows
```

### 4. Access Dashboard

The dashboard will automatically open at: http://localhost:3000

---

## 📹 Adding Your First Camera

### Option 1: Via Dashboard UI

1. Open http://localhost:3000
2. See sample cameras in the grid
3. Click "Start" on any camera

### Option 2: Via API

```bash
# Add webcam (camera index 0)
curl -X POST http://localhost:8000/api/cameras \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Webcam",
    "location": "Desk",
    "stream_url": "0"
  }'

# Add IP camera
curl -X POST http://localhost:8000/api/cameras \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Front Door",
    "location": "Entrance",
    "stream_url": "rtsp://user:pass@192.168.1.100:554/stream"
  }'
```

---

## 🔍 Verifying Installation

### Check Backend Health

```bash
curl http://localhost:8000/health
# Should return: {"status": "healthy"}
```

### Check API Documentation

Open: http://localhost:8000/docs

### Check Frontend

Open: http://localhost:3000

You should see:
- 🎯 Dashboard with camera grid
- 📊 Summary statistics
- 🚨 Alert panel
- 📝 Scene narration panel

---

## 🐛 Troubleshooting

### Backend won't start

```bash
# Check logs
tail -f .pids/backend.log  # Linux/Mac

# Or manually start to see errors
cd backend
source venv/bin/activate
python main.py
```

### Frontend won't start

```bash
# Check logs
tail -f .pids/frontend.log  # Linux/Mac

# Or manually start to see errors
cd frontend
npm start
```

### API Key Error

If you see Gemini API errors:
1. Verify key is correct in `backend/.env`
2. Check key is active at https://ai.google.dev/
3. Ensure no spaces or quotes around the key

### Port Already in Use

If port 8000 or 3000 is already in use:

**Find process:**
```bash
# Linux/Mac
lsof -i :8000
lsof -i :3000

# Windows
netstat -ano | findstr :8000
netstat -ano | findstr :3000
```

**Kill process or change port in config**

### Database Connection Error

```bash
# Check PostgreSQL is running
pg_isready

# If not, start it:
sudo systemctl start postgresql  # Linux
brew services start postgresql   # Mac
```

---

## 📚 Next Steps

Once the system is running:

1. **Add Cameras**: Configure your camera sources
2. **Test Alerts**: System will generate alerts based on activity
3. **View Analysis**: Watch real-time scene narration
4. **Check Patterns**: System learns patterns over time
5. **Review Stats**: Monitor system performance

---

## 🎉 Success!

If you see the dashboard at http://localhost:3000, congratulations!

SentinTinel is now running and ready to monitor your cameras with AI-powered analysis.

---

## 📖 Further Reading

- **Full Documentation**: See [README.md](README.md)
- **Detailed Setup**: See [SETUP_GUIDE.md](SETUP_GUIDE.md)
- **API Reference**: http://localhost:8000/docs (when running)

---

**Need Help?** Open an issue on GitHub or check the troubleshooting section in SETUP_GUIDE.md
