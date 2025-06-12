"""
Unit tests for the session view UI module.
This is a temporary test file that will be deleted after testing.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock, ANY
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import io

# Set testing environment variable
os.environ['TESTING'] = 'True'

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the module we want to test
from ui.session_view import (
    render_session_history,
    render_session_details,
    render_productivity_timeline,
    render_session_screenshots,
    export_session_data
)

class TestSessionViewUI(unittest.TestCase):
    """Test cases for the session view UI components."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock streamlit
        self.st_patcher = patch('ui.session_view.st')
        self.mock_st = self.st_patcher.start()
        
        # Mock matplotlib
        self.plt_patcher = patch('ui.session_view.plt')
        self.mock_plt = self.plt_patcher.start()
        
        # Mock PIL Image
        self.image_patcher = patch('ui.session_view.Image')
        self.mock_image = self.image_patcher.start()
        
        # Mock session tracker functions
        self.get_recent_sessions_patcher = patch('ui.session_view.get_recent_sessions')
        self.mock_get_recent_sessions = self.get_recent_sessions_patcher.start()
        
        self.load_session_patcher = patch('ui.session_view.load_session')
        self.mock_load_session = self.load_session_patcher.start()
        
        # Set up mock returns
        self.mock_column = MagicMock()
        self.mock_st.columns.return_value = [self.mock_column, self.mock_column, self.mock_column]
        self.mock_st.selectbox.return_value = "test_session_id"
        
        # Set up mock session data
        self.mock_session_data = {
            "session_id": "test_session_id",
            "start_time": datetime.now().isoformat(),
            "end_time": (datetime.now() + timedelta(hours=2)).isoformat(),
            "duration": 7200,
            "status": "completed",
            "productivity_score": 85,
            "focus_periods": [
                {
                    "start": datetime.now().isoformat(),
                    "end": (datetime.now() + timedelta(minutes=30)).isoformat(),
                    "duration": 1800
                }
            ],
            "distraction_periods": [
                {
                    "start": (datetime.now() + timedelta(minutes=30)).isoformat(),
                    "end": (datetime.now() + timedelta(minutes=45)).isoformat(),
                    "duration": 900
                }
            ],
            "check_ins": [
                {
                    "question": "How's your focus?",
                    "response": "Good",
                    "timestamp": datetime.now().isoformat()
                }
            ],
            "summary": "Test session summary",
            "tags": ["test", "coding"],
            "notes": "Test session notes"
        }
        
        # Set up mock metrics
        self.mock_metrics = {
            "session_id": "test_session_id",
            "duration_seconds": 7200,
            "duration_formatted": "2:00:00",
            "focus_time_seconds": 5400,
            "focus_time_formatted": "1:30:00",
            "distraction_time_seconds": 1800,
            "distraction_time_formatted": "0:30:00",
            "focus_percentage": 75.0,
            "productivity_score": 85,
            "check_in_count": 1,
            "check_in_compliance": 100.0
        }
        
        # Set up mock session tracker
        self.mock_session_tracker = MagicMock()
        self.mock_session_tracker.get_session_data.return_value = self.mock_session_data
        self.mock_session_tracker.get_productivity_metrics.return_value = self.mock_metrics
        
        # Set up mock load_session return
        self.mock_load_session.return_value = self.mock_session_tracker
        
        # Set up mock recent sessions
        self.mock_get_recent_sessions.return_value = [self.mock_session_data]
        
        # Mock os.path functions
        self.os_path_exists_patcher = patch('os.path.exists')
        self.mock_os_path_exists = self.os_path_exists_patcher.start()
        self.mock_os_path_exists.return_value = True
        
        self.os_listdir_patcher = patch('os.listdir')
        self.mock_os_listdir = self.os_listdir_patcher.start()
        self.mock_os_listdir.return_value = ["screen_20250612_104511.jpg"]
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.st_patcher.stop()
        self.plt_patcher.stop()
        self.image_patcher.stop()
        self.get_recent_sessions_patcher.stop()
        self.load_session_patcher.stop()
        self.os_path_exists_patcher.stop()
        self.os_listdir_patcher.stop()
        
        # Clean up environment variable
        if 'TESTING' in os.environ:
            del os.environ['TESTING']
    
    def test_render_session_history(self):
        """Test rendering the session history page."""
        # Call the function
        render_session_history()
        
        # Check that the title was set
        self.mock_st.title.assert_called_with("Focus Buddy Session History")
        
        # Check that get_recent_sessions was called
        self.mock_get_recent_sessions.assert_called_once()
        
        # Check that a dataframe was created
        self.mock_st.dataframe.assert_called_once()
        
        # Check that a selectbox was created
        self.mock_st.selectbox.assert_called_once()
    
    def test_render_session_details(self):
        """Test rendering session details."""
        # Call the function
        render_session_details("test_session_id")
        
        # In testing mode, it should just write a message
        self.mock_st.write.assert_called_with("Session details for test_session_id")
    
    def test_render_productivity_timeline(self):
        """Test rendering productivity timeline."""
        # Call the function
        render_productivity_timeline(self.mock_session_data)
        
        # Check that st.write was called (in testing mode)
        self.mock_st.write.assert_called_with("Productivity timeline visualization")
    
    def test_render_session_screenshots(self):
        """Test rendering session screenshots."""
        # Call the function
        render_session_screenshots("test_session_id")
        
        # In testing mode, it should just write a message
        self.mock_st.write.assert_called_with("Session screenshots would be displayed here")
    
    def test_export_session_data(self):
        """Test exporting session data."""
        # Call the function
        result = export_session_data("test_session_id")
        
        # Check that load_session was called
        self.mock_load_session.assert_called_with("test_session_id")
        
        # Check that session data was retrieved
        self.mock_session_tracker.get_session_data.assert_called()
        self.mock_session_tracker.get_productivity_metrics.assert_called()
        
        # Check that a result was returned
        self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()
