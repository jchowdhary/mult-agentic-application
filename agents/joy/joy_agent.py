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
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import uvicorn

# Load environment variables
load_dotenv()

# Configure LLM for CrewAI
llm = ChatGoogleGenerativeAI(
    model="gemini-pro",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
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
        schedule = {
            "date": date_str,
            "day": day_name,
            "appointments": [
                {"time": "08:00-09:00", "activity": "Morning yoga and meditation", "type": "leisure"},
                {"time": "09:00-10:00", "activity": "Breakfast", "type": "flexible"},
                {"time": "10:00-12:00", "activity": "Client meetings", "type": "fixed"},
                {"time": "12:00-13:00", "activity": "Lunch and rest", "type": "flexible"},
                {"time": "13:00-15:00", "activity": "Gym workout", "type": "leisure"},
                {"time": "15:00-16:00", "activity": "Coffee break", "type": "flexible"},
                {"time": "16:00-18:00", "activity": "Reading and relaxation", "type": "leisure"},
                {"time": "18:00-19:00", "activity": "Dinner time", "type": "flexible"}
            ]
        }
        
        # Add some random activities for variety
        if day_offset % 2 == 0:
            schedule["appointments"][4] = {"time": "13:00-15:00", "activity": "Business workshop", "type": "fixed"}
        if day_offset % 5 == 0:
            schedule["appointments"][6] = {"time": "16:00-18:00", "activity": "Family gathering", "type": "fixed"}
        
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
    Uses CrewAI agent to intelligently check availability
    """
    date_str = query.date
    
    if date_str not in JOY_DIARY:
        raise HTTPException(status_code=404, detail="Date not in diary range")
    
    day_schedule = JOY_DIARY[date_str]
    
    # Create CrewAI task for availability check
    availability_task = Task(
        description=f"""
        Analyze Mr. Joy's availability for the following request:
        
        Date: {query.date} ({day_schedule['day']})
        Requested Time: {query.start_time} - {query.end_time}
        Activity: {query.activity}
        Duration: 2 hours
        
        Current Schedule for {query.date}:
        {json.dumps(day_schedule['appointments'], indent=2)}
        
        Important Rules:
        1. Activities marked as "leisure" or "flexible" CAN be rescheduled
        2. Activities marked as "fixed" CANNOT be changed
        3. Mr. Joy must have proper meal times (breakfast, lunch, dinner)
        4. Evaluate conflicts with existing appointments
        5. Consider Mr. Joy's energy levels and preferences
        
        Provide your analysis in this EXACT JSON format (no extra text):
        {{
            "available": true or false,
            "reason": "clear explanation of availability or conflict",
            "conflicts": ["list any conflicting activities"],
            "suggestion": "alternative time if not available, empty string if available"
        }}
        """,
        expected_output="JSON formatted availability analysis",
        agent=joy_schedule_agent
    )
    
    try:
        # Execute CrewAI task
        crew = Crew(
            agents=[joy_schedule_agent],
            tasks=[availability_task],
            process=Process.sequential,
            verbose=False
        )
        
        result_text = crew.kickoff()
        
        # Extract JSON from response
        result_str = str(result_text)
        if "```json" in result_str:
            result_str = result_str.split("```json")[1].split("```")[0].strip()
        elif "```" in result_str:
            result_str = result_str.split("```")[1].split("```")[0].strip()
        elif "{" in result_str and "}" in result_str:
            start = result_str.find("{")
            end = result_str.rfind("}") + 1
            result_str = result_str[start:end]
        
        result = json.loads(result_str)
        
        return {
            "agent": "Mr. Joy",
            "framework": "CrewAI",
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
        print(f"Error in CrewAI task: {str(e)}")
        return {
            "agent": "Mr. Joy",
            "framework": "CrewAI",
            "date": query.date,
            "available": False,
            "reason": f"Error processing request with CrewAI: {str(e)}",
            "conflicts": [],
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

if __name__ == "__main__":
    port = int(os.getenv("JOY_AGENT_PORT", 8002))
    print(f"😊 Starting Mr. Joy Agent (CrewAI) on port {port}...")
    print(f"📅 Managing diary for next 10 days from {list(JOY_DIARY.keys())[0]} to {list(JOY_DIARY.keys())[-1]}")
    uvicorn.run(app, host="0.0.0.0", port=port)
