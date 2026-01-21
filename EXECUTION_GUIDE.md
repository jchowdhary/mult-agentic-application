# 🎯 Multi-Agent Badminton Scheduler - Complete Execution Guide

## 📖 Table of Contents
1. [System Overview](#system-overview)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Running the System](#running-the-system)
5. [Testing the System](#testing-the-system)
6. [Understanding the Output](#understanding-the-output)
7. [Troubleshooting](#troubleshooting)
8. [Architecture Details](#architecture-details)

---

## 📋 System Overview

This is a **multi-agent AI system** that coordinates appointment scheduling between two people (Mr. Bean and Mr. Joy) to find a common time for a 2-hour badminton match.

### Components:

1. **Mr. Bean Agent** (Port 8001)
   - Framework: Google Gemini API
   - Purpose: Manages Mr. Bean's 10-day diary
   - Features: Leisure time, meal times, work schedules

2. **Mr. Joy Agent** (Port 8002)
   - Framework: CrewAI
   - Purpose: Manages Mr. Joy's 10-day diary
   - Features: Gym sessions, business meetings, wellness activities

3. **Organizer Agent** (Port 8003)
   - Framework: LangGraph
   - Purpose: Coordinates between Bean and Joy agents
   - Features: Multi-step workflow, AI-powered slot selection

4. **Web Dashboard** (Port 8501)
   - Framework: Streamlit
   - Purpose: Visual interface to interact with all agents
   - Features: Real-time status, schedule viewing, match scheduling

---

## 🔧 Prerequisites

### System Requirements:
- **OS**: Linux (Zorin OS) ✅
- **Python**: 3.11.11 ✅
- **RAM**: Minimum 2GB
- **Internet**: Required for API calls

### API Requirements:
- Google API Key (Gemini) ✅ Already configured

---

## 📦 Installation

### Step 1: Navigate to Project Directory
```bash
cd /home/jayant/genAICourse/multi-agent-collaboration
```

### Step 2: Activate Virtual Environment
```bash
source multiagent/bin/activate
```

You should see `(multiagent)` in your terminal prompt.

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

This will install:
- google-generativeai (for Mr. Bean)
- crewai (for Mr. Joy)
- langgraph (for Organizer)
- streamlit (for Web Dashboard)
- fastapi & uvicorn (for API servers)
- And all other dependencies

**Installation time**: ~2-5 minutes depending on internet speed.

### Step 4: Verify Installation
```bash
python -c "import google.generativeai, crewai, langgraph, streamlit; print('✅ All packages installed')"
```

### Step 5: Verify API Key
```bash
cat .env
```

Should show:
```
GOOGLE_API_KEY=AIzaSyCNY3spvq84_n_-FRuAx2creU8BXoZrAnc
```

---

## 🚀 Running the System

You need to open **4 separate terminal windows** (or use tmux/screen).

### Terminal 1: Start Mr. Bean Agent

```bash
cd /home/jayant/genAICourse/multi-agent-collaboration
source multiagent/bin/activate
python agents/bean/bean_agent.py
```

**Expected Output:**
```
🎩 Starting Mr. Bean Agent on port 8001...
📅 Managing diary for next 10 days from 2026-01-21 to 2026-01-30
INFO:     Started server process [XXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8001
```

**Leave this terminal running!**

---

### Terminal 2: Start Mr. Joy Agent

```bash
cd /home/jayant/genAICourse/multi-agent-collaboration
source multiagent/bin/activate
python agents/joy/joy_agent.py
```

**Expected Output:**
```
😊 Starting Mr. Joy Agent (CrewAI) on port 8002...
📅 Managing diary for next 10 days from 2026-01-21 to 2026-01-30
INFO:     Started server process [XXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8002
```

**Leave this terminal running!**

---

### Terminal 3: Start Organizer Agent

```bash
cd /home/jayant/genAICourse/multi-agent-collaboration
source multiagent/bin/activate
python agents/organizer/organizer_agent.py
```

**Expected Output:**
```
🏸 Starting Organizer Agent (LangGraph) on port 8003...
💡 Coordinates badminton match scheduling between Bean and Joy
INFO:     Started server process [XXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8003
```

**Leave this terminal running!**

---

### Terminal 4: Start Web Dashboard

```bash
cd /home/jayant/genAICourse/multi-agent-collaboration
source multiagent/bin/activate
streamlit run web_app.py
```

**Expected Output:**
```
You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

**A browser window should automatically open!**

---

## 🧪 Testing the System

### Method 1: Using Web Dashboard (Recommended)

1. **Open Browser**: http://localhost:8501

2. **Check System Status**:
   - Sidebar should show all agents as 🟢 Online
   - If any agent is 🔴 Offline, go back and start it

3. **View Schedules**:
   - Click on **"📅 Schedules"** tab
   - See Mr. Bean's and Mr. Joy's diaries side-by-side
   - Color codes:
     - 🎮 Green = Leisure (can reschedule)
     - 🍽️ Orange = Flexible (meal times)
     - 📌 Red = Fixed (cannot change)

4. **Schedule Badminton Match**:
   - Click on **"🏸 Schedule Match"** tab
   - Click **"🚀 Schedule Badminton Match"** button
   - Wait 30-60 seconds for processing
   - See results with:
     - Selected date and time
     - Number of common slots found
     - Process log

5. **View Results**:
   - Click on **"📊 Results"** tab
   - See detailed scheduling results
   - Download results as JSON

---

### Method 2: Using Command Line (API Testing)

#### Test Individual Agents:

**Mr. Bean's Diary:**
```bash
curl http://localhost:8001/diary | python -m json.tool
```

**Mr. Joy's Diary:**
```bash
curl http://localhost:8002/diary | python -m json.tool
```

**System Health Check:**
```bash
curl http://localhost:8003/health | python -m json.tool
```

#### Schedule Badminton Match:
```bash
curl -X POST http://localhost:8003/schedule_badminton \
  -H "Content-Type: application/json" \
  -d '{"duration_hours": 2}' | python -m json.tool
```

**Expected Response:**
```json
{
  "organizer": "LangGraph Agent",
  "status": "booked",
  "selected_slot": {
    "date": "2026-01-23",
    "start_time": "16:00",
    "end_time": "18:00"
  },
  "common_slots_found": 5,
  "bean_available_slots": 12,
  "joy_available_slots": 10,
  "messages": [
    "✅ Fetched diaries for 10 days",
    "✅ Mr. Bean available for 12 slots",
    "✅ Mr. Joy available for 10 slots",
    "🎉 Found 5 common available slots",
    "✨ Selected slot: {...}",
    "✅ Booked with Mr. Bean: booked",
    "✅ Booked with Mr. Joy: booked"
  ]
}
```

---

## 📊 Understanding the Output

### Agent Diaries Structure:

Each agent has a 10-day diary with appointments from 8 AM to 7 PM:

```json
{
  "2026-01-21": {
    "date": "2026-01-21",
    "day": "Tuesday",
    "appointments": [
      {
        "time": "08:00-09:00",
        "activity": "Breakfast with Teddy",
        "type": "flexible"
      },
      {
        "time": "10:00-12:00",
        "activity": "Work at office",
        "type": "fixed"
      }
    ]
  }
}
```

### Appointment Types:

- **`leisure`**: Activities like hobbies, relaxation (CAN be rescheduled)
- **`flexible`**: Meal times, breaks (CAN be adjusted)
- **`fixed`**: Important meetings, commitments (CANNOT change)
- **`booked`**: Newly scheduled appointments

### Scheduling Process:

1. **Fetch Diaries**: Gets 10-day schedules from both agents
2. **Check Bean**: Queries Mr. Bean for available 2-hour slots
3. **Check Joy**: Queries Mr. Joy for the same slots
4. **Find Common**: Identifies mutually available times
5. **Select Best**: AI chooses optimal slot (considers time of day, day of week)
6. **Book**: Automatically books with both agents

---

## 🔍 Troubleshooting

### Problem 1: Port Already in Use

**Error**: `Address already in use`

**Solution**:
```bash
# Find and kill the process
lsof -ti:8001 | xargs kill -9  # For Bean agent
lsof -ti:8002 | xargs kill -9  # For Joy agent
lsof -ti:8003 | xargs kill -9  # For Organizer
lsof -ti:8501 | xargs kill -9  # For Streamlit
```

Then restart the agent.

---

### Problem 2: Module Not Found

**Error**: `ModuleNotFoundError: No module named 'xxx'`

**Solution**:
```bash
# Make sure venv is activated
source multiagent/bin/activate

# Reinstall requirements
pip install --upgrade -r requirements.txt
```

---

### Problem 3: API Key Error

**Error**: `Invalid API key` or `GOOGLE_API_KEY not found`

**Solution**:
```bash
# Check .env file
cat .env

# Should show:
# GOOGLE_API_KEY=AIzaSyCNY3spvq84_n_-FRuAx2creU8BXoZrAnc

# If missing, recreate it:
echo "GOOGLE_API_KEY=AIzaSyCNY3spvq84_n_-FRuAx2creU8BXoZrAnc" > .env
```

---

### Problem 4: Agents Not Communicating

**Symptoms**: Organizer can't reach Bean/Joy agents

**Solution**:
1. Verify all agents are running (check all 4 terminals)
2. Check system health:
   ```bash
   curl http://localhost:8003/health
   ```
3. Restart agents in order: Bean → Joy → Organizer → Web

---

### Problem 5: Slow Response

**Symptoms**: Scheduling takes > 2 minutes

**Causes**:
- Internet connection slow
- API rate limiting
- Too many requests

**Solution**:
- Wait patiently (AI processing takes time)
- Check internet connection
- Restart agents if hanging

---

### Problem 6: No Common Slots Found

**Symptoms**: `common_slots_found: 0`

**Explanation**: This is actually working correctly! It means both agents are genuinely busy during all checked times.

**Solution**:
- Run again (diaries refresh daily)
- Modify agent schedules in code if needed
- Check more days by editing organizer code

---

## 🏗️ Architecture Details

### Agent Communication Flow:

```
Web Dashboard (Streamlit)
        ↓
Organizer Agent (LangGraph)
    ↙         ↘
Bean Agent    Joy Agent
(Gemini)      (CrewAI)
```

### API Endpoints:

**Mr. Bean Agent (8001)**:
- `GET /` - Agent info
- `GET /diary` - Full 10-day diary
- `POST /check_availability` - Check specific time slot
- `POST /book_appointment` - Book appointment

**Mr. Joy Agent (8002)**:
- Same endpoints as Bean Agent
- Uses CrewAI for intelligent responses

**Organizer Agent (8003)**:
- `GET /` - Agent info
- `GET /health` - Check all agents status
- `POST /schedule_badminton` - Main scheduling workflow

---

## 🎯 Advanced Usage

### Customizing Schedules:

Edit the diary generation functions in:
- `agents/bean/bean_agent.py` - Function `generate_bean_diary()`
- `agents/joy/joy_agent.py` - Function `generate_joy_diary()`

### Changing Time Windows:

Edit the organizer agent:
- `agents/organizer/organizer_agent.py` - Function `check_bean_availability()`

### Adding More Agents:

1. Create new agent file in `agents/`
2. Follow same FastAPI pattern
3. Update organizer to include new agent
4. Update web dashboard

---

## 📝 Logging & Debugging

### View Agent Logs:

Logs are displayed in the terminal where each agent is running.

**Enable verbose logging** in any agent:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Debug Mode:

In each agent file, set:
```python
uvicorn.run(app, host="0.0.0.0", port=port, log_level="debug")
```

---

## 🛑 Stopping the System

To stop all agents:

1. **Stop Web Dashboard**: Press `Ctrl+C` in Terminal 4
2. **Stop Organizer**: Press `Ctrl+C` in Terminal 3
3. **Stop Mr. Joy**: Press `Ctrl+C` in Terminal 2
4. **Stop Mr. Bean**: Press `Ctrl+C` in Terminal 1

Or kill all at once:
```bash
lsof -ti:8001,8002,8003,8501 | xargs kill -9
```

---

## 🎉 Success Indicators

You'll know the system is working when:

✅ All 4 terminals show "Started server" or "Uvicorn running"  
✅ Web dashboard shows all agents as 🟢 Online  
✅ You can view both diaries in the Schedules tab  
✅ Scheduling process completes and shows a booked time  
✅ Results tab displays the scheduled badminton match

---

## 📞 Support

If you encounter issues not covered here:

1. Check all terminals for error messages
2. Verify API key is correct
3. Ensure all ports (8001-8003, 8501) are free
4. Restart system completely
5. Check internet connection

---

## 🏆 Next Steps

After successfully running the system:

1. **Experiment**: Try scheduling multiple times
2. **Customize**: Modify agent schedules
3. **Extend**: Add new types of appointments
4. **Learn**: Study how agents communicate
5. **Build**: Create your own multi-agent system!

---

**Congratulations! Your multi-agent system is ready! 🚀🏸**
