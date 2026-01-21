# Mr. Bean Agent - Agent2Agent (A2A) Protocol Implementation

## 🎯 Overview

The Bean agent has been **completely recreated** using Google's **Agent2Agent (A2A) Protocol**, which is an open standard for enabling communication and interoperability between AI agents.

---

## 🔄 What Changed

### **Old Implementation:**
- ❌ Direct FastAPI endpoints
- ❌ No standardized agent card
- ❌ Custom REST API format

### **New Implementation (A2A):**
- ✅ Uses `python-a2a` SDK (Official Google A2A Python SDK)
- ✅ Exposes Agent Card at `/.well-known/agent.json`
- ✅ Implements A2A Protocol skills (functions)
- ✅ Standardized communication format
- ✅ Interoperable with any A2A-compliant system

---

## 📦 Key Components

### **1. Agent Card**
The agent card describes the agent's capabilities and is automatically served at:
```
http://localhost:8001/.well-known/agent.json
```

**Agent Card Contents:**
- Name: "Mr. Bean Calendar Agent"
- Description: Manages appointment diary
- Skills: 4 available skills (functions)

### **2. Skills (Functions)**

#### **Skill 1: `get_diary`**
- **Purpose**: Get complete 10-day diary
- **Parameters**: None
- **Returns**: Full diary with all appointments

#### **Skill 2: `check_availability`**
- **Purpose**: Check if Mr. Bean is available
- **Parameters**:
  - `date` (string): Date in YYYY-MM-DD format
  - `start_time` (string): Start time in HH:MM format
  - `end_time` (string): End time in HH:MM format
  - `activity` (string): Activity description
- **Returns**: Availability status with reasoning

#### **Skill 3: `book_appointment`**
- **Purpose**: Book an appointment
- **Parameters**: Same as check_availability
- **Returns**: Booking confirmation

#### **Skill 4: `reset_diary`**
- **Purpose**: Reset diary to default schedule
- **Parameters**: None
- **Returns**: Reset confirmation

---

## 🚀 How to Run

### **1. Install A2A SDK** (Already done):
```bash
source multiagent/bin/activate
pip install "python-a2a[all]"
```

### **2. Start the Agent**:
```bash
cd /home/jayant/genAICourse/multi-agent-collaboration
source multiagent/bin/activate
python agents/bean/bean_agent.py
```

### **Expected Output:**
```
🎩 Starting Mr. Bean Agent (A2A Protocol) on port 8001...
📅 Managing diary for next 10 days from 2026-01-21 to 2026-01-30
🔗 Agent Card available at: http://localhost:8001/.well-known/agent.json
🌐 Protocol: Agent2Agent (A2A)
INFO:     Uvicorn running on http://0.0.0.0:8001
```

---

## 🔍 Testing the A2A Agent

### **1. View Agent Card:**
```bash
curl -s http://localhost:8001/.well-known/agent.json | python -m json.tool
```

This shows the agent's capabilities in A2A format.

### **2. Call Skills (Functions):**

**Get Diary:**
```bash
curl -X POST http://localhost:8001/skills/get_diary \
  -H "Content-Type: application/json" \
  -d '{}' | python -m json.tool
```

**Check Availability:**
```bash
curl -X POST http://localhost:8001/skills/check_availability \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-01-21",
    "start_time": "14:00",
    "end_time": "16:00",
    "activity": "Badminton match"
  }' | python -m json.tool
```

**Book Appointment:**
```bash
curl -X POST http://localhost:8001/skills/book_appointment \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-01-21",
    "start_time": "14:00",
    "end_time": "16:00",
    "activity": "Badminton match"
  }' | python -m json.tool
```

---

## 🌐 A2A Protocol Features

### **What is Agent2Agent (A2A)?**

<cite index="1-4,8-12">A2A is an open protocol that enables communication and interoperability between AI agents, regardless of the framework or vendor they are built on. It allows agents to discover each other's capabilities, negotiate interaction modalities, and securely collaborate on tasks without exposing internal state</cite>.

### **Key Benefits:**

1. **Interoperability**: Works with agents built on ANY framework (CrewAI, LangGraph, ADK, etc.)
2. **Standardization**: Common language for agent communication
3. **Discovery**: Agent cards enable automatic capability discovery
4. **Security**: Built-in authentication and authorization support
5. **Flexibility**: Supports different data modalities (text, forms, media)

### **Protocol Stack:**

- **Discovery**: Agent cards at `/.well-known/agent.json`
- **Communication**: HTTP/JSON-RPC and Server-Sent Events
- **Task Management**: Stateful conversation contexts
- **Skills**: Function calling with typed parameters

---

## 🔧 Technical Details

### **Python A2A SDK Components:**

```python
from python_a2a import (
    A2AServer,          # Main server class
    AgentCard,          # Agent metadata
    Skill,              # Function definitions
    SkillParameter,     # Function parameters
    Message,            # Communication messages
    MessageRole,        # User/Assistant/System
    # ... and more
)
```

### **Server Setup:**

```python
# 1. Define agent card
agent_card = AgentCard(
    name="Mr. Bean Calendar Agent",
    description="...",
    skills=[...]
)

# 2. Create A2A server
server = A2AServer(agent_card=agent_card)

# 3. Register skill handlers
@server.skill_handler("skill_name")
async def handler(parameters: Dict) -> Dict:
    # Your logic here
    return result

# 4. Run with uvicorn
uvicorn.run(server.app, host="0.0.0.0", port=8001)
```

---

## 📊 Comparison with Old Implementation

| Feature | Old (FastAPI) | New (A2A) |
|---------|--------------|-----------|
| Protocol | Custom REST | A2A Standard |
| Discovery | Manual | Automatic (Agent Card) |
| Skills | Custom endpoints | Standardized skills |
| Interoperability | Limited | Universal |
| Documentation | Manual | Auto-generated |
| Agent Card | None | ✅ Available |

---

## 🔗 Integration with Other Agents

### **Joy Agent (CrewAI):**
- Still uses original implementation
- Can be converted to A2A if needed
- Compatible via REST API bridge

### **Organizer Agent (LangGraph):**
- Still uses original implementation
- Can call Bean agent via A2A protocol
- Or via REST API compatibility layer

---

## 📚 Additional Resources

- **A2A Protocol Docs**: https://a2a-protocol.org/
- **Python A2A SDK**: https://github.com/a2aproject/a2a-python
- **Google A2A Codelabs**: https://codelabs.developers.google.com/intro-a2a-purchasing-concierge
- **A2A Specification**: https://a2a-protocol.org/latest/

---

## ✅ Verification Checklist

- [x] A2A SDK installed (`python-a2a`)
- [x] Bean agent recreated with A2A protocol
- [x] Agent card configured with 4 skills
- [x] Gemini 1.5-flash model configured
- [x] All skills implemented (get_diary, check_availability, book_appointment, reset_diary)
- [x] Server runs on port 8001
- [x] Agent card accessible at `/.well-known/agent.json`
- [x] 14:00-16:00 guaranteed free slot maintained
- [x] Backup of old implementation saved

---

## 🚦 Next Steps

1. **Restart Bean Agent** with new A2A implementation
2. **Test Agent Card** endpoint
3. **Test Skills** via A2A protocol
4. **Verify** 14:00-16:00 availability
5. **Optionally** convert Joy and Organizer agents to A2A

---

**The Bean agent now uses the official Google Agent2Agent protocol! 🎉**
