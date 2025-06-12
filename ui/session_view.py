"""
Session visualization components for Streamlit.
This module provides simplified UI components for visualizing Focus Buddy sessions.
"""

import os
import sys
import streamlit as st
import pandas as pd
from datetime import datetime

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.session_tracker import get_recent_sessions, load_session

def render_session_history():
    """Render the session history view.
    
    Returns:
        str or None: Selected session ID if a session is selected, None otherwise.
    """
    st.header("Session History")
    
    # Get recent sessions
    sessions = get_recent_sessions(limit=10)
    
    if not sessions:
        st.info("No previous sessions found. Start a new focus session to begin tracking your productivity.")
        return None
    
    # Create a DataFrame for the sessions
    sessions_data = []
    for session in sessions:
        start_time = datetime.fromisoformat(session["start_time"])
        
        # Calculate duration
        if session["end_time"]:
            end_time = datetime.fromisoformat(session["end_time"])
            duration = end_time - start_time
            duration_str = str(duration).split('.')[0]  # Remove microseconds
        else:
            duration_str = "Active"
        
        # Add to sessions data
        sessions_data.append({
            "Session ID": session["session_id"],
            "Date": start_time.strftime("%Y-%m-%d"),
            "Time": start_time.strftime("%H:%M"),
            "Duration": duration_str,
            "Status": session["status"].capitalize(),
            "Score": session["productivity_score"]
        })
    
    # Create DataFrame and display as table
    if sessions_data:
        df = pd.DataFrame(sessions_data)
        st.dataframe(df, use_container_width=True)
        
        # Allow selecting a session to view details
        selected_session_id = st.selectbox(
            "Select a session to view details",
            options=[s["Session ID"] for s in sessions_data],
            format_func=lambda x: f"{x} - {next((s['Date'] + ' ' + s['Time']) for s in sessions_data if s['Session ID'] == x)}"
        )
        
        return selected_session_id
    
    return None

def render_session_details(session_id):
    """Render details for a specific session.
    
    Args:
        session_id (str): ID of the session to display.
    """
    # Load the session
    session_tracker = load_session(session_id)
    
    if not session_tracker:
        st.error(f"Could not load session {session_id}")
        return
    
    # Get session data
    session_data = session_tracker.get_session_data()
    metrics = session_tracker.get_productivity_metrics()
    
    # Display session summary
    st.subheader("Session Summary")
    st.write(session_data["summary"])
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Duration", metrics["duration_formatted"])
    
    with col2:
        st.metric("Focus Time", metrics["focus_time_formatted"])
    
    with col3:
        st.metric("Productivity Score", f"{metrics['productivity_score']}/100")
    
    # Display screenshots if available
    captures_dir = os.path.join("data", "session_logs", session_id, "captures")
    if os.path.exists(captures_dir):
        screenshot_files = [
            f for f in os.listdir(captures_dir)
            if f.startswith("screen_") and f.endswith((".jpg", ".jpeg", ".png"))
        ]
        
        if screenshot_files:
            st.subheader("Screenshots")
            st.write(f"{len(screenshot_files)} screenshots captured during this session")
            
            # Show the most recent screenshot
            latest_screenshot = sorted(screenshot_files)[-1]
            file_path = os.path.join(captures_dir, latest_screenshot)
            
            try:
                from PIL import Image
                image = Image.open(file_path)
                st.image(image, caption="Most recent screenshot", use_column_width=True)
            except Exception as e:
                st.error(f"Error displaying image: {str(e)}")
    
    # Display notes
    if session_data["notes"]:
        st.subheader("Session Notes")
        st.text_area("Notes", value=session_data["notes"], height=100, disabled=True)

if __name__ == "__main__":
    # When run directly, show a demo of the session history
    st.set_page_config(
        page_title="Focus Buddy Session History",
        page_icon="📊"
    )
    
    st.title("Focus Buddy Session History")
    selected_session = render_session_history()
    
    if selected_session:
        st.markdown("---")
        render_session_details(selected_session)
