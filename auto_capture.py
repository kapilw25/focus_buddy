"""
Simple script to run automatic screen capture
"""

from utils.screen_capture import capture_screen_once

if __name__ == "__main__":
    # Capture screen once and print the path
    filepath = capture_screen_once()
    if filepath:
        print(f"Screenshot saved to: {filepath}")
    else:
        print("Failed to capture screenshot")
