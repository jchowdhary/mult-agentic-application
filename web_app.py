"""
Multi-Agent Badminton Scheduler - Web Dashboard
Streamlit application to visualize and test the multi-agent system
"""

import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd
import time

# Page configuration
st.set_page_config(
    page_title="Multi-Agent Badminton Scheduler",
    page_icon="🏸",
    layout="wide"
)

# Agent configurations
BEAN_PORT = 8001
JOY_PORT = 8002
ORGANIZER_PORT = 8003

BEAN_URL = f"http://localhost:{BEAN_PORT}"
JOY_URL = f"http://localhost:{JOY_PORT}"
ORGANIZER_URL = f"http://localhost:{ORGANIZER_PORT}"

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .agent-card {
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .status-online {
        color: #2ecc71;
        font-weight: bold;
    }
    .status-offline {
        color: #e74c3c;
        font-weight: bold;
    }
    .appointment {
        padding: 0.8rem;
        margin: 0.5rem 0;
        border-left: 5px solid #3498db;
        background-color: #ffffff;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        color: #2c3e50;
        font-size: 1rem;
        font-weight: 500;
    }
    .appointment-leisure {
        border-left-color: #27ae60;
        background-color: #e8f8f5;
        color: #0e6251;
    }
    .appointment-flexible {
        border-left-color: #f39c12;
        background-color: #fef5e7;
        color: #7d6608;
    }
    .appointment-fixed {
        border-left-color: #e74c3c;
        background-color: #fadbd8;
        color: #922b21;
    }
    .appointment-booked {
        border-left-color: #9b59b6;
        background-color: #f4ecf7;
        color: #512e5f;
        font-weight: 600;
    }
    /* Style for dataframes in Results tab */
    .stDataFrame {
        font-size: 1rem;
    }
    /* Better table styling */
    table {
        color: #2c3e50 !important;
    }
    thead tr th {
        background-color: #3498db !important;
        color: white !important;
        font-weight: bold !important;
        padding: 12px !important;
    }
    tbody tr td {
        background-color: #ffffff !important;
        color: #2c3e50 !important;
        padding: 10px !important;
        border-bottom: 1px solid #ecf0f1 !important;
    }
    tbody tr:hover td {
        background-color: #e8f4f8 !important;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions
def check_agent_status(url, agent_name):
    """Check if an agent is online"""
    try:
        response = requests.get(url, timeout=2)
        return response.status_code == 200
    except:
        return False

def get_agent_diary(url):
    """Fetch agent's diary"""
    try:
        response = requests.get(f"{url}/diary", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def schedule_badminton():
    """Schedule badminton match via organizer"""
    try:
        response = requests.post(
            f"{ORGANIZER_URL}/schedule_badminton",
            json={"duration_hours": 2},
            timeout=60
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        return {"error": str(e)}

def time_overlaps(apt_time, start, end):
    """Check if an appointment time overlaps with a target slot"""
    try:
        apt_start, apt_end = apt_time.split("-")
        # Convert to minutes for comparison
        def to_minutes(time_str):
            h, m = map(int, time_str.split(":"))
            return h * 60 + m
        
        apt_start_min = to_minutes(apt_start)
        apt_end_min = to_minutes(apt_end)
        target_start_min = to_minutes(start)
        target_end_min = to_minutes(end)
        
        # Check for overlap
        return not (apt_end_min <= target_start_min or apt_start_min >= target_end_min)
    except:
        return False

def display_schedule(diary_data, agent_name, color):
    """Display agent's schedule in a nice format"""
    if not diary_data or "diary" not in diary_data:
        st.error(f"No diary data available for {agent_name}")
        return
    
    diary = diary_data["diary"]
    
    for date_str, schedule in list(diary.items())[:3]:  # Show first 3 days
        st.markdown(f"### 📅 {schedule['day']} - {date_str}")
        
        for apt in schedule["appointments"]:
            apt_type = apt.get("type", "unknown")
            css_class = f"appointment appointment-{apt_type}"
            
            icon = {
                "leisure": "🎮",
                "flexible": "🍽️",
                "fixed": "📌",
                "booked": "🏸"
            }.get(apt_type, "📝")
            
            st.markdown(
                f'<div class="{css_class}">{icon} <strong>{apt["time"]}</strong> - {apt["activity"]}</div>',
                unsafe_allow_html=True
            )
        st.markdown("---")

# Main app
def main():
    # Header
    st.markdown('<h1 class="main-header">🏸 Multi-Agent Badminton Scheduler</h1>', unsafe_allow_html=True)
    st.markdown("### Coordinating schedules using Google Gemini, CrewAI & LangGraph")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ System Status")
        
        # Check agent status
        bean_online = check_agent_status(BEAN_URL, "Mr. Bean")
        joy_online = check_agent_status(JOY_URL, "Mr. Joy")
        organizer_online = check_agent_status(ORGANIZER_URL, "Organizer")
        
        st.markdown("#### Agents Status:")
        st.markdown(f"🎩 **Mr. Bean** (Gemini): <span class='status-{'online' if bean_online else 'offline'}'>{'🟢 Online' if bean_online else '🔴 Offline'}</span>", unsafe_allow_html=True)
        st.markdown(f"😊 **Mr. Joy** (CrewAI): <span class='status-{'online' if joy_online else 'offline'}'>{'🟢 Online' if joy_online else '🔴 Offline'}</span>", unsafe_allow_html=True)
        st.markdown(f"🏸 **Organizer** (LangGraph): <span class='status-{'online' if organizer_online else 'offline'}'>{'🟢 Online' if organizer_online else '🔴 Offline'}</span>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # System info
        st.markdown("#### 📊 System Info:")
        st.markdown(f"- **Mr. Bean Port**: {BEAN_PORT}")
        st.markdown(f"- **Mr. Joy Port**: {JOY_PORT}")
        st.markdown(f"- **Organizer Port**: {ORGANIZER_PORT}")
        
        st.markdown("---")
        
        # Quick links
        st.markdown("#### 🔗 Quick Links:")
        st.markdown(f"- [Bean API]({BEAN_URL})")
        st.markdown(f"- [Joy API]({JOY_URL})")
        st.markdown(f"- [Organizer API]({ORGANIZER_URL})")
        
        st.markdown("---")
        
        if st.button("🔄 Refresh Status"):
            st.rerun()
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏠 Home", "📅 Schedules", "🏸 Schedule Match", "📊 Results", "🧪 Test Data"])
    
    with tab1:
        st.header("Welcome to Multi-Agent Scheduler")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 🎩 Mr. Bean")
            st.info("""
            **Framework**: Google Gemini
            
            Mr. Bean's personal AI assistant manages his diary with:
            - Work commitments
            - Leisure activities  
            - Meal times
            - Flexible scheduling
            """)
            
        with col2:
            st.markdown("### 😊 Mr. Joy")
            st.success("""
            **Framework**: CrewAI
            
            Mr. Joy's AI manager handles:
            - Business meetings
            - Gym & yoga sessions
            - Family time
            - Wellness activities
            """)
            
        with col3:
            st.markdown("### 🏸 Organizer")
            st.warning("""
            **Framework**: LangGraph
            
            Intelligent coordinator that:
            - Queries both agents
            - Finds common slots
            - Selects optimal time
            - Books appointments
            """)
        
        st.markdown("---")
        
        # How it works
        st.header("🎯 How It Works")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("#### 1️⃣ Fetch Diaries")
            st.write("Organizer retrieves 10-day schedules from both agents")
            
        with col2:
            st.markdown("#### 2️⃣ Check Availability")
            st.write("Queries each agent for 2-hour time slots")
            
        with col3:
            st.markdown("#### 3️⃣ Find Common Slots")
            st.write("AI identifies mutually available times")
            
        with col4:
            st.markdown("#### 4️⃣ Book Match")
            st.write("Automatically books with both agents")
    
    with tab2:
        st.header("📅 Agent Schedules")
        
        if not bean_online and not joy_online:
            st.error("⚠️ Both agents are offline. Please start them first!")
            st.code("""
# Terminal 1
python agents/bean/bean_agent.py

# Terminal 2  
python agents/joy/joy_agent.py
            """)
        else:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🎩 Mr. Bean's Schedule")
                if bean_online:
                    with st.spinner("Loading Bean's diary..."):
                        bean_diary = get_agent_diary(BEAN_URL)
                        if bean_diary:
                            display_schedule(bean_diary, "Mr. Bean", "#3498db")
                        else:
                            st.error("Failed to load diary")
                else:
                    st.warning("Agent is offline")
            
            with col2:
                st.subheader("😊 Mr. Joy's Schedule")
                if joy_online:
                    with st.spinner("Loading Joy's diary..."):
                        joy_diary = get_agent_diary(JOY_URL)
                        if joy_diary:
                            display_schedule(joy_diary, "Mr. Joy", "#2ecc71")
                        else:
                            st.error("Failed to load diary")
                else:
                    st.warning("Agent is offline")
    
    with tab3:
        st.header("🏸 Schedule Badminton Match")
        
        if not (bean_online and joy_online and organizer_online):
            st.error("⚠️ All agents must be online to schedule a match!")
            
            missing = []
            if not bean_online:
                missing.append("Mr. Bean (port 8001)")
            if not joy_online:
                missing.append("Mr. Joy (port 8002)")
            if not organizer_online:
                missing.append("Organizer (port 8003)")
            
            st.warning(f"Missing agents: {', '.join(missing)}")
        else:
            st.success("✅ All systems ready!")
            
            # Add common schedule viewer
            st.markdown("---")
            st.subheader("🔍 View Common Free Slots")
            st.markdown("Check which time slots are free for BOTH agents before scheduling.")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Date range selector
                date_option = st.radio(
                    "Select date range:",
                    ["Next 3 days", "Next 7 days", "All 10 days"],
                    horizontal=True
                )
            
            with col2:
                if st.button("🔎 Find Common Free Slots", type="secondary"):
                    with st.spinner("Analyzing schedules..."):
                        bean_diary = get_agent_diary(BEAN_URL)
                        joy_diary = get_agent_diary(JOY_URL)
                        
                        if bean_diary and joy_diary:
                            bean_schedule = bean_diary.get("diary", {})
                            joy_schedule = joy_diary.get("diary", {})
                            
                            # Determine how many days to check
                            days_to_check = 3 if "3" in date_option else (7 if "7" in date_option else 10)
                            
                            # Find common free slots
                            common_free = []
                            for date_str in list(bean_schedule.keys())[:days_to_check]:
                                if date_str in joy_schedule:
                                    # Get all busy times for both
                                    bean_busy = {apt["time"] for apt in bean_schedule[date_str]["appointments"]}
                                    joy_busy = {apt["time"] for apt in joy_schedule[date_str]["appointments"]}
                                    
                                    # Check common 2-hour slots
                                    two_hour_slots = [
                                        "08:00-10:00", "09:00-11:00", "10:00-12:00", "11:00-13:00",
                                        "12:00-14:00", "13:00-15:00", "14:00-16:00", "15:00-17:00",
                                        "16:00-18:00", "17:00-19:00"
                                    ]
                                    
                                    for slot in two_hour_slots:
                                        start, end = slot.split("-")
                                        # Check if any appointment overlaps with this slot
                                        bean_free = not any(time_overlaps(apt["time"], start, end) for apt in bean_schedule[date_str]["appointments"])
                                        joy_free = not any(time_overlaps(apt["time"], start, end) for apt in joy_schedule[date_str]["appointments"])
                                        
                                        if bean_free and joy_free:
                                            common_free.append({
                                                "Date": date_str,
                                                "Day": bean_schedule[date_str]["day"],
                                                "Time Slot": slot,
                                                "Duration": "2 hours"
                                            })
                            
                            if common_free:
                                st.success(f"🎉 Found {len(common_free)} common free 2-hour slots!")
                                df = pd.DataFrame(common_free)
                                st.dataframe(df, use_container_width=True, hide_index=True)
                            else:
                                st.warning("⚠️ No common free 2-hour slots found in selected date range.")
                        else:
                            st.error("Failed to fetch diaries")
            
            st.markdown("---")
            st.subheader("🚀 Auto-Schedule Match")
            st.markdown("""
            Let the AI organizer automatically find and book the best time slot.
            The Organizer will:
            1. Query both agents for their 10-day schedules
            2. Check availability for 2-hour badminton slots
            3. Find common available times
            4. Use AI to select the best slot
            5. Automatically book with both agents
            """)
            
            if st.button("🚀 Schedule Badminton Match", type="primary"):
                with st.spinner("🔄 Scheduling in progress... This may take 30-60 seconds..."):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Simulate progress
                    status_text.text("📚 Fetching diaries...")
                    progress_bar.progress(20)
                    
                    # Call the organizer
                    result = schedule_badminton()
                    
                    progress_bar.progress(100)
                    status_text.text("✅ Complete!")
                    
                    if result and "error" not in result:
                        # Store in session state
                        st.session_state.last_result = result
                        
                        st.success("🎉 Badminton match successfully scheduled!")
                        st.balloons()
                        
                        # Display results
                        if result.get("selected_slot"):
                            slot = result["selected_slot"]
                            st.markdown(f"""
                            ### 📅 Scheduled Time:
                            - **Date**: {slot.get('date', 'N/A')}
                            - **Time**: {slot.get('start_time', 'N/A')} - {slot.get('end_time', 'N/A')}
                            - **Duration**: 2 hours
                            """)
                        
                        # Show statistics
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Common Slots Found", result.get("common_slots_found", 0))
                        with col2:
                            st.metric("Bean Available", result.get("bean_available_slots", 0))
                        with col3:
                            st.metric("Joy Available", result.get("joy_available_slots", 0))
                        
                        # Show process log
                        with st.expander("📝 View Process Log"):
                            for msg in result.get("messages", []):
                                st.text(msg)
                    else:
                        st.error("❌ Failed to schedule match")
                        if result:
                            st.error(f"Error: {result.get('error', 'Unknown error')}")
    
    with tab4:
        st.header("📊 Last Scheduling Results")
        
        if "last_result" in st.session_state:
            result = st.session_state.last_result
            
            # Summary
            st.markdown("### 🎯 Summary")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.info(f"""
                **Status**: {result.get('status', 'unknown')}
                
                **Common Slots Found**: {result.get('common_slots_found', 0)}
                
                **Bean Available**: {result.get('bean_available_slots', 0)}
                
                **Joy Available**: {result.get('joy_available_slots', 0)}
                """)
            
            with col2:
                if result.get("selected_slot"):
                    slot = result["selected_slot"]
                    st.success(f"""
                    **🏸 Booked Slot**
                    
                    📅 **Date**: {slot.get('date', 'N/A')}
                    
                    ⏰ **Time**: {slot.get('start_time', 'N/A')} - {slot.get('end_time', 'N/A')}
                    
                    ⏱️ **Duration**: 2 hours
                    """)
            
            # All common slots
            if result.get("all_common_slots"):
                st.markdown("### 📋 All Available Slots")
                
                slots_df = pd.DataFrame(result["all_common_slots"])
                st.dataframe(slots_df, use_container_width=True)
            
            # Process messages
            st.markdown("### 📝 Process Log")
            for i, msg in enumerate(result.get("messages", []), 1):
                st.text(f"{i}. {msg}")
            
            # Download results
            st.download_button(
                label="💾 Download Results (JSON)",
                data=json.dumps(result, indent=2),
                file_name=f"badminton_schedule_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        else:
            st.info("No scheduling results yet. Go to 'Schedule Match' tab to schedule a badminton match!")
    
    with tab5:
        st.header("🧪 Test Data Management")
        
        st.markdown("""
        Use these tools to manage test data for the agents. You can reset diaries to their default 
        state or view the guaranteed common free slots.
        """)
        
        st.markdown("---")
        
        # Show guaranteed common slots
        st.subheader("🔒 Guaranteed Common Free Slots")
        st.info("""
        Both agents have been configured with a **guaranteed 2-hour free slot** every day:
        
        **Time**: 14:00 - 16:00 (2:00 PM - 4:00 PM)
        
        This ensures that the scheduling algorithm will always find at least one common slot 
        for all 10 days. Other slots may also be available depending on flexible/leisure activities.
        """)
        
        st.markdown("---")
        
        # Reset buttons
        st.subheader("🔄 Reset Agent Diaries")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 🎭 Mr. Bean")
            if bean_online:
                if st.button("🔄 Reset Bean's Diary", key="reset_bean"):
                    try:
                        response = requests.post(f"{BEAN_URL}/reset_diary", timeout=5)
                        if response.status_code == 200:
                            st.success("✅ Bean's diary reset successfully!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Failed to reset diary")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
            else:
                st.warning("⚠️ Agent offline")
        
        with col2:
            st.markdown("#### 😊 Mr. Joy")
            if joy_online:
                if st.button("🔄 Reset Joy's Diary", key="reset_joy"):
                    try:
                        response = requests.post(f"{JOY_URL}/reset_diary", timeout=5)
                        if response.status_code == 200:
                            st.success("✅ Joy's diary reset successfully!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Failed to reset diary")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
            else:
                st.warning("⚠️ Agent offline")
        
        with col3:
            st.markdown("#### 🔄 Reset Both")
            if bean_online and joy_online:
                if st.button("🔄 Reset All Diaries", type="primary", key="reset_all"):
                    with st.spinner("Resetting all diaries..."):
                        try:
                            bean_response = requests.post(f"{BEAN_URL}/reset_diary", timeout=5)
                            joy_response = requests.post(f"{JOY_URL}/reset_diary", timeout=5)
                            
                            if bean_response.status_code == 200 and joy_response.status_code == 200:
                                st.success("🎉 All diaries reset successfully!")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("❌ Failed to reset some diaries")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
            else:
                st.warning("⚠️ Both agents must be online")
        
        st.markdown("---")
        
        # Info about schedule configuration
        st.subheader("📊 Schedule Configuration Info")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🎭 Mr. Bean's Typical Schedule:**")
            st.code("""
08:00-09:00: Breakfast (flexible)
09:00-10:00: Morning walk (leisure)
10:00-12:00: Work (fixed)
12:00-13:00: Lunch (flexible)
13:00-14:00: Quick errands (leisure)
14:00-16:00: FREE (guaranteed)
16:00-17:00: Tea time (flexible)
17:00-18:00: Hobbies (leisure)
18:00-19:00: Dinner prep (flexible)
            """)
        
        with col2:
            st.markdown("**😊 Mr. Joy's Typical Schedule:**")
            st.code("""
08:00-09:00: Yoga (leisure)
09:00-10:00: Breakfast (flexible)
10:00-12:00: Client meetings (fixed)
12:00-13:00: Lunch (flexible)
13:00-14:00: Quick walk (leisure)
14:00-16:00: FREE (guaranteed)
16:00-17:00: Coffee (flexible)
17:00-18:00: Reading (leisure)
18:00-19:00: Dinner (flexible)
            """)
        
        st.markdown("---")
        
        st.info("""
        **Activity Types:**
        - 📌 **Fixed**: Cannot be rescheduled (work, meetings)
        - 🍽️ **Flexible**: Can be adjusted (meals, breaks)
        - 🎮 **Leisure**: Can be easily rescheduled (hobbies, exercise)
        - 🏸 **Booked**: New appointments made by the system
        """)

# Run the app
if __name__ == "__main__":
    main()
