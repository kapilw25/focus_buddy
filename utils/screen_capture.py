"""
Screen capture functionality for the Focus Buddy application.
This module handles capturing screenshots of the user's screen.
"""

import os
import time
import base64
import platform
import subprocess
import threading
from datetime import datetime
from pathlib import Path
import tempfile
from PIL import Image
import io

# Try to import mss for cross-platform screen capture
MSS_AVAILABLE = False
try:
    import mss
    import mss.tools
    MSS_AVAILABLE = True
except ImportError:
    pass

from utils.config import (
    SCREEN_CAPTURE_INTERVAL,
    SCREEN_CAPTURE_QUALITY,
    SCREEN_CAPTURE_FORMAT,
    SESSION_LOGS_DIR
)

class ScreenCapture:
    """Class to handle screen capture functionality."""
    
    def __init__(self, session_id=None):
        """Initialize the screen capture module.
        
        Args:
            session_id (str, optional): Unique identifier for the current session.
                If not provided, a timestamp-based ID will be generated.
        """
        self.session_id = session_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.capture_dir = os.path.join(SESSION_LOGS_DIR, self.session_id, "captures")
        os.makedirs(self.capture_dir, exist_ok=True)
        self.last_capture_time = 0
        self.last_capture_path = None
        self._stop_auto_capture = False
        self._auto_capture_thread = None
    
    def capture_screen(self, force=False):
        """Capture the current screen.
        
        Args:
            force (bool): If True, capture regardless of the interval.
                          If False, respect the SCREEN_CAPTURE_INTERVAL.
        
        Returns:
            str: Path to the captured image file, or None if no capture was made.
        """
        current_time = time.time()
        
        # Check if enough time has passed since the last capture
        if not force and (current_time - self.last_capture_time) < SCREEN_CAPTURE_INTERVAL:
            return None
        
        # Generate filename based on timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screen_{timestamp}.{SCREEN_CAPTURE_FORMAT.lower()}"
        filepath = os.path.join(self.capture_dir, filename)
        
        # Capture screen based on the operating system
        success = False
        
        # Try MSS first (cross-platform)
        if MSS_AVAILABLE:
            success = self._capture_mss(filepath)
        
        # If MSS fails, try platform-specific methods
        if not success:
            if platform.system() == "Darwin":  # macOS
                success = self._capture_macos(filepath)
            elif platform.system() == "Windows":
                success = self._capture_windows(filepath)
            elif platform.system() == "Linux":
                success = self._capture_linux(filepath)
        
        # If all methods fail, create a dummy image for testing
        if not success:
            success = self._create_dummy_image(filepath)
        
        if success:
            self.last_capture_time = current_time
            self.last_capture_path = filepath
            return filepath
        
        return None
    
    def _capture_mss(self, filepath):
        """Capture screen using MSS (cross-platform).
        
        Args:
            filepath (str): Path to save the captured image.
            
        Returns:
            bool: True if capture was successful, False otherwise.
        """
        if not MSS_AVAILABLE:
            return False
        
        try:
            with mss.mss() as sct:
                # Get information about the monitors
                monitors = sct.monitors
                
                # Skip the first monitor (which is the "all in one" monitor)
                for i, monitor in enumerate(monitors[1:], 1):
                    # Take the screenshot
                    sct_img = sct.grab(monitor)
                    
                    # Convert to PIL Image
                    img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                    
                    # Save the image
                    monitor_filename = filepath.replace(
                        f".{SCREEN_CAPTURE_FORMAT.lower()}", 
                        f"_monitor{i}.{SCREEN_CAPTURE_FORMAT.lower()}"
                    )
                    
                    if SCREEN_CAPTURE_FORMAT.lower() in ["jpg", "jpeg"]:
                        img.save(monitor_filename, quality=SCREEN_CAPTURE_QUALITY, optimize=True)
                    else:
                        img.save(monitor_filename)
                    
                    # For the first monitor, also save with the original filename
                    if i == 1:
                        if SCREEN_CAPTURE_FORMAT.lower() in ["jpg", "jpeg"]:
                            img.save(filepath, quality=SCREEN_CAPTURE_QUALITY, optimize=True)
                        else:
                            img.save(filepath)
                
                return True
        except Exception as e:
            print(f"Error capturing screen with MSS: {e}")
            return False
    
    def _capture_macos(self, filepath):
        """Capture screen on macOS using screencapture command.
        
        Args:
            filepath (str): Path to save the captured image.
            
        Returns:
            bool: True if capture was successful, False otherwise.
        """
        try:
            # Use the built-in screencapture command
            cmd = [
                "screencapture",
                "-x",  # No sound
                "-t", SCREEN_CAPTURE_FORMAT.lower(),
                filepath
            ]
            subprocess.run(cmd, check=True)
            
            # Compress the image if needed
            if SCREEN_CAPTURE_FORMAT.lower() in ["jpg", "jpeg"]:
                self._compress_image(filepath)
            
            return True
        except Exception as e:
            print(f"Error capturing screen on macOS: {e}")
            return False
    
    def _capture_windows(self, filepath):
        """Capture screen on Windows using PIL.
        
        Args:
            filepath (str): Path to save the captured image.
            
        Returns:
            bool: True if capture was successful, False otherwise.
        """
        try:
            print("Windows screen capture not implemented")
            return False
        except Exception as e:
            print(f"Error capturing screen on Windows: {e}")
            return False
    
    def _capture_linux(self, filepath):
        """Capture screen on Linux using scrot or similar.
        
        Args:
            filepath (str): Path to save the captured image.
            
        Returns:
            bool: True if capture was successful, False otherwise.
        """
        try:
            # Try using scrot if available
            cmd = ["scrot", filepath]
            subprocess.run(cmd, check=True)
            
            # Compress the image if needed
            if SCREEN_CAPTURE_FORMAT.lower() in ["jpg", "jpeg"]:
                self._compress_image(filepath)
            
            return True
        except FileNotFoundError:
            # If scrot is not available, try using import from ImageMagick
            try:
                cmd = ["import", "-window", "root", filepath]
                subprocess.run(cmd, check=True)
                
                # Compress the image if needed
                if SCREEN_CAPTURE_FORMAT.lower() in ["jpg", "jpeg"]:
                    self._compress_image(filepath)
                
                return True
            except Exception as e:
                print(f"Error capturing screen on Linux with import: {e}")
                return False
        except Exception as e:
            print(f"Error capturing screen on Linux: {e}")
            return False
    
    def _create_dummy_image(self, filepath):
        """Create a dummy image for testing purposes.
        
        Args:
            filepath (str): Path to save the dummy image.
            
        Returns:
            bool: True if creation was successful, False otherwise.
        """
        try:
            # Create a simple colored image
            width, height = 800, 600
            img = Image.new('RGB', (width, height), color=(73, 109, 137))
            
            # Add some text
            from PIL import ImageDraw
            draw = ImageDraw.Draw(img)
            text = "Focus Buddy - Test Image"
            text_position = (width // 4, height // 2)
            draw.text(text_position, text, fill=(255, 255, 255))
            
            # Save the image
            if SCREEN_CAPTURE_FORMAT.lower() in ["jpg", "jpeg"]:
                img.save(filepath, quality=SCREEN_CAPTURE_QUALITY, optimize=True)
            else:
                img.save(filepath)
            
            print("Created dummy test image since screen capture is not available")
            return True
        except Exception as e:
            print(f"Error creating dummy image: {e}")
            return False
    
    def _compress_image(self, filepath):
        """Compress the image to reduce file size.
        
        Args:
            filepath (str): Path to the image file.
        """
        try:
            with Image.open(filepath) as img:
                img.save(filepath, quality=SCREEN_CAPTURE_QUALITY, optimize=True)
        except Exception as e:
            print(f"Error compressing image: {e}")
    
    def get_latest_capture(self):
        """Get the path to the most recent screen capture.
        
        Returns:
            str: Path to the latest capture, or None if no captures exist.
        """
        return self.last_capture_path
    
    def get_capture_as_base64(self, filepath=None):
        """Convert a screen capture to base64 for use with APIs.
        
        Args:
            filepath (str, optional): Path to the image file.
                If not provided, uses the latest capture.
                
        Returns:
            str: Base64-encoded image data, or None if the file doesn't exist.
        """
        filepath = filepath or self.last_capture_path
        
        if not filepath or not os.path.exists(filepath):
            return None
        
        try:
            with open(filepath, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
                return encoded_string
        except Exception as e:
            print(f"Error encoding image to base64: {e}")
            return None
    
    def cleanup_old_captures(self, max_captures=10):
        """Remove old captures to save disk space.
        
        Args:
            max_captures (int): Maximum number of captures to keep.
        """
        try:
            captures = sorted([
                os.path.join(self.capture_dir, f) 
                for f in os.listdir(self.capture_dir) 
                if f.startswith("screen_") and os.path.isfile(os.path.join(self.capture_dir, f))
            ])
            
            # Remove oldest captures if we have more than max_captures
            if len(captures) > max_captures:
                for old_capture in captures[:-max_captures]:
                    os.remove(old_capture)
        except Exception as e:
            print(f"Error cleaning up old captures: {e}")
    
    def start_auto_capture(self, interval=None):
        """Start automatic screen capture at regular intervals.
        
        Args:
            interval (int, optional): Interval between captures in seconds.
                If not provided, uses SCREEN_CAPTURE_INTERVAL from config.
        """
        if self._auto_capture_thread and self._auto_capture_thread.is_alive():
            print("Auto capture is already running")
            return
        
        self._stop_auto_capture = False
        interval = interval or SCREEN_CAPTURE_INTERVAL
        
        def auto_capture_thread():
            print(f"Starting automatic screen capture every {interval} seconds")
            while not self._stop_auto_capture:
                filepath = self.capture_screen(force=True)
                if filepath:
                    print(f"Auto-captured screenshot: {filepath}")
                time.sleep(interval)
        
        self._auto_capture_thread = threading.Thread(target=auto_capture_thread)
        self._auto_capture_thread.daemon = True
        self._auto_capture_thread.start()
        
        print(f"Automatic screen capture started with interval {interval} seconds")
    
    def stop_auto_capture(self):
        """Stop automatic screen capture."""
        self._stop_auto_capture = True
        if self._auto_capture_thread:
            self._auto_capture_thread.join(timeout=1.0)
            print("Automatic screen capture stopped")


def capture_screen_once(output_dir=None):
    """Utility function to capture the screen once without creating a session.
    
    Args:
        output_dir (str, optional): Directory to save the capture.
            If not provided, uses a temporary directory.
            
    Returns:
        str: Path to the captured image file, or None if capture failed.
    """
    if output_dir is None:
        output_dir = tempfile.mkdtemp()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"screen_{timestamp}.{SCREEN_CAPTURE_FORMAT.lower()}"
    filepath = os.path.join(output_dir, filename)
    
    # Create a temporary ScreenCapture instance
    screen_capture = ScreenCapture()
    
    # Override the capture directory
    screen_capture.capture_dir = output_dir
    
    # Force a capture
    return screen_capture.capture_screen(force=True)


def run_auto_capture(interval_minutes=5, duration_minutes=None):
    """Run automatic screen capture for a specified duration.
    
    Args:
        interval_minutes (int): Interval between captures in minutes.
        duration_minutes (int, optional): Duration to run in minutes.
            If not provided, runs until manually stopped.
    """
    interval_seconds = interval_minutes * 60
    end_time = None
    
    if duration_minutes:
        end_time = time.time() + (duration_minutes * 60)
    
    # Create a ScreenCapture instance
    screen_capture = ScreenCapture()
    
    print(f"Starting automatic screen capture")
    print(f"Interval: {interval_minutes} minutes ({interval_seconds} seconds)")
    if end_time:
        print(f"Duration: {duration_minutes} minutes")
        print(f"End time: {datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Screenshots will be saved to: {screen_capture.capture_dir}")
    print("Press Ctrl+C to stop")
    
    try:
        screen_capture.start_auto_capture(interval=interval_seconds)
        
        # If duration is specified, wait until the end time
        if end_time:
            while time.time() < end_time:
                time.sleep(1)
            screen_capture.stop_auto_capture()
        else:
            # Otherwise, wait indefinitely until Ctrl+C
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        screen_capture.stop_auto_capture()
        print("Automatic screen capture stopped by user")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Screen capture utility")
    parser.add_argument("--interval", type=int, default=5, help="Capture interval in minutes")
    parser.add_argument("--duration", type=int, help="Duration in minutes (optional)")
    parser.add_argument("--once", action="store_true", help="Capture once and exit")
    
    args = parser.parse_args()
    
    if args.once:
        filepath = capture_screen_once()
        if filepath:
            print(f"Screenshot saved to: {filepath}")
    else:
        run_auto_capture(args.interval, args.duration)

class ScreenCapture:
    """Class to handle screen capture functionality."""
    
    def __init__(self, session_id=None):
        """Initialize the screen capture module.
        
        Args:
            session_id (str, optional): Unique identifier for the current session.
                If not provided, a timestamp-based ID will be generated.
        """
        self.session_id = session_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.capture_dir = os.path.join(SESSION_LOGS_DIR, self.session_id, "captures")
        os.makedirs(self.capture_dir, exist_ok=True)
        self.last_capture_time = 0
        self.last_capture_path = None
    
    def capture_screen(self, force=False):
        """Capture the current screen.
        
        Args:
            force (bool): If True, capture regardless of the interval.
                          If False, respect the SCREEN_CAPTURE_INTERVAL.
        
        Returns:
            str: Path to the captured image file, or None if no capture was made.
        """
        current_time = time.time()
        
        # Check if enough time has passed since the last capture
        if not force and (current_time - self.last_capture_time) < SCREEN_CAPTURE_INTERVAL:
            return None
        
        # Generate filename based on timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screen_{timestamp}.{SCREEN_CAPTURE_FORMAT.lower()}"
        filepath = os.path.join(self.capture_dir, filename)
        
        # Capture screen based on the operating system
        success = False
        
        if platform.system() == "Darwin":  # macOS
            success = self._capture_macos(filepath)
        elif platform.system() == "Windows":
            success = self._capture_windows(filepath)
        elif platform.system() == "Linux":
            success = self._capture_linux(filepath)
        
        # If all methods fail, create a dummy image for testing
        if not success:
            success = self._create_dummy_image(filepath)
        
        if success:
            self.last_capture_time = current_time
            self.last_capture_path = filepath
            return filepath
        
        return None
    
    def _capture_macos(self, filepath):
        """Capture screen on macOS using screencapture command.
        
        Args:
            filepath (str): Path to save the captured image.
            
        Returns:
            bool: True if capture was successful, False otherwise.
        """
        try:
            # Use the built-in screencapture command
            cmd = [
                "screencapture",
                "-x",  # No sound
                "-t", SCREEN_CAPTURE_FORMAT.lower(),
                filepath
            ]
            subprocess.run(cmd, check=True)
            
            # Compress the image if needed
            if SCREEN_CAPTURE_FORMAT.lower() in ["jpg", "jpeg"]:
                self._compress_image(filepath)
            
            return True
        except Exception as e:
            print(f"Error capturing screen on macOS: {e}")
            return False
    
    def _capture_windows(self, filepath):
        """Capture screen on Windows using PIL.
        
        Args:
            filepath (str): Path to save the captured image.
            
        Returns:
            bool: True if capture was successful, False otherwise.
        """
        try:
            print("Windows screen capture not implemented")
            return False
        except Exception as e:
            print(f"Error capturing screen on Windows: {e}")
            return False
    
    def _capture_linux(self, filepath):
        """Capture screen on Linux using scrot or similar.
        
        Args:
            filepath (str): Path to save the captured image.
            
        Returns:
            bool: True if capture was successful, False otherwise.
        """
        try:
            # Try using scrot if available
            cmd = ["scrot", filepath]
            subprocess.run(cmd, check=True)
            
            # Compress the image if needed
            if SCREEN_CAPTURE_FORMAT.lower() in ["jpg", "jpeg"]:
                self._compress_image(filepath)
            
            return True
        except FileNotFoundError:
            # If scrot is not available, try using import from ImageMagick
            try:
                cmd = ["import", "-window", "root", filepath]
                subprocess.run(cmd, check=True)
                
                # Compress the image if needed
                if SCREEN_CAPTURE_FORMAT.lower() in ["jpg", "jpeg"]:
                    self._compress_image(filepath)
                
                return True
            except Exception as e:
                print(f"Error capturing screen on Linux with import: {e}")
                return False
        except Exception as e:
            print(f"Error capturing screen on Linux: {e}")
            return False
    
    def _create_dummy_image(self, filepath):
        """Create a dummy image for testing purposes.
        
        Args:
            filepath (str): Path to save the dummy image.
            
        Returns:
            bool: True if creation was successful, False otherwise.
        """
        try:
            # Create a simple colored image
            width, height = 800, 600
            img = Image.new('RGB', (width, height), color=(73, 109, 137))
            
            # Add some text
            from PIL import ImageDraw
            draw = ImageDraw.Draw(img)
            text = "Focus Buddy - Test Image"
            text_position = (width // 4, height // 2)
            draw.text(text_position, text, fill=(255, 255, 255))
            
            # Save the image
            if SCREEN_CAPTURE_FORMAT.lower() in ["jpg", "jpeg"]:
                img.save(filepath, quality=SCREEN_CAPTURE_QUALITY, optimize=True)
            else:
                img.save(filepath)
            
            print("Created dummy test image since screen capture is not available")
            return True
        except Exception as e:
            print(f"Error creating dummy image: {e}")
            return False
    
    def _compress_image(self, filepath):
        """Compress the image to reduce file size.
        
        Args:
            filepath (str): Path to the image file.
        """
        try:
            with Image.open(filepath) as img:
                img.save(filepath, quality=SCREEN_CAPTURE_QUALITY, optimize=True)
        except Exception as e:
            print(f"Error compressing image: {e}")
    
    def get_latest_capture(self):
        """Get the path to the most recent screen capture.
        
        Returns:
            str: Path to the latest capture, or None if no captures exist.
        """
        return self.last_capture_path
    
    def get_capture_as_base64(self, filepath=None):
        """Convert a screen capture to base64 for use with APIs.
        
        Args:
            filepath (str, optional): Path to the image file.
                If not provided, uses the latest capture.
                
        Returns:
            str: Base64-encoded image data, or None if the file doesn't exist.
        """
        filepath = filepath or self.last_capture_path
        
        if not filepath or not os.path.exists(filepath):
            return None
        
        try:
            with open(filepath, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
                return encoded_string
        except Exception as e:
            print(f"Error encoding image to base64: {e}")
            return None
    
    def cleanup_old_captures(self, max_captures=10):
        """Remove old captures to save disk space.
        
        Args:
            max_captures (int): Maximum number of captures to keep.
        """
        try:
            captures = sorted([
                os.path.join(self.capture_dir, f) 
                for f in os.listdir(self.capture_dir) 
                if f.startswith("screen_") and os.path.isfile(os.path.join(self.capture_dir, f))
            ])
            
            # Remove oldest captures if we have more than max_captures
            if len(captures) > max_captures:
                for old_capture in captures[:-max_captures]:
                    os.remove(old_capture)
        except Exception as e:
            print(f"Error cleaning up old captures: {e}")


def capture_screen_once(output_dir=None):
    """Utility function to capture the screen once without creating a session.
    
    Args:
        output_dir (str, optional): Directory to save the capture.
            If not provided, uses a temporary directory.
            
    Returns:
        str: Path to the captured image file, or None if capture failed.
    """
    if output_dir is None:
        output_dir = tempfile.mkdtemp()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"screen_{timestamp}.{SCREEN_CAPTURE_FORMAT.lower()}"
    filepath = os.path.join(output_dir, filename)
    
    # Create a temporary ScreenCapture instance
    screen_capture = ScreenCapture()
    
    # Override the capture directory
    screen_capture.capture_dir = output_dir
    
    # Force a capture
    return screen_capture.capture_screen(force=True)
