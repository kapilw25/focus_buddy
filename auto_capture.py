"""
Simple script to run automatic screen capture
"""

from utils.screen_capture import run_auto_capture

if __name__ == "__main__":
    # Run automatic screen capture every 5 minutes
    # Press Ctrl+C to stop
    run_auto_capture(interval_minutes=5)
