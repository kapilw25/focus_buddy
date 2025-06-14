"""
Test script to verify screen capture functionality.
"""

import os
from utils.screen_capture import ScreenCapture
from datetime import datetime

def test_screen_capture():
    print("Testing screen capture functionality...")
    
    # Create a screen capture instance
    screen_capture = ScreenCapture()
    
    # Force a capture
    print("Attempting to capture screen...")
    screenshot_path = screen_capture.capture_screen(force=True)
    
    if screenshot_path:
        print(f"Screenshot captured successfully: {screenshot_path}")
        print(f"File exists: {os.path.exists(screenshot_path)}")
        print(f"File size: {os.path.getsize(screenshot_path)} bytes")
        
        # Get all screenshots (main and individual monitors)
        all_screenshots = screen_capture.get_all_screenshots()
        print(f"All screenshots captured: {len(all_screenshots)}")
        for i, path in enumerate(all_screenshots):
            print(f"  Screenshot {i+1}: {path}")
            print(f"  Exists: {os.path.exists(path)}")
            print(f"  Size: {os.path.getsize(path)} bytes")
    else:
        print("Failed to capture screenshot")

if __name__ == "__main__":
    test_screen_capture()
