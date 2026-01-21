"""
Mr. Bean Agent - Appointment Diary Manager
Uses Google Gemini API to manage Mr. Bean's schedule
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv
import uvicorn

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

# FastAPI app
app = FastAPI(title="Mr. Bean Agent", description="Manages Mr. Bean's appointment diary")

class TimeSlotQuery(BaseModel):
    date: str
    start_time: str
    end_time: str
    activity: str

class DiaryResponse(BaseModel):
    status: str
    available: bool
    message: str
    diary: Dict = None

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

@app.get("/")
def read_root():
    return {
        "agent": "Mr. Bean",
        "status": "active",
        "description": "Managing Mr. Bean's appointment diary from 8 AM to 7 PM"
    }

@app.get("/diary")
def get_full_diary():
    """Get Mr. Bean's complete 10-day diary"""
    return {
        "agent": "Mr. Bean",
        "diary": BEAN_DIARY
    }

@app.post("/check_availability")
async def check_availability(query: TimeSlotQuery):
    """
    Check if Mr. Bean is available for the requested time slot
    Uses Gemini to intelligently check availability considering leisure time
    """
    date_str = query.date
    
    if date_str not in BEAN_DIARY:
        raise HTTPException(status_code=404, detail="Date not in diary range")
    
    day_schedule = BEAN_DIARY[date_str]
    
    # Use Gemini to analyze availability
    prompt = f"""
    You are Mr. Bean's personal assistant. Analyze if Mr. Bean can accommodate this request:
    
    Date: {query.date}
    Requested Time: {query.start_time} - {query.end_time}
    Activity: {query.activity}
    
    Current Schedule for {query.date}:
    {json.dumps(day_schedule['appointments'], indent=2)}
    
    Rules:
    1. Activities marked as "leisure" or "flexible" can be rescheduled
    2. Activities marked as "fixed" cannot be changed
    3. Mr. Bean needs at least 1 hour for meals
    4. Consider if the time slot overlaps with existing appointments
    
    Respond in JSON format:
    {{
        "available": true/false,
        "reason": "explanation",
        "conflicts": ["list of conflicting activities if any"],
        "suggestion": "alternative time if not available"
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        result_text = response.text
        
        # Extract JSON from response
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0].strip()
        
        result = json.loads(result_text)
        
        return {
            "agent": "Mr. Bean",
            "date": query.date,
            "requested_time": f"{query.start_time} - {query.end_time}",
            "activity": query.activity,
            "available": result.get("available", False),
            "reason": result.get("reason", ""),
            "conflicts": result.get("conflicts", []),
            "suggestion": result.get("suggestion", ""),
            "current_schedule": day_schedule
        }
    
    except Exception as e:
        return {
            "agent": "Mr. Bean",
            "date": query.date,
            "available": False,
            "reason": f"Error processing request: {str(e)}",
            "conflicts": [],
            "suggestion": ""
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
        "agent": "Mr. Bean",
        "status": "booked",
        "message": f"Appointment booked for {query.date} at {query.start_time}-{query.end_time}",
        "appointment": new_appointment
    }

@app.post("/reset_diary")
async def reset_diary():
    """Reset diary to original state"""
    global BEAN_DIARY
    BEAN_DIARY = generate_bean_diary()
    return {
        "agent": "Mr. Bean",
        "status": "reset",
        "message": "Diary has been reset to default schedule"
    }

if __name__ == "__main__":
    port = int(os.getenv("BEAN_AGENT_PORT", 8001))
    print(f"🎩 Starting Mr. Bean Agent on port {port}...")
    print(f"📅 Managing diary for next 10 days from {list(BEAN_DIARY.keys())[0]} to {list(BEAN_DIARY.keys())[-1]}")
    uvicorn.run(app, host="0.0.0.0", port=port)
