"""
Integration test for Focus Buddy application.
This test verifies that the core components work together correctly.
"""

import os
import sys
import unittest
import tempfile
import shutil
from datetime import datetime
import time
from unittest.mock import patch

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the modules we want to test
from utils.screen_capture import ScreenCapture
from core.vision_analyzer import VisionAnalyzer
from core.session_tracker import SessionTracker
from utils.config import SESSION_LOGS_DIR

class FocusBuddyIntegrationTest(unittest.TestCase):
    """Integration test for Focus Buddy application."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test sessions
        self.temp_dir = tempfile.mkdtemp()
        
        # Patch SESSION_LOGS_DIR for testing
        self.session_logs_patcher = patch('utils.config.SESSION_LOGS_DIR', self.temp_dir)
        self.session_logs_patcher.start()
        
        # Also patch it in the session_tracker module
        self.session_tracker_patcher = patch('core.session_tracker.SESSION_LOGS_DIR', self.temp_dir)
        self.session_tracker_patcher.start()
        
        # Create a test session ID
        self.session_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Initialize components
        self.screen_capture = ScreenCapture(self.session_id)
        self.vision_analyzer = VisionAnalyzer()
        self.session_tracker = SessionTracker(self.session_id)
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Stop the patchers
        self.session_logs_patcher.stop()
        self.session_tracker_patcher.stop()
        
        # Remove the temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_full_workflow(self):
        """Test the full workflow from screen capture to session tracking."""
        # 1. Capture a screenshot
        screenshot_path = self.screen_capture.capture_screen(force=True)
        self.assertIsNotNone(screenshot_path, "Screenshot capture failed")
        self.assertTrue(os.path.exists(screenshot_path), "Screenshot file does not exist")
        
        # 2. Create a mock analysis (to avoid actual API calls)
        mock_analysis = {
            "content": "The user is coding in Visual Studio Code",
            "timestamp": datetime.now().isoformat(),
            "image_path": screenshot_path,
            "is_productive": True,
            "detected_apps": ["Visual Studio Code"],
            "detected_activities": ["coding"]
        }
        
        # 3. Add the analysis to the session tracker
        self.session_tracker.add_screen_analysis(mock_analysis)
        
        # 4. Add a check-in
        self.session_tracker.add_check_in({
            "question": "How's your progress?",
            "response": "Good",
            "timestamp": datetime.now().isoformat()
        })
        
        # 5. Add a tag and note
        self.session_tracker.add_tag("integration_test")
        self.session_tracker.add_note("Integration test note")
        
        # 6. Get session data and verify
        session_data = self.session_tracker.get_session_data()
        self.assertEqual(session_data["session_id"], self.session_id)
        self.assertEqual(session_data["status"], "active")
        self.assertEqual(len(session_data["check_ins"]), 1)
        self.assertEqual(session_data["tags"], ["integration_test"])
        self.assertTrue("Integration test note" in session_data["notes"])
        
        # 7. Add a distraction analysis
        mock_distraction = {
            "content": "The user is browsing social media",
            "timestamp": datetime.now().isoformat(),
            "image_path": screenshot_path,
            "is_productive": False,
            "detected_apps": ["Chrome"],
            "detected_activities": ["browsing"]
        }
        
        # Wait a moment to ensure timestamps are different
        time.sleep(0.1)
        self.session_tracker.add_screen_analysis(mock_distraction)
        
        # 8. End the session
        end_summary = self.session_tracker.end_session("Test session completed")
        
        # 9. Verify final session data
        self.assertEqual(end_summary["status"], "completed")
        self.assertIsNotNone(end_summary["end_time"])
        self.assertTrue(end_summary["duration"] > 0)
        self.assertEqual(end_summary["summary"], "Test session completed")
        
        # 10. Get productivity metrics
        metrics = self.session_tracker.get_productivity_metrics()
        self.assertTrue("productivity_score" in metrics)
        self.assertTrue("focus_percentage" in metrics)
        self.assertTrue("duration_seconds" in metrics)
    
    def test_screen_capture_only(self):
        """Test that screen capture works independently."""
        # Capture a screenshot
        screenshot_path = self.screen_capture.capture_screen(force=True)
        self.assertIsNotNone(screenshot_path, "Screenshot capture failed")
        self.assertTrue(os.path.exists(screenshot_path), "Screenshot file does not exist")
        
        # Get all screenshots
        all_screenshots = self.screen_capture.get_all_screenshots()
        self.assertTrue(len(all_screenshots) > 0, "No screenshots returned")
        
        # Get base64 encoding
        base64_data = self.screen_capture.get_capture_as_base64()
        self.assertIsNotNone(base64_data, "Base64 encoding failed")
    
    def test_session_tracker_only(self):
        """Test that session tracker works independently."""
        # Add a tag and note
        self.session_tracker.add_tag("test_tag")
        self.session_tracker.add_note("Test note")
        
        # Check if it's time for a check-in
        should_check_in = self.session_tracker.should_check_in()
        self.assertIsInstance(should_check_in, bool)
        
        # Check if session is inactive
        is_inactive = self.session_tracker.is_inactive(inactive_threshold=0)
        self.assertTrue(is_inactive, "New session should be considered inactive")
        
        # End the session
        session_data = self.session_tracker.end_session()
        
        # Verify session data was saved
        session_file = os.path.join(self.temp_dir, self.session_id, "session.json")
        self.assertTrue(os.path.exists(session_file), "Session file was not created")


if __name__ == "__main__":
    unittest.main()
