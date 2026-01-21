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
        padding: 0.5rem;
        margin: 0.3rem 0;
        border-left: 4px solid #3498db;
        background-color: #ecf0f1;
    }
    .appointment-leisure {
        border-left-color: #2ecc71;
    }
    .appointment-flexible {
        border-left-color: #f39c12;
    }
    .appointment-fixed {
        border-left-color: #e74c3c;
    }
    .appointment-booked {
        border-left-color: #9b59b6;
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
    tab1, tab2, tab3, tab4 = st.tabs(["🏠 Home", "📅 Schedules", "🏸 Schedule Match", "📊 Results"])
    
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
            
            st.markdown("""
            Click the button below to start the intelligent scheduling process.
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

# Run the app
if __name__ == "__main__":
    main()
