"""
Test script to verify vision analyzer functionality.
"""

import os
import json
from utils.screen_capture import ScreenCapture
from core.vision_analyzer import VisionAnalyzer
from datetime import datetime

def test_vision_analyzer():
    print("Testing vision analyzer functionality...")
    
    # Create a screen capture instance
    screen_capture = ScreenCapture()
    
    # Force a capture
    print("Capturing screenshot...")
    screenshot_path = screen_capture.capture_screen(force=True)
    
    if not screenshot_path:
        print("Failed to capture screenshot")
        return
    
    print(f"Screenshot captured: {screenshot_path}")
    
    # Create a vision analyzer instance
    vision_analyzer = VisionAnalyzer()
    
    # Analyze the screenshot
    print("Analyzing screenshot with GPT-4o...")
    analysis = vision_analyzer.analyze_image(screenshot_path)
    
    # Print the analysis
    print("\nAnalysis results:")
    print(f"Content: {analysis['content']}")
    print(f"Is productive: {analysis['is_productive']}")
    print(f"Detected apps: {analysis['detected_apps']}")
    print(f"Detected activities: {analysis['detected_activities']}")
    
    # Save the analysis to a file
    output_file = f"test_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(analysis, f, indent=2)
    
    print(f"\nAnalysis saved to: {output_file}")

if __name__ == "__main__":
    test_vision_analyzer()
