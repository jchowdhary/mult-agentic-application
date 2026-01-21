# 🏸 Multi-Agent Badminton Scheduler

A sophisticated multi-agent AI system that intelligently coordinates appointment scheduling between two people to find a common time for a badminton match.

## 🎯 Overview

This project demonstrates **multi-agent collaboration** using three different AI frameworks:
- **Groq (Llama 3.3) + A2A Protocol** (for Mr. Bean's agent)
- **CrewAI + Groq** (for Mr. Joy's agent)
- **LangGraph + Gemini** (for the Organizer agent)

The system manages 10-day appointment diaries (8 AM - 7 PM) with leisure time, meal times, and fixed appointments, then intelligently finds common 2-hour slots for a badminton match.

---

## ✨ Features

- 🤖 **3 Autonomous AI Agents** working together
- 📅 **10-day appointment diaries** for each person
- 🧠 **Intelligent scheduling** considering flexible vs fixed appointments
- 🎨 **Beautiful web interface** with real-time status
- 🔄 **Automatic coordination** between agents
- 📊 **Detailed reporting** of scheduling process
- 🏸 **2-hour badminton match** scheduling

---

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│   Web Dashboard (Streamlit)         │
│   Port 8501                          │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Organizer Agent (LangGraph)       │
│   Port 8003                          │
│   - Fetches diaries                 │
│   - Checks availability              │
│   - Selects best slot                │
│   - Books appointments               │
└──────────┬────────────────┬─────────┘
           │                │
     ┌─────▼─────┐    ┌────▼──────┐
     │ Mr. Bean  │    │ Mr. Joy   │
     │ (Gemini)  │    │ (CrewAI)  │
     │ Port 8001 │    │ Port 8002 │
     └───────────┘    └───────────┘
```

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd /home/jayant/genAICourse/multi-agent-collaboration
source multiagent/bin/activate
pip install -r requirements.txt
```

### 2. Start All Agents (4 Terminals)

**Terminal 1 - Mr. Bean:**
```bash
python agents/bean/bean_agent.py
```

**Terminal 2 - Mr. Joy:**
```bash
python agents/joy/joy_agent.py
```

**Terminal 3 - Organizer:**
```bash
python agents/organizer/organizer_agent.py
```

**Terminal 4 - Web App:**
```bash
streamlit run web_app.py
```

### 3. Open Browser
Visit: http://localhost:8501

---

## 📚 Documentation

- **[QUICK_START.md](QUICK_START.md)** - 5-minute setup guide
- **[EXECUTION_GUIDE.md](EXECUTION_GUIDE.md)** - Complete step-by-step guide
- **[API Documentation](#api-endpoints)** - Endpoint details

---

## 🎭 The Agents

### 🎩 Mr. Bean Agent
- **Framework**: Groq (Llama 3.3) + A2A Protocol
- **Port**: 8001
- **Schedule**: Work, leisure, meals, hobbies
- **Special**: Uses Groq AI to intelligently evaluate availability with A2A agent card

### 😊 Mr. Joy Agent
- **Framework**: CrewAI + Groq LLM
- **Port**: 8002  
- **Schedule**: Business meetings, gym, yoga, family time
- **Special**: Direct availability checking (Groq AI-ready)

### 🏸 Organizer Agent
- **Framework**: LangGraph
- **Port**: 8003
- **Purpose**: Coordinates between Bean and Joy
- **Special**: Multi-step workflow with AI-powered slot selection

---

## 📋 API Endpoints

### Mr. Bean Agent (8001)
```
GET  /               - Agent information
GET  /diary          - 10-day appointment diary
POST /check_availability - Check time slot availability
POST /book_appointment   - Book an appointment
```

### Mr. Joy Agent (8002)
```
GET  /               - Agent information
GET  /diary          - 10-day appointment diary
POST /check_availability - Check time slot availability
POST /book_appointment   - Book an appointment
```

### Organizer Agent (8003)
```
GET  /                   - Agent information
GET  /health             - Check all agents status
POST /schedule_badminton - Schedule badminton match
```

---

## 🧪 Testing

### Via Web Dashboard
1. Open http://localhost:8501
2. Navigate to "Schedule Match" tab
3. Click "Schedule Badminton Match"
4. View results

### Via Command Line
```bash
# Check system health
curl http://localhost:8003/health

# Schedule match
curl -X POST http://localhost:8003/schedule_badminton \
  -H "Content-Type: application/json" \
  -d '{"duration_hours": 2}'

# View diaries
curl http://localhost:8001/diary
curl http://localhost:8002/diary
```

---

## 📊 How It Works

1. **Fetch Diaries**: Organizer retrieves 10-day schedules from both agents
2. **Check Bean**: Queries Mr. Bean for available 2-hour slots
3. **Check Joy**: Queries Mr. Joy for the same time slots
4. **Find Common**: Identifies mutually available times
5. **AI Selection**: Uses Gemini to choose the optimal slot
6. **Book**: Automatically books with both agents
7. **Display**: Shows results in web dashboard

---

## 🎨 Appointment Types

- **🎮 Leisure** (Green): Can be rescheduled (hobbies, relaxation)
- **🍽️ Flexible** (Orange): Can be adjusted (meals, breaks)
- **📌 Fixed** (Red): Cannot be changed (meetings, commitments)
- **🏸 Booked** (Purple): Scheduled appointments

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Mr. Bean Agent | Groq + A2A | AI-powered schedule management |
| Mr. Joy Agent | CrewAI + Groq | Multi-agent framework |
| Organizer | LangGraph + Gemini | Workflow orchestration |
| Web Interface | Streamlit | Interactive dashboard |
| API Framework | FastAPI | REST API server |
| Server | Uvicorn | ASGI server |

---

## 📁 Project Structure

```
multi-agent-collaboration/
├── agents/
│   ├── bean/
│   │   └── bean_agent.py          # Mr. Bean agent (Gemini)
│   ├── joy/
│   │   └── joy_agent.py           # Mr. Joy agent (CrewAI)
│   └── organizer/
│       └── organizer_agent.py     # Organizer (LangGraph)
├── web_app.py                     # Streamlit dashboard
├── requirements.txt               # Python dependencies
├── .env                           # API keys
├── README.md                      # This file
├── QUICK_START.md                 # Quick setup guide
└── EXECUTION_GUIDE.md             # Detailed guide
```

---

## ⚙️ Configuration

### Environment Variables (.env)
```bash
# Required API Keys
GOOGLE_API_KEY=your_google_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here
OPENAI_API_KEY=dummy_value_required_by_crewai

# Optional Port Configuration
BEAN_AGENT_PORT=8001
JOY_AGENT_PORT=8002
ORGANIZER_AGENT_PORT=8003
WEB_APP_PORT=8501
```

**API Key Notes:**
- **GOOGLE_API_KEY**: Get from [Google AI Studio](https://makersuite.google.com/app/apikey) - Used by Organizer agent
- **GROQ_API_KEY**: Get from [Groq Console](https://console.groq.com/keys) - Used by Bean & Joy agents
- **OPENAI_API_KEY**: CrewAI requires this variable but doesn't use it. Set to any dummy value (e.g., "sk-dummy")

---

## 🔧 Customization

### Modify Schedules
Edit diary generation in:
- `agents/bean/bean_agent.py` → `generate_bean_diary()`
- `agents/joy/joy_agent.py` → `generate_joy_diary()`

### Change Time Windows
Edit organizer:
- `agents/organizer/organizer_agent.py` → `check_bean_availability()`

### Add New Agent
1. Create agent file in `agents/new_agent/`
2. Follow FastAPI pattern
3. Update organizer workflow
4. Update web dashboard

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Port in use | `lsof -ti:8001 \| xargs kill -9` |
| Module not found | `pip install --upgrade -r requirements.txt` |
| API key error | Check `.env` file |
| Agents not communicating | Restart in order: Bean → Joy → Organizer |
| Slow response | Check internet, wait patiently |

See [EXECUTION_GUIDE.md](EXECUTION_GUIDE.md) for detailed troubleshooting.

---

## 📈 Performance

- **Diary Generation**: < 1 second
- **Availability Check**: 2-5 seconds per agent
- **Full Scheduling**: 30-60 seconds
- **Web Dashboard**: Real-time updates

---

## 🎓 Learning Outcomes

This project demonstrates:
- ✅ Multi-agent system design
- ✅ Inter-agent communication
- ✅ RESTful API development
- ✅ Workflow orchestration with LangGraph
- ✅ Integration of multiple AI frameworks
- ✅ Real-time web dashboards
- ✅ Intelligent scheduling algorithms

---

## 🚧 Future Enhancements

- [ ] Add more agents (3+ people coordination)
- [ ] Support multiple activities (not just badminton)
- [ ] Variable duration slots
- [ ] Recurring appointments
- [ ] Email notifications
- [ ] Calendar integration (Google Calendar, Outlook)
- [ ] Mobile app
- [ ] Voice interface

---

## 📝 License

This project is for educational purposes.

---

## 🙏 Acknowledgments

- **Google Gemini** for powerful LLM API
- **CrewAI** for multi-agent framework
- **LangGraph** for workflow orchestration
- **Streamlit** for beautiful web interface

---

## 📞 Support

For issues or questions:
1. Check [EXECUTION_GUIDE.md](EXECUTION_GUIDE.md)
2. Review terminal logs
3. Verify all agents are running
4. Check API key configuration

---

## 🎯 Success Metrics

The system is working correctly when:
- ✅ All 4 services start without errors
- ✅ Web dashboard shows all agents online
- ✅ Scheduling completes in < 90 seconds
- ✅ Common slots are found and booked
- ✅ Both diaries show the booked appointment

---

## 🏆 Project Status

- [x] Mr. Bean Agent (Gemini) - **Complete**
- [x] Mr. Joy Agent (CrewAI) - **Complete**
- [x] Organizer Agent (LangGraph) - **Complete**
- [x] Web Dashboard (Streamlit) - **Complete**
- [x] Documentation - **Complete**
- [x] Testing - **Complete**

**Status**: ✅ **Production Ready**

---

**Made with ❤️ for multi-agent AI exploration**

**Ready to schedule? Fire up those agents! 🚀🏸**
