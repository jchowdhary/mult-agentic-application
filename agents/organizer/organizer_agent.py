"""
Organizer Agent - Badminton Match Scheduler
Uses LangGraph to coordinate between Mr. Bean and Mr. Joy agents
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Annotated, TypedDict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import uvicorn

# Load environment variables
load_dotenv()

# Configure LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-pro",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.3
)

# FastAPI app
app = FastAPI(title="Organizer Agent", description="Coordinates badminton match scheduling between Bean and Joy")

class ScheduleRequest(BaseModel):
    duration_hours: int = 2
    preferred_dates: List[str] = None

# State for LangGraph
class OrganizerState(TypedDict):
    bean_diary: Dict
    joy_diary: Dict
    bean_availability: List[Dict]
    joy_availability: List[Dict]
    common_slots: List[Dict]
    selected_slot: Dict
    messages: List[str]
    status: str

def get_agent_diary(agent_name: str, port: int) -> Dict:
    """Fetch diary from agent"""
    try:
        response = requests.get(f"http://localhost:{port}/diary", timeout=10)
        if response.status_code == 200:
            return response.json()
        return {}
    except Exception as e:
        print(f"Error fetching {agent_name} diary: {str(e)}")
        return {}

def check_agent_availability(agent_name: str, port: int, date: str, start_time: str, end_time: str) -> Dict:
    """Check if agent is available for specific time slot"""
    try:
        payload = {
            "date": date,
            "start_time": start_time,
            "end_time": end_time,
            "activity": "Badminton match"
        }
        response = requests.post(
            f"http://localhost:{port}/check_availability",
            json=payload,
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        return {"available": False, "reason": "Error checking availability"}
    except Exception as e:
        print(f"Error checking {agent_name} availability: {str(e)}")
        return {"available": False, "reason": f"Connection error: {str(e)}"}

def book_agent_appointment(agent_name: str, port: int, date: str, start_time: str, end_time: str) -> Dict:
    """Book appointment with agent"""
    try:
        payload = {
            "date": date,
            "start_time": start_time,
            "end_time": end_time,
            "activity": "Badminton match"
        }
        response = requests.post(
            f"http://localhost:{port}/book_appointment",
            json=payload,
            timeout=10
        )
        return response.json() if response.status_code == 200 else {}
    except Exception as e:
        print(f"Error booking with {agent_name}: {str(e)}")
        return {}

# LangGraph nodes
def fetch_diaries(state: OrganizerState) -> OrganizerState:
    """Fetch diaries from both agents"""
    print("📚 Fetching diaries from Mr. Bean and Mr. Joy...")
    
    bean_port = int(os.getenv("BEAN_AGENT_PORT", 8001))
    joy_port = int(os.getenv("JOY_AGENT_PORT", 8002))
    
    bean_data = get_agent_diary("Mr. Bean", bean_port)
    joy_data = get_agent_diary("Mr. Joy", joy_port)
    
    state["bean_diary"] = bean_data.get("diary", {})
    state["joy_diary"] = joy_data.get("diary", {})
    state["messages"].append(f"✅ Fetched diaries for {len(state['bean_diary'])} days")
    
    return state

def find_potential_slots(state: OrganizerState) -> OrganizerState:
    """Find potential 2-hour time slots across all days"""
    print("🔍 Finding potential 2-hour time slots...")
    
    potential_slots = []
    bean_diary = state["bean_diary"]
    
    # Common time slots to check (2-hour windows between 8 AM and 7 PM)
    time_windows = [
        ("08:00", "10:00"), ("09:00", "11:00"), ("10:00", "12:00"),
        ("11:00", "13:00"), ("12:00", "14:00"), ("13:00", "15:00"),
        ("14:00", "16:00"), ("15:00", "17:00"), ("16:00", "18:00"),
        ("17:00", "19:00")
    ]
    
    for date_str in bean_diary.keys():
        for start, end in time_windows:
            potential_slots.append({
                "date": date_str,
                "start_time": start,
                "end_time": end
            })
    
    state["messages"].append(f"🎯 Found {len(potential_slots)} potential time slots to check")
    return state

def check_bean_availability(state: OrganizerState) -> OrganizerState:
    """Check Mr. Bean's availability for all potential slots"""
    print("🎩 Checking Mr. Bean's availability...")
    
    bean_port = int(os.getenv("BEAN_AGENT_PORT", 8001))
    bean_available = []
    
    # Check a subset of potential slots (first 30 to avoid too many API calls)
    for slot in state.get("bean_diary", {}).keys()[:5]:  # Check first 5 days
        time_windows = [
            ("09:00", "11:00"), ("13:00", "15:00"), ("16:00", "18:00")
        ]
        
        for start, end in time_windows:
            result = check_agent_availability("Mr. Bean", bean_port, slot, start, end)
            if result.get("available", False):
                bean_available.append({
                    "date": slot,
                    "start_time": start,
                    "end_time": end,
                    "reason": result.get("reason", "")
                })
    
    state["bean_availability"] = bean_available
    state["messages"].append(f"✅ Mr. Bean available for {len(bean_available)} slots")
    
    return state

def check_joy_availability(state: OrganizerState) -> OrganizerState:
    """Check Mr. Joy's availability for Bean's available slots"""
    print("😊 Checking Mr. Joy's availability...")
    
    joy_port = int(os.getenv("JOY_AGENT_PORT", 8002))
    joy_available = []
    
    # Check Joy's availability for each of Bean's available slots
    for bean_slot in state["bean_availability"]:
        result = check_agent_availability(
            "Mr. Joy", 
            joy_port,
            bean_slot["date"],
            bean_slot["start_time"],
            bean_slot["end_time"]
        )
        
        if result.get("available", False):
            joy_available.append({
                "date": bean_slot["date"],
                "start_time": bean_slot["start_time"],
                "end_time": bean_slot["end_time"],
                "reason": result.get("reason", "")
            })
    
    state["joy_availability"] = joy_available
    state["messages"].append(f"✅ Mr. Joy available for {len(joy_available)} slots")
    
    return state

def find_common_slots(state: OrganizerState) -> OrganizerState:
    """Find common available slots for both"""
    print("🤝 Finding common available slots...")
    
    bean_slots = {f"{s['date']}_{s['start_time']}_{s['end_time']}" for s in state["bean_availability"]}
    joy_slots = {f"{s['date']}_{s['start_time']}_{s['end_time']}" for s in state["joy_availability"]}
    
    common = bean_slots.intersection(joy_slots)
    
    common_slots = []
    for slot_key in common:
        parts = slot_key.split("_")
        common_slots.append({
            "date": parts[0],
            "start_time": parts[1],
            "end_time": parts[2]
        })
    
    state["common_slots"] = sorted(common_slots, key=lambda x: x["date"])
    state["messages"].append(f"🎉 Found {len(common_slots)} common available slots")
    
    if common_slots:
        state["status"] = "slots_found"
    else:
        state["status"] = "no_slots"
    
    return state

def select_best_slot(state: OrganizerState) -> OrganizerState:
    """Select the best slot using LLM"""
    print("🧠 Using AI to select the best slot...")
    
    if not state["common_slots"]:
        state["selected_slot"] = {}
        state["messages"].append("❌ No common slots found")
        return state
    
    # Use LLM to select best slot
    prompt = f"""
    You are an intelligent meeting organizer. Select the BEST time slot for a badminton match 
    between Mr. Bean and Mr. Joy based on these available options:
    
    {json.dumps(state["common_slots"], indent=2)}
    
    Consider:
    1. Earlier in the week is generally better
    2. Afternoon slots (13:00-17:00) are ideal for sports
    3. Avoid very early morning or late evening
    
    Respond with ONLY the index number (0, 1, 2, etc.) of the best slot.
    """
    
    try:
        response = llm.invoke(prompt)
        selection = int(response.content.strip())
        
        if 0 <= selection < len(state["common_slots"]):
            state["selected_slot"] = state["common_slots"][selection]
            state["messages"].append(f"✨ Selected slot: {state['selected_slot']}")
        else:
            state["selected_slot"] = state["common_slots"][0]
            state["messages"].append("✨ Selected first available slot")
    except:
        state["selected_slot"] = state["common_slots"][0]
        state["messages"].append("✨ Selected first available slot")
    
    return state

def book_appointments(state: OrganizerState) -> OrganizerState:
    """Book the selected slot with both agents"""
    print("📅 Booking appointments with both agents...")
    
    if not state["selected_slot"]:
        state["messages"].append("❌ Cannot book - no slot selected")
        return state
    
    slot = state["selected_slot"]
    bean_port = int(os.getenv("BEAN_AGENT_PORT", 8001))
    joy_port = int(os.getenv("JOY_AGENT_PORT", 8002))
    
    # Book with both agents
    bean_booking = book_agent_appointment(
        "Mr. Bean", bean_port, 
        slot["date"], slot["start_time"], slot["end_time"]
    )
    
    joy_booking = book_agent_appointment(
        "Mr. Joy", joy_port,
        slot["date"], slot["start_time"], slot["end_time"]
    )
    
    state["messages"].append(f"✅ Booked with Mr. Bean: {bean_booking.get('status', 'unknown')}")
    state["messages"].append(f"✅ Booked with Mr. Joy: {joy_booking.get('status', 'unknown')}")
    state["status"] = "booked"
    
    return state

# Build LangGraph workflow
def build_organizer_workflow():
    """Build the LangGraph workflow for organizing badminton match"""
    
    workflow = StateGraph(OrganizerState)
    
    # Add nodes
    workflow.add_node("fetch_diaries", fetch_diaries)
    workflow.add_node("check_bean", check_bean_availability)
    workflow.add_node("check_joy", check_joy_availability)
    workflow.add_node("find_common", find_common_slots)
    workflow.add_node("select_slot", select_best_slot)
    workflow.add_node("book", book_appointments)
    
    # Add edges
    workflow.set_entry_point("fetch_diaries")
    workflow.add_edge("fetch_diaries", "check_bean")
    workflow.add_edge("check_bean", "check_joy")
    workflow.add_edge("check_joy", "find_common")
    workflow.add_edge("find_common", "select_slot")
    workflow.add_edge("select_slot", "book")
    workflow.add_edge("book", END)
    
    return workflow.compile()

# Create workflow
organizer_workflow = build_organizer_workflow()

@app.get("/")
def read_root():
    return {
        "agent": "Organizer",
        "status": "active",
        "description": "Coordinates badminton match scheduling between Mr. Bean and Mr. Joy",
        "framework": "LangGraph"
    }

@app.post("/schedule_badminton")
async def schedule_badminton(request: ScheduleRequest):
    """Schedule a badminton match between Bean and Joy"""
    
    print("\n🏸 Starting badminton match scheduling process...")
    print("=" * 60)
    
    # Initialize state
    initial_state = {
        "bean_diary": {},
        "joy_diary": {},
        "bean_availability": [],
        "joy_availability": [],
        "common_slots": [],
        "selected_slot": {},
        "messages": [],
        "status": "in_progress"
    }
    
    try:
        # Run the LangGraph workflow
        final_state = organizer_workflow.invoke(initial_state)
        
        print("\n" + "=" * 60)
        print("🎉 Scheduling process completed!")
        print("=" * 60 + "\n")
        
        return {
            "organizer": "LangGraph Agent",
            "status": final_state["status"],
            "selected_slot": final_state["selected_slot"],
            "common_slots_found": len(final_state["common_slots"]),
            "all_common_slots": final_state["common_slots"],
            "messages": final_state["messages"],
            "bean_available_slots": len(final_state["bean_availability"]),
            "joy_available_slots": len(final_state["joy_availability"])
        }
    
    except Exception as e:
        print(f"❌ Error in scheduling: {str(e)}")
        return {
            "organizer": "LangGraph Agent",
            "status": "error",
            "error": str(e),
            "messages": ["Error occurred during scheduling process"]
        }

@app.get("/health")
def health_check():
    """Check if both agents are reachable"""
    bean_port = int(os.getenv("BEAN_AGENT_PORT", 8001))
    joy_port = int(os.getenv("JOY_AGENT_PORT", 8002))
    
    bean_status = "offline"
    joy_status = "offline"
    
    try:
        response = requests.get(f"http://localhost:{bean_port}/", timeout=2)
        if response.status_code == 200:
            bean_status = "online"
    except:
        pass
    
    try:
        response = requests.get(f"http://localhost:{joy_port}/", timeout=2)
        if response.status_code == 200:
            joy_status = "online"
    except:
        pass
    
    return {
        "organizer": "online",
        "mr_bean_agent": bean_status,
        "mr_joy_agent": joy_status,
        "all_systems": "ready" if bean_status == "online" and joy_status == "online" else "not ready"
    }

if __name__ == "__main__":
    port = int(os.getenv("ORGANIZER_AGENT_PORT", 8003))
    print(f"🏸 Starting Organizer Agent (LangGraph) on port {port}...")
    print(f"💡 Coordinates badminton match scheduling between Bean and Joy")
    uvicorn.run(app, host="0.0.0.0", port=port)
