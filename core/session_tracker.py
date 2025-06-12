"""
Session Tracker for the Focus Buddy application.
This module tracks productivity metrics and session data.
"""

import os
import json
import time
import logging
import shutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple

from utils.config import (
    SESSION_LOGS_DIR,
    MIN_SESSION_DURATION,
    DEFAULT_SESSION_DURATION,
    CHECK_IN_INTERVAL
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SessionTracker:
    """Class to handle tracking of focus sessions and productivity metrics."""
    
    def __init__(self, session_id: Optional[str] = None):
        """Initialize the session tracker.
        
        Args:
            session_id (str, optional): Unique identifier for the session.
                If not provided, a timestamp-based ID will be generated.
        """
        self.session_id = session_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_dir = os.path.join(SESSION_LOGS_DIR, self.session_id)
        self.session_file = os.path.join(self.session_dir, "session.json")
        self.analysis_dir = os.path.join(self.session_dir, "analysis")
        
        # Create directories if they don't exist
        os.makedirs(self.session_dir, exist_ok=True)
        os.makedirs(self.analysis_dir, exist_ok=True)
        
        # Initialize session data
        self.session_data = {
            "session_id": self.session_id,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "duration": 0,
            "status": "active",
            "productivity_score": 0,
            "focus_periods": [],
            "distraction_periods": [],
            "check_ins": [],
            "summary": "",
            "tags": [],
            "notes": ""
        }
        
        # Save initial session data
        self._save_session_data()
        
        # Track current state
        self.last_check_in_time = time.time()
        self.last_activity_time = time.time()
        self.current_focus_period_start = time.time()
        self.is_currently_focused = True
        self.total_focus_time = 0
        self.total_distraction_time = 0
        
        logger.info(f"Session tracker initialized with ID: {self.session_id}")
    
    def add_screen_analysis(self, analysis_data: Dict[str, Any]) -> None:
        """Add screen analysis data to the session.
        
        Args:
            analysis_data (dict): Analysis data from the vision analyzer.
        """
        # Save analysis data to a file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        analysis_file = os.path.join(self.analysis_dir, f"analysis_{timestamp}.json")
        
        with open(analysis_file, "w") as f:
            json.dump(analysis_data, f, indent=2)
        
        # Update session data based on analysis
        current_time = time.time()
        is_productive = analysis_data.get("is_productive", False)
        
        # Update focus/distraction periods
        if is_productive != self.is_currently_focused:
            # If state changed, end the current period
            if self.is_currently_focused:
                # End focus period
                focus_duration = current_time - self.current_focus_period_start
                self.total_focus_time += focus_duration
                self.session_data["focus_periods"].append({
                    "start": datetime.fromtimestamp(self.current_focus_period_start).isoformat(),
                    "end": datetime.fromtimestamp(current_time).isoformat(),
                    "duration": focus_duration
                })
            else:
                # End distraction period
                distraction_duration = current_time - self.current_focus_period_start
                self.total_distraction_time += distraction_duration
                self.session_data["distraction_periods"].append({
                    "start": datetime.fromtimestamp(self.current_focus_period_start).isoformat(),
                    "end": datetime.fromtimestamp(current_time).isoformat(),
                    "duration": distraction_duration
                })
            
            # Start new period
            self.current_focus_period_start = current_time
            self.is_currently_focused = is_productive
        
        # Update last activity time
        self.last_activity_time = current_time
        
        # Update productivity score
        self._update_productivity_score()
        
        # Save updated session data
        self._save_session_data()
        
        logger.info(f"Added screen analysis to session {self.session_id}")
    
    def add_check_in(self, check_in_data: Dict[str, Any]) -> None:
        """Add a check-in to the session.
        
        Args:
            check_in_data (dict): Check-in data, including user responses.
        """
        # Add timestamp if not present
        if "timestamp" not in check_in_data:
            check_in_data["timestamp"] = datetime.now().isoformat()
        
        # Add to check-ins list
        self.session_data["check_ins"].append(check_in_data)
        
        # Update last check-in time
        self.last_check_in_time = time.time()
        
        # Save updated session data
        self._save_session_data()
        
        logger.info(f"Added check-in to session {self.session_id}")
    
    def add_note(self, note: str) -> None:
        """Add a note to the session.
        
        Args:
            note (str): Note text to add.
        """
        # Add timestamp to note
        timestamped_note = f"[{datetime.now().isoformat()}] {note}"
        
        # Append to existing notes
        if self.session_data["notes"]:
            self.session_data["notes"] += f"\n{timestamped_note}"
        else:
            self.session_data["notes"] = timestamped_note
        
        # Save updated session data
        self._save_session_data()
        
        logger.info(f"Added note to session {self.session_id}")
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the session.
        
        Args:
            tag (str): Tag to add.
        """
        # Add tag if not already present
        if tag not in self.session_data["tags"]:
            self.session_data["tags"].append(tag)
            
            # Save updated session data
            self._save_session_data()
            
            logger.info(f"Added tag '{tag}' to session {self.session_id}")
    
    def end_session(self, summary: Optional[str] = None) -> Dict[str, Any]:
        """End the current session and generate summary metrics.
        
        Args:
            summary (str, optional): Session summary text.
                If not provided, a default summary will be generated.
                
        Returns:
            dict: Session data with summary metrics.
        """
        # Update end time and duration
        end_time = datetime.now()
        self.session_data["end_time"] = end_time.isoformat()
        
        # Calculate duration
        start_time = datetime.fromisoformat(self.session_data["start_time"])
        duration_seconds = (end_time - start_time).total_seconds()
        self.session_data["duration"] = duration_seconds
        
        # Close any open focus/distraction periods
        current_time = time.time()
        if self.is_currently_focused:
            # End focus period
            focus_duration = current_time - self.current_focus_period_start
            self.total_focus_time += focus_duration
            self.session_data["focus_periods"].append({
                "start": datetime.fromtimestamp(self.current_focus_period_start).isoformat(),
                "end": datetime.fromtimestamp(current_time).isoformat(),
                "duration": focus_duration
            })
        else:
            # End distraction period
            distraction_duration = current_time - self.current_focus_period_start
            self.total_distraction_time += distraction_duration
            self.session_data["distraction_periods"].append({
                "start": datetime.fromtimestamp(self.current_focus_period_start).isoformat(),
                "end": datetime.fromtimestamp(current_time).isoformat(),
                "duration": distraction_duration
            })
        
        # Update final productivity score
        self._update_productivity_score()
        
        # Generate summary if not provided
        if summary:
            self.session_data["summary"] = summary
        else:
            self.session_data["summary"] = self._generate_summary()
        
        # Update status
        self.session_data["status"] = "completed"
        
        # Save final session data
        self._save_session_data()
        
        logger.info(f"Ended session {self.session_id}")
        return self.session_data
    
    def get_session_data(self) -> Dict[str, Any]:
        """Get the current session data.
        
        Returns:
            dict: Current session data.
        """
        return self.session_data
    
    def get_productivity_metrics(self) -> Dict[str, Any]:
        """Get productivity metrics for the current session.
        
        Returns:
            dict: Productivity metrics.
        """
        # Calculate current duration
        if self.session_data["end_time"]:
            end_time = datetime.fromisoformat(self.session_data["end_time"])
        else:
            end_time = datetime.now()
        
        start_time = datetime.fromisoformat(self.session_data["start_time"])
        duration_seconds = (end_time - start_time).total_seconds()
        
        # Calculate focus percentage
        total_time = self.total_focus_time + self.total_distraction_time
        focus_percentage = (self.total_focus_time / max(total_time, 1)) * 100
        
        # Calculate check-in compliance
        expected_check_ins = max(1, int(duration_seconds / CHECK_IN_INTERVAL))
        actual_check_ins = len(self.session_data["check_ins"])
        check_in_compliance = min(100, (actual_check_ins / expected_check_ins) * 100)
        
        return {
            "session_id": self.session_id,
            "duration_seconds": duration_seconds,
            "duration_formatted": str(timedelta(seconds=int(duration_seconds))),
            "focus_time_seconds": self.total_focus_time,
            "focus_time_formatted": str(timedelta(seconds=int(self.total_focus_time))),
            "distraction_time_seconds": self.total_distraction_time,
            "distraction_time_formatted": str(timedelta(seconds=int(self.total_distraction_time))),
            "focus_percentage": focus_percentage,
            "productivity_score": self.session_data["productivity_score"],
            "check_in_count": actual_check_ins,
            "check_in_compliance": check_in_compliance
        }
    
    def should_check_in(self) -> bool:
        """Check if it's time for a check-in.
        
        Returns:
            bool: True if it's time for a check-in, False otherwise.
        """
        current_time = time.time()
        time_since_last_check_in = current_time - self.last_check_in_time
        return time_since_last_check_in >= CHECK_IN_INTERVAL
    
    def is_inactive(self, inactive_threshold: int = 300) -> bool:
        """Check if the session is inactive.
        
        Args:
            inactive_threshold (int): Threshold in seconds to consider a session inactive.
                
        Returns:
            bool: True if the session is inactive, False otherwise.
        """
        current_time = time.time()
        time_since_last_activity = current_time - self.last_activity_time
        return time_since_last_activity >= inactive_threshold
    
    def _update_productivity_score(self) -> None:
        """Update the productivity score based on focus and distraction periods."""
        # Calculate total time
        total_time = self.total_focus_time + self.total_distraction_time
        
        if total_time > 0:
            # Base score is the percentage of time spent focused
            base_score = (self.total_focus_time / total_time) * 100
            
            # Adjust based on session duration
            duration_factor = min(1.0, self.session_data["duration"] / DEFAULT_SESSION_DURATION)
            
            # Calculate final score (0-100)
            score = base_score * duration_factor
            
            # Round to integer
            self.session_data["productivity_score"] = round(score)
    
    def _generate_summary(self) -> str:
        """Generate a summary of the session.
        
        Returns:
            str: Session summary text.
        """
        metrics = self.get_productivity_metrics()
        
        # Create summary text
        summary = f"Focus session completed with a productivity score of {metrics['productivity_score']}/100. "
        summary += f"Duration: {metrics['duration_formatted']}. "
        summary += f"Time spent focused: {metrics['focus_time_formatted']} ({metrics['focus_percentage']:.1f}%). "
        
        # Add tags if present
        if self.session_data["tags"]:
            tags_str = ", ".join(self.session_data["tags"])
            summary += f"Tags: {tags_str}."
        
        return summary
    
    def _save_session_data(self) -> None:
        """Save the session data to a file."""
        with open(self.session_file, "w") as f:
            json.dump(self.session_data, f, indent=2)


def load_session(session_id: str) -> Optional[SessionTracker]:
    """Load a session from disk.
    
    Args:
        session_id (str): Session ID to load.
        
    Returns:
        SessionTracker: Loaded session tracker, or None if not found.
    """
    session_dir = os.path.join(SESSION_LOGS_DIR, session_id)
    session_file = os.path.join(session_dir, "session.json")
    
    if not os.path.exists(session_file):
        logger.error(f"Session file not found: {session_file}")
        return None
    
    try:
        # Create a new session tracker with the given ID
        tracker = SessionTracker(session_id)
        
        # Load session data from file
        with open(session_file, "r") as f:
            tracker.session_data = json.load(f)
        
        # Recalculate focus and distraction times
        tracker.total_focus_time = sum(
            datetime.fromisoformat(period["end"]).timestamp() - 
            datetime.fromisoformat(period["start"]).timestamp()
            for period in tracker.session_data["focus_periods"]
        )
        
        tracker.total_distraction_time = sum(
            datetime.fromisoformat(period["end"]).timestamp() - 
            datetime.fromisoformat(period["start"]).timestamp()
            for period in tracker.session_data["distraction_periods"]
        )
        
        # Set current state based on last period
        if tracker.session_data["focus_periods"] and tracker.session_data["distraction_periods"]:
            last_focus = datetime.fromisoformat(tracker.session_data["focus_periods"][-1]["end"]).timestamp()
            last_distraction = datetime.fromisoformat(tracker.session_data["distraction_periods"][-1]["end"]).timestamp()
            tracker.is_currently_focused = last_focus > last_distraction
        
        # Set last activity and check-in times
        tracker.last_activity_time = time.time()
        if tracker.session_data["check_ins"]:
            last_check_in = tracker.session_data["check_ins"][-1]["timestamp"]
            tracker.last_check_in_time = datetime.fromisoformat(last_check_in).timestamp()
        else:
            tracker.last_check_in_time = time.time()
        
        logger.info(f"Loaded session {session_id}")
        return tracker
        
    except Exception as e:
        logger.error(f"Error loading session {session_id}: {e}")
        return None


def get_recent_sessions(limit: int = 10) -> List[Dict[str, Any]]:
    """Get a list of recent sessions.
    
    Args:
        limit (int): Maximum number of sessions to return.
        
    Returns:
        list: List of session data dictionaries.
    """
    # Get all session directories
    session_dirs = [
        d for d in os.listdir(SESSION_LOGS_DIR)
        if os.path.isdir(os.path.join(SESSION_LOGS_DIR, d)) and d != ".git"
    ]
    
    # Sort by name (which is timestamp-based)
    session_dirs.sort(reverse=True)
    
    # Limit the number of sessions
    session_dirs = session_dirs[:limit]
    
    # Load session data for each directory
    sessions = []
    for session_id in session_dirs:
        session_file = os.path.join(SESSION_LOGS_DIR, session_id, "session.json")
        if os.path.exists(session_file):
            try:
                with open(session_file, "r") as f:
                    session_data = json.load(f)
                sessions.append(session_data)
            except Exception as e:
                logger.error(f"Error loading session {session_id}: {e}")
    
    return sessions


def delete_session(session_id: str) -> bool:
    """Delete a session and its data.
    
    Args:
        session_id (str): Session ID to delete.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    session_dir = os.path.join(SESSION_LOGS_DIR, session_id)
    
    if not os.path.exists(session_dir):
        logger.error(f"Session directory not found: {session_dir}")
        return False
    
    try:
        shutil.rmtree(session_dir)
        logger.info(f"Deleted session {session_id}")
        return True
    except Exception as e:
        logger.error(f"Error deleting session {session_id}: {e}")
        return False


if __name__ == "__main__":
    # Simple test if run directly
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "list":
        # List recent sessions
        sessions = get_recent_sessions()
        print(f"Found {len(sessions)} recent sessions:")
        for session in sessions:
            start_time = session.get("start_time", "Unknown")
            status = session.get("status", "Unknown")
            score = session.get("productivity_score", 0)
            print(f"- {session['session_id']}: {start_time} ({status}) - Score: {score}")
    
    elif len(sys.argv) > 1 and sys.argv[1] == "delete" and len(sys.argv) > 2:
        # Delete a session
        session_id = sys.argv[2]
        success = delete_session(session_id)
        if success:
            print(f"Successfully deleted session {session_id}")
        else:
            print(f"Failed to delete session {session_id}")
    
    else:
        # Create a new test session
        tracker = SessionTracker()
        print(f"Created new test session: {tracker.session_id}")
        
        # Add some test data
        tracker.add_tag("test")
        tracker.add_note("This is a test session")
        
        # Add a mock screen analysis
        tracker.add_screen_analysis({
            "content": "The user is coding in Visual Studio Code",
            "timestamp": datetime.now().isoformat(),
            "image_path": "test.jpg",
            "is_productive": True,
            "detected_apps": ["Visual Studio Code"],
            "detected_activities": ["coding"]
        })
        
        # Add a mock check-in
        tracker.add_check_in({
            "question": "How's your progress?",
            "response": "Good",
            "timestamp": datetime.now().isoformat()
        })
        
        # Wait a bit
        time.sleep(1)
        
        # Add another mock screen analysis
        tracker.add_screen_analysis({
            "content": "The user is browsing social media",
            "timestamp": datetime.now().isoformat(),
            "image_path": "test2.jpg",
            "is_productive": False,
            "detected_apps": ["Chrome"],
            "detected_activities": ["browsing"]
        })
        
        # End the session
        session_data = tracker.end_session()
        
        # Print metrics
        metrics = tracker.get_productivity_metrics()
        print("\nSession metrics:")
        for key, value in metrics.items():
            print(f"- {key}: {value}")
        
        print(f"\nSession summary: {session_data['summary']}")
        print(f"Session data saved to: {tracker.session_file}")
