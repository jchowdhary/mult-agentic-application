"""
Mr. Bean Agent - A2A-Compatible Implementation
Provides A2A agent card while maintaining FastAPI compatibility
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai
import uvicorn
import os
from langchain_groq import ChatGroq
# Load environment variables
load_dotenv()

# Configure Gemini
# Get GROQ API key
groq_api_key = os.getenv('GROQ_API_KEY')
model = ChatGroq(
    groq_api_key=groq_api_key,
    model_name="llama-3.3-70b-versatile",  # Latest Llama 3.2 text model
    temperature=0.3
)
# genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
# model = genai.GenerativeModel('models/gemini-2.5-flash-lite')

# FastAPI app
app = FastAPI(title="Mr. Bean Agent (A2A-Compatible)", description="Manages Mr. Bean's appointment diary using A2A protocol concepts")

class TimeSlotQuery(BaseModel):
    date: str
    start_time: str
    end_time: str
    activity: str

# Mr. Bean's appointment diary for 10 days
def generate_bean_diary():
    """Generate Mr. Bean's appointment diary for the next 10 days"""
    diary = {}
    start_date = datetime.now().date()
    
    for day_offset in range(10):
        current_date = start_date + timedelta(days=day_offset)
        date_str = current_date.strftime("%Y-%m-%d")
        day_name = current_date.strftime("%A")
        
        # Mr. Bean's typical schedule
        # Note: 14:00-16:00 is intentionally FREE for all days (common slot with Joy)
        schedule = {
            "date": date_str,
            "day": day_name,
            "appointments": [
                {"time": "08:00-09:00", "activity": "Breakfast with Teddy", "type": "flexible"},
                {"time": "09:00-10:00", "activity": "Morning walk in park", "type": "leisure"},
                {"time": "10:00-12:00", "activity": "Work at office", "type": "fixed"},
                {"time": "12:00-13:00", "activity": "Lunch break", "type": "flexible"},
                {"time": "13:00-14:00", "activity": "Quick errands", "type": "leisure"},
                # 14:00-16:00 is FREE (guaranteed common slot)
                {"time": "16:00-17:00", "activity": "Tea time", "type": "flexible"},
                {"time": "17:00-18:00", "activity": "Hobbies and TV", "type": "leisure"},
                {"time": "18:00-19:00", "activity": "Dinner preparation", "type": "flexible"}
            ]
        }
        
        # Add some variation for specific days (but keep 14:00-16:00 free)
        if day_offset % 3 == 0:
            schedule["appointments"].insert(3, {"time": "12:30-13:00", "activity": "Lunch with friends", "type": "flexible"})
        if day_offset % 5 == 0:
            schedule["appointments"].insert(2, {"time": "09:30-10:00", "activity": "Check emails", "type": "leisure"})
        
        diary[date_str] = schedule
    
    return diary

# Store the diary
BEAN_DIARY = generate_bean_diary()

# A2A Agent Card endpoint
@app.get("/.well-known/agent.json")
def get_agent_card():
    """A2A Protocol - Agent Card Discovery"""
    port = int(os.getenv("BEAN_AGENT_PORT", 8001))
    base_url = f"http://localhost:{port}"
    
    return {
        "name": "Mr. Bean Calendar Agent",
        "description": "Manages Mr. Bean's appointment diary from 8 AM to 7 PM. Can check availability and book appointments.",
        "url": base_url,
        "version": "1.0.0",
        "protocol_version": "0.3.0",
        "protocol": "Agent2Agent (A2A)",
        "framework": "Google Gemini + FastAPI",
        "skills": [
            {
                "name": "get_diary",
                "description": "Get Mr. Bean's complete 10-day diary",
                "endpoint": f"{base_url}/diary",
                "method": "GET",
                "parameters": []
            },
            {
                "name": "check_availability",
                "description": "Check if Mr. Bean is available for a specific time slot",
                "endpoint": f"{base_url}/check_availability",
                "method": "POST",
                "parameters": [
                    {"name": "date", "type": "string", "description": "Date in YYYY-MM-DD format", "required": True},
                    {"name": "start_time", "type": "string", "description": "Start time in HH:MM format", "required": True},
                    {"name": "end_time", "type": "string", "description": "End time in HH:MM format", "required": True},
                    {"name": "activity", "type": "string", "description": "Activity description", "required": True}
                ]
            },
            {
                "name": "book_appointment",
                "description": "Book an appointment in Mr. Bean's diary",
                "endpoint": f"{base_url}/book_appointment",
                "method": "POST",
                "parameters": [
                    {"name": "date", "type": "string", "description": "Date in YYYY-MM-DD format", "required": True},
                    {"name": "start_time", "type": "string", "description": "Start time in HH:MM format", "required": True},
                    {"name": "end_time", "type": "string", "description": "End time in HH:MM format", "required": True},
                    {"name": "activity", "type": "string", "description": "Activity description", "required": True}
                ]
            },
            {
                "name": "reset_diary",
                "description": "Reset Mr. Bean's diary to default schedule",
                "endpoint": f"{base_url}/reset_diary",
                "method": "POST",
                "parameters": []
            }
        ]
    }

@app.get("/")
def read_root():
    return {
        "agent": "Mr. Bean (A2A-Compatible)",
        "status": "active",
        "description": "Managing Mr. Bean's appointment diary from 8 AM to 7 PM",
        "protocol": "Agent2Agent (A2A) Compatible",
        "agent_card": "http://localhost:8001/.well-known/agent.json"
    }

@app.get("/diary")
def get_full_diary():
    """Get Mr. Bean's complete 10-day diary"""
    return {
        "agent": "Mr. Bean (A2A)",
        "diary": BEAN_DIARY,
        "protocol": "Agent2Agent"
    }

@app.post("/check_availability")
async def check_availability(query: TimeSlotQuery):
    """
    Check if Mr. Bean is available for the requested time slot
    Uses Google Gemini AI to intelligently analyze availability
    """
    date_str = query.date
    
    if date_str not in BEAN_DIARY:
        raise HTTPException(status_code=404, detail="Date not in diary range")
    
    day_schedule = BEAN_DIARY[date_str]
    
    # Use Gemini AI to analyze availability
    prompt = f"""
    You are Mr. Bean's intelligent scheduling assistant. Analyze if Mr. Bean is available:
    
    REQUESTED SLOT:
    - Date: {query.date} ({day_schedule['day']})
    - Time: {query.start_time} to {query.end_time}
    - Activity: {query.activity}
    
    CURRENT SCHEDULE:
    {json.dumps(day_schedule['appointments'], indent=2)}
    
    RULES:
    1. If NO appointments exist in the requested time range ({query.start_time}-{query.end_time}), he IS AVAILABLE
    2. "fixed" appointments CANNOT be moved (e.g., work, meetings)
    3. "flexible" and "leisure" appointments CAN be rescheduled
    4. Check EXACT time overlaps only
    
    RESPOND WITH ONLY THIS JSON (no markdown, no extra text):
    {{"available": true, "reason": "explanation", "conflicts": [], "suggestion": ""}}
    """
    
    try:
        response = model.invoke(prompt)
        result_text = response.text.strip()
        
        # Extract JSON
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0].strip()
        
        result = json.loads(result_text)
        
        return {
            "agent": "Mr. Bean (A2A + Gemini AI)",
            "date": query.date,
            "requested_time": f"{query.start_time} - {query.end_time}",
            "activity": query.activity,
            "available": result.get("available", False),
            "reason": result.get("reason", ""),
            "conflicts": result.get("conflicts", []),
            "suggestion": result.get("suggestion", ""),
            "current_schedule": day_schedule,
            "protocol": "Agent2Agent + Gemini AI"
        }
    
    except Exception as e:
        return {
            "agent": "Mr. Bean (A2A)",
            "date": query.date,
            "available": False,
            "reason": f"AI Error: {str(e)}",
            "conflicts": [],
            "suggestion": "",
            "protocol": "Agent2Agent"
        }

@app.post("/book_appointment")
async def book_appointment(query: TimeSlotQuery):
    """Book an appointment in Mr. Bean's diary"""
    date_str = query.date
    
    if date_str not in BEAN_DIARY:
        raise HTTPException(status_code=404, detail="Date not in diary range")
    
    # Add the appointment
    new_appointment = {
        "time": f"{query.start_time}-{query.end_time}",
        "activity": query.activity,
        "type": "booked"
    }
    
    BEAN_DIARY[date_str]["appointments"].append(new_appointment)
    BEAN_DIARY[date_str]["appointments"].sort(key=lambda x: x["time"])
    
    return {
        "agent": "Mr. Bean (A2A)",
        "status": "booked",
        "message": f"Appointment booked for {query.date} at {query.start_time}-{query.end_time}",
        "appointment": new_appointment,
        "protocol": "Agent2Agent"
    }

@app.post("/reset_diary")
async def reset_diary():
    """Reset diary to original state"""
    global BEAN_DIARY
    BEAN_DIARY = generate_bean_diary()
    return {
        "agent": "Mr. Bean (A2A)",
        "status": "reset",
        "message": "Diary has been reset to default schedule",
        "protocol": "Agent2Agent"
    }

if __name__ == "__main__":
    port = int(os.getenv("BEAN_AGENT_PORT", 8001))
    print(f"🎩 Starting Mr. Bean Agent (A2A-Compatible) on port {port}...")
    print(f"📅 Managing diary for next 10 days from {list(BEAN_DIARY.keys())[0]} to {list(BEAN_DIARY.keys())[-1]}")
    print(f"🔗 Agent Card (A2A Discovery): http://localhost:{port}/.well-known/agent.json")
    print(f"🌐 Protocol: Agent2Agent (A2A) Compatible")
    print(f"⚡ Framework: Google Gemini + FastAPI")
    
    uvicorn.run(app, host="0.0.0.0", port=port)
