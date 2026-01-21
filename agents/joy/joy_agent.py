"""
Mr. Joy Agent - Appointment Diary Manager
Uses CrewAI to manage Mr. Joy's schedule
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from crewai import Agent, Task, Crew, Process
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import uvicorn

# Load environment variables
load_dotenv()

# Configure LLM for CrewAI - using Groq (fast and free!)
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    groq_api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.7
)

# FastAPI app
app = FastAPI(title="Mr. Joy Agent", description="Manages Mr. Joy's appointment diary using CrewAI")

class TimeSlotQuery(BaseModel):
    date: str
    start_time: str
    end_time: str
    activity: str

# Mr. Joy's appointment diary for 10 days
def generate_joy_diary():
    """Generate Mr. Joy's appointment diary for the next 10 days"""
    diary = {}
    start_date = datetime.now().date()
    
    for day_offset in range(10):
        current_date = start_date + timedelta(days=day_offset)
        date_str = current_date.strftime("%Y-%m-%d")
        day_name = current_date.strftime("%A")
        
        # Mr. Joy's typical schedule (slightly different from Bean)
        # Note: 14:00-16:00 is intentionally FREE for all days (common slot with Bean)
        schedule = {
            "date": date_str,
            "day": day_name,
            "appointments": [
                {"time": "08:00-09:00", "activity": "Morning yoga and meditation", "type": "leisure"},
                {"time": "09:00-10:00", "activity": "Breakfast", "type": "flexible"},
                {"time": "10:00-12:00", "activity": "Client meetings", "type": "fixed"},
                {"time": "12:00-13:00", "activity": "Lunch and rest", "type": "flexible"},
                {"time": "13:00-14:00", "activity": "Quick walk", "type": "leisure"},
                # 14:00-16:00 is FREE (guaranteed common slot)
                {"time": "16:00-17:00", "activity": "Coffee break", "type": "flexible"},
                {"time": "17:00-18:00", "activity": "Reading and relaxation", "type": "leisure"},
                {"time": "18:00-19:00", "activity": "Dinner time", "type": "flexible"}
            ]
        }
        
        # Add some variation for specific days (but keep 14:00-16:00 free)
        if day_offset % 4 == 0:
            schedule["appointments"].insert(2, {"time": "10:30-11:00", "activity": "Team standup", "type": "fixed"})
        if day_offset % 6 == 0:
            schedule["appointments"].insert(5, {"time": "16:30-17:00", "activity": "Quick gym session", "type": "leisure"})
        
        diary[date_str] = schedule
    
    return diary

# Store the diary
JOY_DIARY = generate_joy_diary()

# Create CrewAI agent for Mr. Joy
joy_schedule_agent = Agent(
    role="Personal Calendar Manager for Mr. Joy",
    goal="Efficiently manage Mr. Joy's appointment diary and find available time slots",
    backstory="""You are Mr. Joy's dedicated personal assistant with deep knowledge 
    of his schedule preferences and priorities. You understand that leisure activities 
    and flexible appointments can be rescheduled to accommodate important meetings or events.
    You always consider Mr. Joy's wellbeing and ensure he has proper meal times and rest.""",
    llm=llm,
    verbose=True,
    allow_delegation=False
)

@app.get("/")
def read_root():
    return {
        "agent": "Mr. Joy",
        "status": "active",
        "description": "Managing Mr. Joy's appointment diary from 8 AM to 7 PM using CrewAI",
        "framework": "CrewAI"
    }

@app.get("/diary")
def get_full_diary():
    """Get Mr. Joy's complete 10-day diary"""
    return {
        "agent": "Mr. Joy",
        "diary": JOY_DIARY,
        "framework": "CrewAI"
    }

@app.post("/check_availability")
async def check_availability(query: TimeSlotQuery):
    """
    Check if Mr. Joy is available for the requested time slot
    Direct schedule checking (AI temporarily disabled due to API quota)
    """
    date_str = query.date
    
    if date_str not in JOY_DIARY:
        raise HTTPException(status_code=404, detail="Date not in diary range")
    
    day_schedule = JOY_DIARY[date_str]
    
    # Convert times to minutes for easy comparison
    def time_to_minutes(time_str):
        h, m = map(int, time_str.split(":"))
        return h * 60 + m
    
    req_start = time_to_minutes(query.start_time)
    req_end = time_to_minutes(query.end_time)
    
    # Check for conflicts
    conflicts = []
    fixed_conflicts = []
    
    for apt in day_schedule["appointments"]:
        apt_start_str, apt_end_str = apt["time"].split("-")
        apt_start = time_to_minutes(apt_start_str)
        apt_end = time_to_minutes(apt_end_str)
        
        # Check if times overlap
        if not (req_end <= apt_start or req_start >= apt_end):
            conflicts.append(apt["activity"])
            if apt["type"] == "fixed":
                fixed_conflicts.append(apt["activity"])
    
    # Determine availability
    if not conflicts:
        # No conflicts - available
        return {
            "agent": "Mr. Joy (CrewAI)",
            "date": query.date,
            "requested_time": f"{query.start_time} - {query.end_time}",
            "activity": query.activity,
            "available": True,
            "reason": "Time slot is completely free",
            "conflicts": [],
            "suggestion": "",
            "current_schedule": day_schedule
        }
    elif fixed_conflicts:
        # Has fixed conflicts - not available
        return {
            "agent": "Mr. Joy (CrewAI)",
            "date": query.date,
            "requested_time": f"{query.start_time} - {query.end_time}",
            "activity": query.activity,
            "available": False,
            "reason": f"Conflicts with fixed appointment(s): {', '.join(fixed_conflicts)}",
            "conflicts": conflicts,
            "suggestion": "Try a different time slot",
            "current_schedule": day_schedule
        }
    else:
        # Only flexible/leisure conflicts - can reschedule, so available
        return {
            "agent": "Mr. Joy (CrewAI)",
            "date": query.date,
            "requested_time": f"{query.start_time} - {query.end_time}",
            "activity": query.activity,
            "available": True,
            "reason": f"Can reschedule flexible activities: {', '.join(conflicts)}",
            "conflicts": conflicts,
            "suggestion": "",
            "current_schedule": day_schedule
        }

@app.post("/book_appointment")
async def book_appointment(query: TimeSlotQuery):
    """Book an appointment in Mr. Joy's diary"""
    date_str = query.date
    
    if date_str not in JOY_DIARY:
        raise HTTPException(status_code=404, detail="Date not in diary range")
    
    # Add the appointment
    new_appointment = {
        "time": f"{query.start_time}-{query.end_time}",
        "activity": query.activity,
        "type": "booked"
    }
    
    JOY_DIARY[date_str]["appointments"].append(new_appointment)
    JOY_DIARY[date_str]["appointments"].sort(key=lambda x: x["time"])
    
    return {
        "agent": "Mr. Joy",
        "framework": "CrewAI",
        "status": "booked",
        "message": f"Appointment booked for {query.date} at {query.start_time}-{query.end_time}",
        "appointment": new_appointment
    }

@app.post("/reset_diary")
async def reset_diary():
    """Reset diary to original state"""
    global JOY_DIARY
    JOY_DIARY = generate_joy_diary()
    return {
        "agent": "Mr. Joy",
        "framework": "CrewAI",
        "status": "reset",
        "message": "Diary has been reset to default schedule"
    }

if __name__ == "__main__":
    port = int(os.getenv("JOY_AGENT_PORT", 8002))
    print(f"😊 Starting Mr. Joy Agent (CrewAI) on port {port}...")
    print(f"📅 Managing diary for next 10 days from {list(JOY_DIARY.keys())[0]} to {list(JOY_DIARY.keys())[-1]}")
    uvicorn.run(app, host="0.0.0.0", port=port)
