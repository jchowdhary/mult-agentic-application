# 🧪 Complete Testing Guide - Multi-Agent Badminton Scheduler

## 📋 Overview

This guide shows you how to:
1. Start all agents in separate terminals
2. Test with curl commands (API testing)
3. Test with web dashboard (UI testing)

---

## 🚀 Step-by-Step Execution

### Prerequisites
✅ Dependencies installed (already done)
✅ API key configured in .env (already done)
✅ Virtual environment created (already done)

---

## 🖥️ Terminal Setup

You need to open **4 separate terminals**. Here's how:

### Option 1: Using GNOME Terminal (Recommended for Zorin OS)
1. Press `Ctrl+Alt+T` to open first terminal
2. Press `Ctrl+Shift+T` 3 more times to open 3 more tabs
3. You'll have 4 tabs in one window

### Option 2: Using Separate Windows
1. Press `Ctrl+Alt+T` four times to open 4 separate terminal windows
2. Arrange them on your screen

---

## 📝 Commands for Each Terminal

### Terminal 1: Mr. Bean Agent

```bash
cd /home/jayant/genAICourse/multi-agent-collaboration
source multiagent/bin/activate
python agents/bean/bean_agent.py
```

**Expected Output:**
```
🎩 Starting Mr. Bean Agent on port 8001...
📅 Managing diary for next 10 days from 2026-01-21 to 2026-01-30
INFO:     Started server process [12345]
INFO:     Uvicorn running on http://0.0.0.0:8001
```

**Status**: ✅ Leave this terminal running

---

### Terminal 2: Mr. Joy Agent

```bash
cd /home/jayant/genAICourse/multi-agent-collaboration
source multiagent/bin/activate
python agents/joy/joy_agent.py
```

**Expected Output:**
```
😊 Starting Mr. Joy Agent (CrewAI) on port 8002...
📅 Managing diary for next 10 days from 2026-01-21 to 2026-01-30
INFO:     Started server process [12346]
INFO:     Uvicorn running on http://0.0.0.0:8002
```

**Status**: ✅ Leave this terminal running

---

### Terminal 3: Organizer Agent

```bash
cd /home/jayant/genAICourse/multi-agent-collaboration
source multiagent/bin/activate
python agents/organizer/organizer_agent.py
```

**Expected Output:**
```
🏸 Starting Organizer Agent (LangGraph) on port 8003...
💡 Coordinates badminton match scheduling between Bean and Joy
INFO:     Started server process [12347]
INFO:     Uvicorn running on http://0.0.0.0:8003
```

**Status**: ✅ Leave this terminal running

---

### Terminal 4: Testing Terminal (Keep this free for curl commands)

```bash
cd /home/jayant/genAICourse/multi-agent-collaboration
source multiagent/bin/activate
```

**This terminal will be used for testing with curl commands below**

---

## 🧪 Testing with curl Commands

### Test 1: Check if all agents are running

```bash
# Test Mr. Bean Agent
curl -s http://localhost:8001/ | python -m json.tool

# Test Mr. Joy Agent
curl -s http://localhost:8002/ | python -m json.tool

# Test Organizer Agent
curl -s http://localhost:8003/ | python -m json.tool
```

**Expected**: Each should return agent information in JSON format

---

### Test 2: Check System Health

```bash
curl -s http://localhost:8003/health | python -m json.tool
```

**Expected Output:**
```json
{
  "organizer": "online",
  "mr_bean_agent": "online",
  "mr_joy_agent": "online",
  "all_systems": "ready"
}
```

---

### Test 3: View Mr. Bean's Diary

```bash
curl -s http://localhost:8001/diary | python -m json.tool | head -50
```

**You'll see**: 10-day diary with appointments from 08:00 to 19:00

---

### Test 4: View Mr. Joy's Diary

```bash
curl -s http://localhost:8002/diary | python -m json.tool | head -50
```

**You'll see**: 10-day diary with different appointments

---

### Test 5: Check Mr. Bean's Availability for Specific Time

```bash
curl -s -X POST http://localhost:8001/check_availability \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-01-22",
    "start_time": "16:00",
    "end_time": "18:00",
    "activity": "Badminton match"
  }' | python -m json.tool
```

**Expected**: JSON response with availability status, conflicts, and suggestions

---

### Test 6: Check Mr. Joy's Availability for Specific Time

```bash
curl -s -X POST http://localhost:8002/check_availability \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-01-22",
    "start_time": "16:00",
    "end_time": "18:00",
    "activity": "Badminton match"
  }' | python -m json.tool
```

**Expected**: JSON response with CrewAI's availability analysis

---

### Test 7: **MAIN TEST - Schedule Badminton Match!** 🏸

```bash
curl -s -X POST http://localhost:8003/schedule_badminton \
  -H "Content-Type: application/json" \
  -d '{"duration_hours": 2}' | python -m json.tool
```

**This will take 30-60 seconds** (AI processing time)

**Expected Output:**
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
  "all_common_slots": [
    {
      "date": "2026-01-21",
      "start_time": "16:00",
      "end_time": "18:00"
    },
    ...
  ],
  "messages": [
    "✅ Fetched diaries for 10 days",
    "✅ Mr. Bean available for 12 slots",
    "✅ Mr. Joy available for 10 slots",
    "🎉 Found 5 common available slots",
    "✨ Selected slot: {...}",
    "✅ Booked with Mr. Bean: booked",
    "✅ Booked with Mr. Joy: booked"
  ],
  "bean_available_slots": 12,
  "joy_available_slots": 10
}
```

---

### Test 8: Verify Booking - Check Updated Diaries

```bash
# Check Bean's diary again - should see new "booked" appointment
curl -s http://localhost:8001/diary | python -m json.tool | grep -A 5 "Badminton"

# Check Joy's diary again - should see new "booked" appointment
curl -s http://localhost:8002/diary | python -m json.tool | grep -A 5 "Badminton"
```

**Expected**: You'll see the badminton appointment with `"type": "booked"`

---

## 🌐 Testing with Web Dashboard (Optional)

If you want to use the web interface instead:

### Start Streamlit (Use Terminal 4 OR a 5th terminal)

```bash
cd /home/jayant/genAICourse/multi-agent-collaboration
source multiagent/bin/activate
streamlit run web_app.py
```

Then open browser: **http://localhost:8501**

---

## 📊 Complete Test Script (All-in-One)

Save this as a test script to run all tests at once:

```bash
#!/bin/bash
# Save as: test_system.sh

echo "🧪 Multi-Agent System Testing"
echo "=============================="
echo ""

echo "📍 Test 1: System Health Check"
curl -s http://localhost:8003/health | python -m json.tool
echo ""

echo "📍 Test 2: Verify Mr. Bean is online"
curl -s http://localhost:8001/ | python -m json.tool | head -10
echo ""

echo "📍 Test 3: Verify Mr. Joy is online"
curl -s http://localhost:8002/ | python -m json.tool | head -10
echo ""

echo "📍 Test 4: View sample from Bean's diary"
curl -s http://localhost:8001/diary | python -m json.tool | head -30
echo ""

echo "📍 Test 5: View sample from Joy's diary"
curl -s http://localhost:8002/diary | python -m json.tool | head -30
echo ""

echo "📍 Test 6: Check Bean's availability"
curl -s -X POST http://localhost:8001/check_availability \
  -H "Content-Type: application/json" \
  -d '{"date": "2026-01-22", "start_time": "16:00", "end_time": "18:00", "activity": "Test"}' \
  | python -m json.tool
echo ""

echo "📍 Test 7: MAIN TEST - Schedule Badminton Match"
echo "⏳ This will take 30-60 seconds..."
curl -s -X POST http://localhost:8003/schedule_badminton \
  -H "Content-Type: application/json" \
  -d '{"duration_hours": 2}' | python -m json.tool
echo ""

echo "✅ All tests completed!"
```

**Make it executable and run:**
```bash
chmod +x test_system.sh
./test_system.sh
```

---

## 🔍 Troubleshooting

### Issue: "Connection refused"
**Cause**: Agent not running
**Solution**: Check the corresponding terminal and restart the agent

### Issue: "Port already in use"
**Solution**:
```bash
lsof -ti:8001 | xargs kill -9  # Kill Bean
lsof -ti:8002 | xargs kill -9  # Kill Joy
lsof -ti:8003 | xargs kill -9  # Kill Organizer
```

### Issue: Slow response (> 90 seconds)
**Cause**: AI processing time, internet speed
**Solution**: Wait patiently, check internet connection

### Issue: "No common slots found"
**Cause**: Both agents genuinely busy (this is correct behavior!)
**Solution**: The system is working correctly

---

## 📈 Expected Timings

| Operation | Expected Time |
|-----------|---------------|
| Agent startup | 2-5 seconds |
| Health check | < 1 second |
| View diary | < 1 second |
| Check availability (one agent) | 5-10 seconds |
| Full badminton scheduling | 30-60 seconds |

---

## ✅ Success Checklist

- [ ] All 3 agent terminals show "Uvicorn running"
- [ ] Health check returns `"all_systems": "ready"`
- [ ] Can view both diaries via curl
- [ ] Availability check returns valid JSON
- [ ] Badminton scheduling completes successfully
- [ ] Both diaries show the booked appointment

---

## 🎯 Quick Validation Commands

Run these to quickly verify everything works:

```bash
# 1. Check all systems
curl -s http://localhost:8003/health

# 2. Schedule match
curl -s -X POST http://localhost:8003/schedule_badminton \
  -H "Content-Type: application/json" \
  -d '{"duration_hours": 2}' | python -m json.tool

# 3. Verify booking
curl -s http://localhost:8001/diary | python -m json.tool | grep -C 3 "Badminton"
```

---

## 📝 Notes

- **All APIs return JSON** - Perfect for curl testing
- **No web browser needed** - Pure command-line testing
- **Streamlit is optional** - Only for visual interface
- **Each agent is independent** - Can test separately
- **Organizer coordinates** - Links all agents together

---

## 🏆 You've Successfully Tested When:

✅ Health check shows all agents online
✅ Scheduling returns a selected time slot
✅ Both agents show the badminton appointment
✅ Process completes in < 90 seconds
✅ No error messages in any terminal

---

**Happy Testing! 🚀🏸**

**Remember**: Keep all 3 agent terminals running while testing!
