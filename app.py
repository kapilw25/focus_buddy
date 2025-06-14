"""
Focus Buddy - Main Streamlit Application
This is the main entry point for the Focus Buddy application.
"""

import os
import time
import threading
import streamlit as st
from datetime import datetime, timedelta

from ui.dashboard import (
    render_dashboard,
    capture_and_analyze_screen
)
from utils.screen_capture import ScreenCapture
from core.vision_analyzer import VisionAnalyzer
from core.session_tracker import SessionTracker
from utils.config import (
    SCREEN_CAPTURE_INTERVAL,
    CHECK_IN_INTERVAL,
    DEFAULT_SESSION_DURATION
)

# Set page configuration
st.set_page_config(
    page_title="Focus Buddy",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables if they don't exist
if "session_active" not in st.session_state:
    st.session_state.session_active = False
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "session_start_time" not in st.session_state:
    st.session_state.session_start_time = None
if "last_analysis" not in st.session_state:
    st.session_state.last_analysis = None
if "analysis_history" not in st.session_state:
    st.session_state.analysis_history = []
if "screen_capture" not in st.session_state:
    st.session_state.screen_capture = None
if "vision_analyzer" not in st.session_state:
    st.session_state.vision_analyzer = None
if "session_tracker" not in st.session_state:
    st.session_state.session_tracker = None
if "capture_interval" not in st.session_state:
    st.session_state.capture_interval = SCREEN_CAPTURE_INTERVAL
if "check_in_interval" not in st.session_state:
    st.session_state.check_in_interval = CHECK_IN_INTERVAL
if "session_duration" not in st.session_state:
    st.session_state.session_duration = DEFAULT_SESSION_DURATION
if "auto_end_session" not in st.session_state:
    st.session_state.auto_end_session = False
if "stop_capture_thread" not in st.session_state:
    st.session_state.stop_capture_thread = False
if "last_capture_time" not in st.session_state:
    st.session_state.last_capture_time = 0
if "auto_end_triggered" not in st.session_state:
    st.session_state.auto_end_triggered = False

def start_session():
    """Start a new focus session."""
    # Generate a new session ID based on timestamp
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Initialize components
    screen_capture = ScreenCapture(session_id)
    vision_analyzer = VisionAnalyzer()
    session_tracker = SessionTracker(session_id)
    
    # Update session state
    st.session_state.session_active = True
    st.session_state.session_id = session_id
    st.session_state.session_start_time = datetime.now()
    st.session_state.screen_capture = screen_capture
    st.session_state.vision_analyzer = vision_analyzer
    st.session_state.session_tracker = session_tracker
    st.session_state.analysis_history = []
    st.session_state.stop_capture_thread = False
    st.session_state.last_capture_time = 0
    
    # Add initial tags
    session_tracker.add_tag("focus_session")
    
    # Add session start note
    session_tracker.add_note("Session started")
    
    st.success(f"Focus session started! Session ID: {session_id}")

def end_session():
    """End the current focus session."""
    if not st.session_state.session_active:
        st.warning("No active session to end.")
        return
    
    # Stop the capture thread
    st.session_state.stop_capture_thread = True
    
    # Generate session summary
    if st.session_state.session_tracker:
        # Calculate session duration
        duration = datetime.now() - st.session_state.session_start_time
        duration_minutes = duration.total_seconds() / 60
        
        # Generate summary text
        summary = f"Focus session completed. Duration: {duration_minutes:.1f} minutes."
        
        # Add productivity insights if available
        if st.session_state.analysis_history:
            productive_count = sum(1 for a in st.session_state.analysis_history if a.get("is_productive", False))
            productivity_percentage = (productive_count / len(st.session_state.analysis_history)) * 100
            summary += f" Productivity rate: {productivity_percentage:.1f}%."
        
        # End the session with summary
        st.session_state.session_tracker.end_session(summary)
        
        # Display metrics
        metrics = st.session_state.session_tracker.get_productivity_metrics()
        st.success(f"Session ended! {summary}")
        st.info(f"Focus score: {metrics['productivity_score']}/100")
    
    # Reset session state
    st.session_state.session_active = False
    st.session_state.session_id = None
    st.session_state.session_start_time = None
    st.session_state.screen_capture = None
    st.session_state.vision_analyzer = None
    st.session_state.session_tracker = None

def capture_and_analyze_once(auto_capture=False):
    """Capture and analyze screen once when called from the main thread.
    
    Args:
        auto_capture (bool): Whether this is an automatic capture or manual.
    """
    if not st.session_state.session_active:
        return
        
    try:
        print(f"Attempting to capture screenshot... (auto={auto_capture})")
        # Capture screenshot
        screenshot_path = st.session_state.screen_capture.capture_screen(force=True)
        
        if screenshot_path:
            print(f"Screenshot captured: {screenshot_path}")
            # Analyze the screenshot
            print("Analyzing screenshot with GPT-4o...")
            analysis = st.session_state.vision_analyzer.analyze_image(screenshot_path)
            
            # Mark if this was an automatic capture
            analysis["auto_capture"] = auto_capture
            
            print("Analysis complete, updating session state...")
            # Store the analysis
            st.session_state.last_analysis = analysis
            st.session_state.analysis_history.append(analysis)
            
            # Update the session tracker
            st.session_state.session_tracker.add_screen_analysis(analysis)
            
            # Limit history size
            if len(st.session_state.analysis_history) > 20:
                st.session_state.analysis_history = st.session_state.analysis_history[-20:]
            
            print("Analysis added to session state")
            st.session_state.last_capture_time = time.time()
            
            # Check if we should auto-end the session
            if st.session_state.auto_end_session and st.session_state.session_start_time:
                elapsed_time = (datetime.now() - st.session_state.session_start_time).total_seconds()
                if elapsed_time >= st.session_state.session_duration:
                    st.session_state.auto_end_triggered = True
            
            return True
        else:
            print("Failed to capture screenshot")
            return False
    except Exception as e:
        print(f"Error in capture and analyze: {str(e)}")
        return False

def check_capture_interval():
    """Check if it's time to capture a screenshot based on the interval."""
    if not st.session_state.session_active:
        return False
        
    current_time = time.time()
    time_since_last_capture = current_time - st.session_state.last_capture_time
    
    return time_since_last_capture >= st.session_state.capture_interval

def render_settings():
    """Render settings in the sidebar."""
    with st.sidebar.expander("⚙️ Settings", expanded=False):
        # Capture settings
        st.subheader("Screen Capture")
        capture_interval = st.slider(
            "Capture Interval (seconds)",
            min_value=10,
            max_value=300,
            value=st.session_state.capture_interval,
            step=10,
            help="How frequently Focus Buddy will capture and analyze your screen"
        )
        st.session_state.capture_interval = capture_interval
        
        # Session settings
        st.subheader("Session")
        check_in_interval = st.slider(
            "Check-in Interval (minutes)",
            min_value=1,
            max_value=30,
            value=st.session_state.check_in_interval // 60,
            step=1,
            help="How frequently Focus Buddy will check in with you during a session"
        )
        st.session_state.check_in_interval = check_in_interval * 60  # Convert to seconds
        
        auto_end_session = st.checkbox(
            "Auto-end Session After Duration",
            value=st.session_state.auto_end_session,
            help="Automatically end the session after the specified duration"
        )
        st.session_state.auto_end_session = auto_end_session
        
        if auto_end_session:
            session_duration = st.number_input(
                "Session Duration (minutes)",
                min_value=5,
                max_value=480,
                value=st.session_state.session_duration // 60,
                step=5,
                help="Duration for focus sessions"
            )
            st.session_state.session_duration = session_duration * 60  # Convert to seconds

def display_sidebar():
    """Display and handle the sidebar UI."""
    st.sidebar.title("🎯 Focus Buddy")
    st.sidebar.write("AI-powered productivity assistant")
    
    # Session controls
    st.sidebar.header("Session Controls")
    
    if st.session_state.session_active:
        # Display session info
        elapsed_time = datetime.now() - st.session_state.session_start_time
        elapsed_minutes = elapsed_time.total_seconds() / 60
        st.sidebar.info(f"Session active for {elapsed_minutes:.1f} minutes")
        
        # End session button
        if st.sidebar.button("End Session", type="primary"):
            end_session()
        
        # Check if auto-end was triggered
        if st.session_state.get("auto_end_triggered", False):
            end_session()
            st.session_state.auto_end_triggered = False
    else:
        # Start session button
        if st.sidebar.button("Start Focus Session", type="primary"):
            start_session()
    
    # Manual capture button (available in both states)
    if st.sidebar.button("Capture & Analyze Now"):
        with st.spinner("Capturing and analyzing your screen..."):
            if st.session_state.session_active:
                # Use session components
                success = capture_and_analyze_once(auto_capture=False)
                if success:
                    st.success("Screen captured and analyzed!")
                else:
                    st.error("Failed to capture or analyze screen.")
            else:
                # Use temporary components
                analysis = capture_and_analyze_screen()
                if analysis:
                    if "temp_analysis_history" not in st.session_state:
                        st.session_state.temp_analysis_history = []
                    st.session_state.temp_analysis_history.append(analysis)
                    st.session_state.last_analysis = analysis
                    st.success("Screen captured and analyzed!")
                else:
                    st.error("Failed to capture or analyze screen.")
    
    # Settings section
    render_settings()
    
    # About section
    st.sidebar.header("About")
    st.sidebar.info(
        "Focus Buddy helps you maintain focus during deep work sessions "
        "by monitoring your screen, analyzing your environment, and "
        "providing timely nudges to keep you on track."
    )
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.caption("© 2025 Focus Buddy")

def auto_capture_thread():
    """Background thread for automatic screen capture and check-ins."""
    if not st.session_state.session_active:
        return
    
    # Get current time
    current_time = time.time()
    
    # Check if it's time for a screen capture
    if current_time - st.session_state.last_capture_time >= st.session_state.capture_interval:
        print(f"Auto capture triggered at {datetime.now().strftime('%H:%M:%S')}")
        capture_success = capture_and_analyze_once(auto_capture=True)
        if capture_success:
            print(f"Auto capture successful at {datetime.now().strftime('%H:%M:%S')}")
            st.session_state.last_capture_time = current_time
            # Add a note to indicate this was an automatic capture
            if st.session_state.session_tracker:
                st.session_state.session_tracker.add_note("Automatic screen capture")
    
    # Check if it's time for a check-in
    if st.session_state.session_tracker and st.session_state.session_tracker.should_check_in():
        print(f"Auto check-in triggered at {datetime.now().strftime('%H:%M:%S')}")
        # Perform check-in
        check_in_data = {
            "timestamp": datetime.now().isoformat(),
            "type": "automatic",
            "question": "Automatic check-in",
            "response": "System generated check-in"
        }
        st.session_state.session_tracker.add_check_in(check_in_data)
        print(f"Auto check-in completed at {datetime.now().strftime('%H:%M:%S')}")

def main():
    """Main application entry point."""
    # Display the sidebar
    display_sidebar()
    
    # Run the auto capture thread in the background
    if st.session_state.session_active:
        auto_capture_thread()
    
    # Display the main content
    if st.session_state.session_active:
        # Show active session dashboard
        render_dashboard(
            session_active=True,
            session_tracker=st.session_state.session_tracker,
            analysis_history=st.session_state.analysis_history,
            last_analysis=st.session_state.last_analysis,
            session_start_time=st.session_state.session_start_time
        )
    else:
        # Show inactive session dashboard
        temp_history = st.session_state.get("temp_analysis_history", [])
        last_analysis = st.session_state.get("last_analysis", None)
        
        render_dashboard(
            session_active=False,
            analysis_history=temp_history,
            last_analysis=last_analysis
        )

if __name__ == "__main__":
    main()
