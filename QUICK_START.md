# 🚀 Multi-Agent Badminton Scheduler - Quick Start Guide

## 📋 Overview

This system uses 3 AI agents to schedule a badminton match between Mr. Bean and Mr. Joy:

1. **Mr. Bean Agent** (Google Gemini) - Port 8001
2. **Mr. Joy Agent** (CrewAI) - Port 8002  
3. **Organizer Agent** (LangGraph) - Port 8003
4. **Web Dashboard** (Streamlit) - Port 8501

---

## ⚡ Quick Setup (5 Minutes)

### Step 1: Activate Virtual Environment
```bash
cd /home/jayant/genAICourse/multi-agent-collaboration
source multiagent/bin/activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Verify API Key
```bash
# Already configured in .env file
cat .env
```

---

## 🎯 Running the System

### Option A: All-in-One Launch (Recommended)

Open **4 separate terminals** and run:

**Terminal 1 - Mr. Bean Agent:**
```bash
cd /home/jayant/genAICourse/multi-agent-collaboration
source multiagent/bin/activate
python agents/bean/bean_agent.py
```

**Terminal 2 - Mr. Joy Agent:**
```bash
cd /home/jayant/genAICourse/multi-agent-collaboration
source multiagent/bin/activate
python agents/joy/joy_agent.py
```

**Terminal 3 - Organizer Agent:**
```bash
cd /home/jayant/genAICourse/multi-agent-collaboration
source multiagent/bin/activate
python agents/organizer/organizer_agent.py
```

**Terminal 4 - Web Dashboard:**
```bash
cd /home/jayant/genAICourse/multi-agent-collaboration
source multiagent/bin/activate
streamlit run web_app.py
```

---

## 🌐 Access the System

Once all agents are running:

- **Web Dashboard**: http://localhost:8501
- **Mr. Bean API**: http://localhost:8001
- **Mr. Joy API**: http://localhost:8002
- **Organizer API**: http://localhost:8003

---

## 🧪 Testing the System

### Method 1: Use the Web Dashboard
1. Open http://localhost:8501
2. Click "Schedule Badminton Match"
3. Watch the magic happen!

### Method 2: Use API Directly
```bash
# Check system health
curl http://localhost:8003/health

# Schedule badminton match
curl -X POST http://localhost:8003/schedule_badminton \
  -H "Content-Type: application/json" \
  -d '{"duration_hours": 2}'
```

### Method 3: View Individual Diaries
```bash
# Mr. Bean's diary
curl http://localhost:8001/diary

# Mr. Joy's diary
curl http://localhost:8002/diary
```

---

## 📊 What Happens?

1. **Organizer Agent** fetches both diaries (10 days each)
2. Checks **Mr. Bean's** availability for 2-hour slots
3. Checks **Mr. Joy's** availability for same slots
4. Finds **common available times**
5. Uses **AI** to select the best slot
6. Books appointment with **both agents**
7. Displays result in **web dashboard**

---

## 🎨 Features

### Mr. Bean Agent (Google Gemini)
- ✅ 10-day diary (8 AM - 7 PM)
- ✅ Leisure activities (flexible)
- ✅ Fixed appointments
- ✅ Meal times
- ✅ AI-powered availability checking

### Mr. Joy Agent (CrewAI)
- ✅ 10-day diary (8 AM - 7 PM)
- ✅ Yoga & gym time (leisure)
- ✅ Business meetings (fixed)
- ✅ Meal times
- ✅ CrewAI intelligent scheduling

### Organizer Agent (LangGraph)
- ✅ Multi-agent coordination
- ✅ Workflow orchestration
- ✅ Optimal slot selection
- ✅ Automatic booking

---

## 🛠️ Troubleshooting

### Problem: Port already in use
```bash
# Find and kill process
lsof -ti:8001 | xargs kill -9  # Bean
lsof -ti:8002 | xargs kill -9  # Joy
lsof -ti:8003 | xargs kill -9  # Organizer
```

### Problem: Module not found
```bash
pip install --upgrade -r requirements.txt
```

### Problem: API key error
```bash
# Check .env file
cat .env
# Should show: GOOGLE_API_KEY=AIzaSyCNY3spvq84_n_-FRuAx2creU8BXoZrAnc
```

---

## 📁 Project Structure

```
multi-agent-collaboration/
├── agents/
│   ├── bean/bean_agent.py       # Mr. Bean (Gemini)
│   ├── joy/joy_agent.py         # Mr. Joy (CrewAI)
│   └── organizer/organizer_agent.py  # Organizer (LangGraph)
├── web_app.py                   # Streamlit dashboard
├── requirements.txt             # Dependencies
├── .env                         # API keys
└── QUICK_START.md              # This file
```

---

## 🎯 Next Steps

1. **Explore Diaries**: Visit agent endpoints to see schedules
2. **Schedule Match**: Use web dashboard to coordinate
3. **Check Results**: View booked appointments
4. **Customize**: Modify schedules in agent code

---

## 💡 Tips

- Agents must be running BEFORE using Organizer
- Web dashboard shows real-time status
- Each agent runs independently
- Leisure/flexible times can be rescheduled
- Fixed appointments cannot be changed

---

**Happy Scheduling! 🏸**
