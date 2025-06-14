"""
Dashboard components for Streamlit.
This module provides simplified UI components for the Focus Buddy dashboard.
"""

import os
import sys
import time
from datetime import datetime
import streamlit as st
import pandas as pd
from PIL import Image

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.screen_capture import ScreenCapture
from core.vision_analyzer import VisionAnalyzer

def render_header():
    """Render the dashboard header."""
    st.title("Focus Buddy Dashboard")
    st.write("AI-powered productivity assistant that helps you maintain focus")

def render_session_metrics(session_tracker=None, analysis_history=None, session_start_time=None):
    """Render metrics for the current session."""
    st.header("Session Metrics")
    
    # Create columns for metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Session duration
        if session_start_time:
            elapsed_time = datetime.now() - session_start_time
            elapsed_minutes = elapsed_time.total_seconds() / 60
            st.metric("Session Duration", f"{elapsed_minutes:.1f} min")
        else:
            st.metric("Session Duration", "0 min")
    
    with col2:
        # Productivity rate
        if analysis_history and len(analysis_history) > 0:
            productive_count = sum(1 for a in analysis_history if a.get("is_productive", False))
            productivity_percentage = (productive_count / len(analysis_history)) * 100
            st.metric("Productivity Rate", f"{productivity_percentage:.1f}%")
        else:
            st.metric("Productivity Rate", "N/A")
    
    with col3:
        # Focus score
        if session_tracker:
            metrics = session_tracker.get_productivity_metrics()
            st.metric("Focus Score", f"{metrics['productivity_score']}/100")
        else:
            st.metric("Focus Score", "N/A")

def render_latest_analysis(analysis=None):
    """Render the latest screen analysis."""
    st.header("Latest Screen Analysis")
    
    if analysis:
        # Create columns for analysis details
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.write("**What's on your screen:**")
            st.write(analysis["content"])
            
            # Display detected apps and activities
            if analysis.get("detected_apps"):
                st.write(f"**Detected applications:** {', '.join(analysis['detected_apps'])}")
            
            if analysis.get("detected_activities"):
                st.write(f"**Detected activities:** {', '.join(analysis['detected_activities'])}")
            
            # Display productivity assessment
            if analysis.get("is_productive", False):
                st.success("This appears to be productive work.")
            else:
                st.warning("This might be a distraction from your focus.")
        
        with col2:
            # Display timestamp
            if "timestamp" in analysis:
                timestamp = datetime.fromisoformat(analysis["timestamp"])
                st.write(f"**Time:** {timestamp.strftime('%H:%M:%S')}")
            
            # Display thumbnail of screenshot if available
            if "image_path" in analysis and os.path.exists(analysis["image_path"]):
                try:
                    image = Image.open(analysis["image_path"])
                    # Resize for thumbnail
                    thumbnail_size = (300, 200)
                    image.thumbnail(thumbnail_size)
                    st.image(image, caption="Screenshot", use_container_width=True)
                except Exception as e:
                    st.error(f"Error displaying image: {str(e)}")
    else:
        st.info("No screen analysis available yet. The first analysis will appear shortly.")

def render_activity_timeline(analysis_history=None):
    """Render the activity timeline."""
    st.header("Activity Timeline")
    
    if analysis_history and len(analysis_history) > 0:
        # Create a DataFrame for the history
        history_data = []
        
        for analysis in reversed(analysis_history):
            if "timestamp" not in analysis:
                continue
                
            timestamp = datetime.fromisoformat(analysis["timestamp"])
            
            # Create a summary of the analysis
            summary = analysis.get("content", "")
            if len(summary) > 100:
                summary = summary[:97] + "..."
            
            # Determine status
            status = "Productive" if analysis.get("is_productive", False) else "Distraction"
            
            # Determine if this was automatic or manual
            capture_type = "Automatic" if analysis.get("auto_capture", False) else "Manual"
            
            # Add to history data
            history_data.append({
                "Time": timestamp.strftime("%H:%M:%S"),
                "Activity": summary,
                "Status": status,
                "Type": capture_type,
                "Apps": ", ".join(analysis.get("detected_apps", [])) if analysis.get("detected_apps") else "None"
            })
        
        # Create DataFrame and display as table
        if history_data:
            df = pd.DataFrame(history_data)
            st.dataframe(df, use_container_width=True)
    else:
        st.info("No activity history available yet.")

def render_dashboard(session_active=False, session_tracker=None, analysis_history=None, 
                    last_analysis=None, session_start_time=None):
    """Render the complete dashboard."""
    render_header()
    
    if not session_active:
        st.write("Welcome to Focus Buddy! Start a focus session to begin tracking your productivity.")
        
        # Display instructions
        st.header("How it works")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("1. Start a Session")
            st.write("Click 'Start Focus Session' in the sidebar to begin tracking your productivity.")
        
        with col2:
            st.subheader("2. Work Naturally")
            st.write("Focus Buddy will periodically capture your screen and analyze your activity.")
        
        with col3:
            st.subheader("3. Get Insights")
            st.write("Receive real-time feedback and productivity insights to stay on track.")
        
        return
    
    # Render dashboard components for active session
    render_session_metrics(session_tracker, analysis_history, session_start_time)
    render_latest_analysis(last_analysis)
    render_activity_timeline(analysis_history)

def capture_and_analyze_screen():
    """Capture and analyze the current screen."""
    # Create temporary instances
    screen_capture = ScreenCapture()
    vision_analyzer = VisionAnalyzer()
    
    # Capture screenshot
    screenshot_path = screen_capture.capture_screen(force=True)
    
    if screenshot_path:
        # Get all screenshots (main and individual monitors)
        all_screenshots = screen_capture.get_all_screenshots()
        
        # Analyze each screenshot
        all_analyses = []
        for img_path in all_screenshots:
            analysis = vision_analyzer.analyze_image(img_path)
            all_analyses.append(analysis)
        
        # If we have multiple analyses, combine them
        if len(all_analyses) > 1:
            # Use the main screenshot's analysis as the base
            combined_analysis = all_analyses[0].copy()
            
            # Combine content from all analyses
            combined_content = "Analysis of all connected screens:\n\n"
            for i, analysis in enumerate(all_analyses):
                screen_name = "Main Screen" if i == 0 else f"Screen {i}"
                combined_content += f"--- {screen_name} ---\n{analysis['content']}\n\n"
            
            combined_analysis["content"] = combined_content
            
            # Combine detected apps and activities
            all_apps = []
            all_activities = []
            for analysis in all_analyses:
                all_apps.extend(analysis.get("detected_apps", []))
                all_activities.extend(analysis.get("detected_activities", []))
            
            # Remove duplicates
            combined_analysis["detected_apps"] = list(set(all_apps))
            combined_analysis["detected_activities"] = list(set(all_activities))
            
            # Determine overall productivity (productive if any screen shows productive work)
            combined_analysis["is_productive"] = any(a.get("is_productive", False) for a in all_analyses)
            
            # Store paths to all screenshots
            combined_analysis["all_screenshots"] = all_screenshots
            
            return combined_analysis
        else:
            # Just return the single analysis
            return all_analyses[0]
    
    return None

if __name__ == "__main__":
    # When run directly, show a demo of the dashboard
    st.set_page_config(
        page_title="Focus Buddy",
        page_icon="🎯",
        layout="wide"
    )
    
    st.sidebar.title("🎯 Focus Buddy")
    st.sidebar.write("AI-powered productivity assistant")
    
    # Demo controls
    st.sidebar.header("Demo Controls")
    
    if st.sidebar.button("Capture & Analyze Screen Now"):
        with st.spinner("Capturing and analyzing your screen..."):
            analysis = capture_and_analyze_screen()
            
            if analysis:
                st.session_state.last_analysis = analysis
                if "analysis_history" not in st.session_state:
                    st.session_state.analysis_history = []
                st.session_state.analysis_history.append(analysis)
                st.success("Screen captured and analyzed!")
            else:
                st.error("Failed to capture or analyze screen.")
    
    # Initialize session state for demo
    if "analysis_history" not in st.session_state:
        st.session_state.analysis_history = []
    
    if "last_analysis" not in st.session_state:
        st.session_state.last_analysis = None
    
    if "session_start_time" not in st.session_state:
        st.session_state.session_start_time = datetime.now()
    
    # Render the dashboard
    render_dashboard(
        session_active=True,
        session_tracker=None,
        analysis_history=st.session_state.analysis_history,
        last_analysis=st.session_state.last_analysis,
        session_start_time=st.session_state.session_start_time
    )
