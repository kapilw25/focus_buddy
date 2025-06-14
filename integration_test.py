"""
Integration test for Focus Buddy application.
This test verifies that the app.py functionality works correctly with real API calls.
"""

import os
import sys
import unittest
import tempfile
import shutil
from datetime import datetime
import time
import threading
import json

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the modules we want to test
from utils.screen_capture import ScreenCapture
from core.vision_analyzer import VisionAnalyzer
from core.session_tracker import SessionTracker
from utils.config import SESSION_LOGS_DIR
from ui.dashboard import capture_and_analyze_screen

class AppIntegrationTest(unittest.TestCase):
    """Integration test for app.py functionality with real API calls."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a test session ID
        self.session_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Initialize components directly (no mocking)
        self.screen_capture = ScreenCapture(self.session_id)
        self.vision_analyzer = VisionAnalyzer()
        self.session_tracker = SessionTracker(self.session_id)
        
        # Create output directory for results
        self.output_dir = os.path.join(os.path.dirname(__file__), "test_results")
        os.makedirs(self.output_dir, exist_ok=True)
    
    def test_app_multi_screen_capture_and_analysis(self):
        """Test capturing and analyzing all connected screens with real GPT-4o API calls."""
        print("\n=== Testing Multi-Screen Capture and Real-time GPT-4o Analysis ===")
        
        # 1. Use the dashboard's capture_and_analyze_screen function (same as used in app.py)
        print("Capturing screenshots from all connected screens...")
        analysis = capture_and_analyze_screen()
        
        # 2. Verify we got a valid analysis
        self.assertIsNotNone(analysis, "Screen capture and analysis failed")
        
        # 3. Print the analysis content to console in real-time
        print("\n=== GPT-4o Analysis of Your Screens ===")
        print(analysis["content"])
        
        # 4. Show detected apps and activities
        if analysis.get("detected_apps"):
            print(f"\nDetected applications: {', '.join(analysis['detected_apps'])}")
        
        if analysis.get("detected_activities"):
            print(f"Detected activities: {', '.join(analysis['detected_activities'])}")
        
        # 5. Show productivity assessment
        if analysis.get("is_productive", False):
            print("\nGPT-4o assessment: This appears to be productive work.")
        else:
            print("\nGPT-4o assessment: This might be a distraction from your focus.")
        
        # 6. Save the analysis to a file for review
        result_file = os.path.join(self.output_dir, f"screen_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(result_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        print(f"\nAnalysis saved to: {result_file}")
        
        # 7. Verify we have paths to all screenshots
        if "all_screenshots" in analysis:
            print(f"\nCaptured {len(analysis['all_screenshots'])} screen(s)")
            for i, screenshot in enumerate(analysis["all_screenshots"]):
                print(f"  Screen {i+1}: {os.path.basename(screenshot)}")
                self.assertTrue(os.path.exists(screenshot), f"Screenshot {i+1} does not exist")
        else:
            self.assertTrue("image_path" in analysis, "No image path in analysis")
            self.assertTrue(os.path.exists(analysis["image_path"]), "Screenshot does not exist")
            print(f"\nCaptured 1 screen: {os.path.basename(analysis['image_path'])}")
        
        # 8. Add the analysis to the session tracker (as app.py would do)
        self.session_tracker.add_screen_analysis(analysis)
        
        # 9. Get session data and verify
        session_data = self.session_tracker.get_session_data()
        self.assertEqual(session_data["session_id"], self.session_id)
        self.assertEqual(session_data["status"], "active")
        
        # 10. Get productivity metrics
        metrics = self.session_tracker.get_productivity_metrics()
        print(f"\nProductivity metrics:")
        print(f"  Score: {metrics['productivity_score']}/100")
        print(f"  Focus percentage: {metrics['focus_percentage']}%")
        
        print("\nTest completed successfully!")

    def test_continuous_screen_monitoring(self):
        """Test continuous monitoring of screens for a short period."""
        print("\n=== Testing Continuous Screen Monitoring with Real-time Analysis ===")
        
        # Number of captures to perform
        num_captures = 3
        # Seconds between captures
        capture_interval = 5
        
        analyses = []
        stop_thread = False
        
        def capture_thread():
            for i in range(num_captures):
                if stop_thread:
                    break
                    
                print(f"\nCapture {i+1}/{num_captures}...")
                analysis = capture_and_analyze_screen()
                
                if analysis:
                    analyses.append(analysis)
                    print(f"\n=== GPT-4o Analysis {i+1}/{num_captures} ===")
                    print(analysis["content"])
                    
                    # Add to session tracker
                    self.session_tracker.add_screen_analysis(analysis)
                    
                    # Wait for next capture
                    if i < num_captures - 1:
                        print(f"Waiting {capture_interval} seconds for next capture...")
                        time.sleep(capture_interval)
        
        # Start capture thread
        thread = threading.Thread(target=capture_thread)
        thread.daemon = True
        thread.start()
        
        try:
            # Wait for thread to complete
            thread.join(timeout=(num_captures * capture_interval) + 30)  # Add extra time for API calls
            
            # Check results
            self.assertTrue(len(analyses) > 0, "No analyses were collected")
            
            # Get final productivity metrics
            metrics = self.session_tracker.get_productivity_metrics()
            print(f"\nFinal productivity metrics after {len(analyses)} captures:")
            print(f"  Score: {metrics['productivity_score']}/100")
            print(f"  Focus percentage: {metrics['focus_percentage']}%")
            
            # Save all analyses to a file
            result_file = os.path.join(self.output_dir, f"continuous_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            with open(result_file, 'w') as f:
                json.dump(analyses, f, indent=2)
            
            print(f"\nAll analyses saved to: {result_file}")
            print("\nTest completed successfully!")
            
        except KeyboardInterrupt:
            print("\nTest interrupted by user")
            stop_thread = True
            thread.join(timeout=2)


# Original integration tests (kept for reference)
class FocusBuddyIntegrationTest(unittest.TestCase):
    """Original integration tests for Focus Buddy components."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test sessions
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a test session ID
        self.session_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Initialize components
        self.screen_capture = ScreenCapture(self.session_id)
        self.vision_analyzer = VisionAnalyzer()
        self.session_tracker = SessionTracker(self.session_id)
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Remove the temporary directory
        shutil.rmtree(self.temp_dir)
    
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


if __name__ == "__main__":
    # Run only the app integration tests by default
    suite = unittest.TestSuite()
    suite.addTest(AppIntegrationTest("test_app_multi_screen_capture_and_analysis"))
    suite.addTest(AppIntegrationTest("test_continuous_screen_monitoring"))
    
    runner = unittest.TextTestRunner()
    runner.run(suite)
