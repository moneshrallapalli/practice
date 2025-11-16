# 🔑 API Key Setup Guide - Google Gemini

This guide will walk you through getting your Google Gemini API key and configuring it for SentinTinel.

## 📋 What You Need

- A Google account (Gmail)
- 5 minutes of your time

---

## 🎯 Step-by-Step: Get Your Gemini API Key

### Step 1: Visit Google AI Studio

Open your browser and go to: **https://ai.google.dev/**

Or directly to: **https://aistudio.google.com/app/apikey**

### Step 2: Sign In

1. Click **"Get API key"** or **"Sign in"** in the top right
2. Sign in with your Google account
3. You may need to accept Terms of Service

### Step 3: Create API Key

Once signed in, you'll see the API Key page:

1. Click the **"Get API key"** button (blue button)
2. You'll see a dialog with two options:
   - **"Create API key in new project"** ← Choose this if first time
   - **"Create API key in existing project"** ← If you have a Google Cloud project

3. Click **"Create API key in new project"**

### Step 4: Copy Your API Key

1. A new API key will be generated
2. It looks like: `AIzaSyD...` (starts with `AIzaSy`)
3. Click the **"Copy"** button (📋 icon)
4. **IMPORTANT**: Save this somewhere safe! You won't see it again.

Example API key format:
```
AIzaSyDXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### Step 5: (Optional) Secure Your API Key

For better security:

1. Click on your API key in the list
2. Set restrictions:
   - **Application restrictions**: None (for development)
   - **API restrictions**: Restrict to Gemini API only
3. Click **"Save"**

---

## ⚙️ Step-by-Step: Configure SentinTinel

### For Linux/Mac:

**Method 1: Using Terminal**

```bash
# 1. Navigate to project directory
cd /path/to/practice

# 2. Copy the example .env file
cp backend/.env.example backend/.env

# 3. Edit the .env file
nano backend/.env
# or
vim backend/.env
# or
code backend/.env  # if using VS Code
```

**Method 2: Using File Manager**

1. Open your file manager
2. Navigate to: `practice/backend/`
3. Copy `.env.example` and rename it to `.env`
4. Open `.env` with a text editor
5. Find this line:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```
6. Replace `your_api_key_here` with your actual API key:
   ```
   GEMINI_API_KEY=AIzaSyDXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   ```
7. Save the file

### For Windows:

**Method 1: Using Command Prompt**

```batch
REM 1. Navigate to project directory
cd C:\path\to\practice

REM 2. Copy the example .env file
copy backend\.env.example backend\.env

REM 3. Edit the .env file
notepad backend\.env
```

**Method 2: Using File Explorer**

1. Open File Explorer
2. Navigate to: `practice\backend\`
3. Copy `.env.example` and rename it to `.env`
4. Open `.env` with Notepad or your preferred text editor
5. Find this line:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```
6. Replace `your_api_key_here` with your actual API key:
   ```
   GEMINI_API_KEY=AIzaSyDXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   ```
7. Save the file

---

## ✅ Verify Your Configuration

### Check 1: File Exists

Make sure the `.env` file exists in the correct location:

**Linux/Mac:**
```bash
ls -la backend/.env
```

**Windows:**
```batch
dir backend\.env
```

You should see the file listed.

### Check 2: API Key is Set

**Linux/Mac:**
```bash
grep GEMINI_API_KEY backend/.env
```

**Windows:**
```batch
findstr GEMINI_API_KEY backend\.env
```

You should see something like:
```
GEMINI_API_KEY=AIzaSyDXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### Check 3: No Placeholder Text

Make sure you replaced the placeholder text. These are WRONG:
```bash
❌ GEMINI_API_KEY=your_api_key_here
❌ GEMINI_API_KEY=your_gemini_api_key_here
❌ GEMINI_API_KEY=
❌ GEMINI_API_KEY="AIzaSy..."  # Don't use quotes
```

This is CORRECT:
```bash
✅ GEMINI_API_KEY=AIzaSyDXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

---

## 🚀 Test Your API Key

### Method 1: Quick Python Test

Create a test file to verify your API key works:

**Linux/Mac:**
```bash
cd backend
python3 << 'EOF'
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment
load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
    print("❌ API key not found in .env file")
    exit(1)

if api_key.startswith('your_'):
    print("❌ API key not configured (still has placeholder)")
    exit(1)

print(f"✅ API key found: {api_key[:20]}...")

# Test the key
try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Say hello")
    print("✅ API key is valid and working!")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"❌ API key test failed: {e}")
EOF
```

**Windows:**
```batch
cd backend
python test_api_key.py
```

Create `test_api_key.py`:
```python
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment
load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
    print("❌ API key not found in .env file")
    exit(1)

if api_key.startswith('your_'):
    print("❌ API key not configured (still has placeholder)")
    exit(1)

print(f"✅ API key found: {api_key[:20]}...")

# Test the key
try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Say hello")
    print("✅ API key is valid and working!")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"❌ API key test failed: {e}")
```

### Method 2: Start the Application

Just try starting SentinTinel:

**Linux/Mac:**
```bash
./start.sh
```

**Windows:**
```batch
start.bat
```

If you see errors about invalid API key, check the troubleshooting section below.

---

## 🐛 Troubleshooting

### Error: "API key not valid"

**Symptoms:**
- Error message: `Invalid API key`
- Error message: `API key not found`

**Solutions:**

1. **Check the API key format**
   - Should start with `AIzaSy`
   - Should be about 39 characters long
   - No spaces before or after
   - No quotes around it

2. **Verify it's in the right file**
   ```bash
   # Make sure .env exists (not .env.example)
   ls -la backend/.env
   ```

3. **Check for hidden characters**
   - Re-copy the API key from Google AI Studio
   - Delete the old line completely
   - Paste the new key

4. **Regenerate the API key**
   - Go back to https://aistudio.google.com/app/apikey
   - Delete the old key
   - Create a new one
   - Update your `.env` file

### Error: "API key quota exceeded"

**Symptoms:**
- Error message: `Quota exceeded`
- Error message: `Rate limit reached`

**Solutions:**

1. **Check your quota**
   - Visit https://aistudio.google.com/app/apikey
   - Check usage limits

2. **Wait and retry**
   - Free tier has rate limits
   - Wait a few minutes and try again

3. **Reduce FPS**
   - Edit `backend/.env`
   - Change `CAMERA_FPS=2` to `CAMERA_FPS=1`

### Error: File not found (.env)

**Symptoms:**
- Error message: `.env file not found`
- Application won't start

**Solutions:**

1. **Make sure .env exists**
   ```bash
   # Create from template
   cp backend/.env.example backend/.env
   ```

2. **Check you're in the right directory**
   ```bash
   # Should be in project root
   pwd
   # Should show: /path/to/practice
   ```

3. **Verify file name**
   - File should be named `.env` (with a dot at the start)
   - NOT `env.txt` or `.env.txt`
   - NOT `.env.example`

### API Key in Wrong Format

**Wrong formats:**
```bash
❌ GEMINI_API_KEY="AIzaSy..."      # Don't use quotes
❌ GEMINI_API_KEY='AIzaSy...'      # Don't use quotes
❌ GEMINI_API_KEY = AIzaSy...      # No spaces around =
❌ export GEMINI_API_KEY=AIzaSy... # Don't use export
```

**Correct format:**
```bash
✅ GEMINI_API_KEY=AIzaSyDXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

---

## 🔒 Security Best Practices

### DO:
- ✅ Keep your API key private
- ✅ Add `.env` to `.gitignore` (already done)
- ✅ Use environment variables
- ✅ Regenerate key if exposed
- ✅ Set API restrictions in Google Cloud Console

### DON'T:
- ❌ Commit `.env` to git
- ❌ Share your API key publicly
- ❌ Hardcode API key in source code
- ❌ Upload to GitHub, pastebin, etc.
- ❌ Email or message API keys

---

## 📚 Additional Resources

### Official Documentation:
- **Google AI Studio**: https://ai.google.dev/
- **Gemini API Docs**: https://ai.google.dev/docs
- **API Key Management**: https://aistudio.google.com/app/apikey

### Getting Help:
- **Gemini API Issues**: https://github.com/google/generative-ai-python/issues
- **SentinTinel Issues**: [Your GitHub Issues Page]

---

## 🎉 You're Done!

If your API key is configured correctly, you should be able to:

1. Start SentinTinel with `./start.sh` or `start.bat`
2. See the dashboard at http://localhost:3000
3. Start a camera and see AI analysis in real-time

**Happy Monitoring!** 🛡️

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────┐
│  QUICK REFERENCE: API KEY SETUP                 │
├─────────────────────────────────────────────────┤
│                                                 │
│  1. Get API Key:                                │
│     https://aistudio.google.com/app/apikey      │
│                                                 │
│  2. Copy .env file:                             │
│     cp backend/.env.example backend/.env        │
│                                                 │
│  3. Edit .env file:                             │
│     nano backend/.env                           │
│                                                 │
│  4. Add your key:                               │
│     GEMINI_API_KEY=AIzaSy...                    │
│                                                 │
│  5. Start application:                          │
│     ./start.sh                                  │
│                                                 │
└─────────────────────────────────────────────────┘
```
