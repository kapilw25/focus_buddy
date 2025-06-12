"""
Vision Analyzer for the Focus Buddy application.
This module processes screen captures with GPT-4 Vision to extract context and insights.
"""

import os
import json
import base64
import logging
from datetime import datetime
import time
from typing import Dict, List, Optional, Any, Tuple

from openai import OpenAI

from utils.config import (
    OPENAI_API_KEY,
    GPT4O_MODEL,
    SCREEN_CAPTURE_INTERVAL
)
from utils.prompts import SCREEN_ANALYSIS_PROMPT

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VisionAnalyzer:
    """Class to handle screen capture analysis using GPT-4 Vision."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the vision analyzer.
        
        Args:
            api_key (str, optional): OpenAI API key. If not provided, uses the key from config.
        """
        self.api_key = api_key or OPENAI_API_KEY
        self.client = OpenAI(api_key=self.api_key)
        self.last_analysis_time = 0
        self.last_analysis_result = None
        self.analysis_history = []
        
    def analyze_image(self, image_path: str, prompt: Optional[str] = None) -> Dict[str, Any]:
        """Analyze a single image using GPT-4 Vision.
        
        Args:
            image_path (str): Path to the image file.
            prompt (str, optional): Custom prompt for analysis. If not provided, uses default.
            
        Returns:
            dict: Analysis results containing the following keys:
                - 'content': The text content of the analysis
                - 'timestamp': When the analysis was performed
                - 'image_path': Path to the analyzed image
                - 'is_productive': Boolean indicating if the content appears productive
                - 'detected_apps': List of detected applications
                - 'detected_activities': List of detected activities
        """
        if not os.path.exists(image_path):
            logger.error(f"Image file not found: {image_path}")
            return {
                "content": "Error: Image file not found",
                "timestamp": datetime.now().isoformat(),
                "image_path": image_path,
                "is_productive": False,
                "detected_apps": [],
                "detected_activities": []
            }
        
        # Use default prompt if none provided
        if prompt is None:
            prompt = SCREEN_ANALYSIS_PROMPT
        
        try:
            # Encode image to base64
            base64_image = self._encode_image(image_path)
            
            # Call OpenAI API with the correct format for vision analysis (new API format)
            response = self.client.chat.completions.create(
                model=GPT4O_MODEL,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an AI assistant that analyzes screenshots to understand user activity."
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=300
            )
            
            # Extract content from response (new API format)
            content = response.choices[0].message.content
            
            # Basic analysis of productivity (simple keyword matching)
            is_productive = self._assess_productivity(content)
            
            # Extract detected applications and activities
            detected_apps = self._extract_applications(content)
            detected_activities = self._extract_activities(content)
            
            # Create result dictionary
            result = {
                "content": content,
                "timestamp": datetime.now().isoformat(),
                "image_path": image_path,
                "is_productive": is_productive,
                "detected_apps": detected_apps,
                "detected_activities": detected_activities
            }
            
            # Update last analysis
            self.last_analysis_time = time.time()
            self.last_analysis_result = result
            self.analysis_history.append(result)
            
            # Limit history size
            if len(self.analysis_history) > 10:
                self.analysis_history.pop(0)
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            return {
                "content": f"Error analyzing image: {str(e)}",
                "timestamp": datetime.now().isoformat(),
                "image_path": image_path,
                "is_productive": False,
                "detected_apps": [],
                "detected_activities": []
            }
    
    def _encode_image(self, image_path: str) -> str:
        """Encode an image file to base64.
        
        Args:
            image_path (str): Path to the image file.
            
        Returns:
            str: Base64-encoded image data.
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    
    def analyze_image_batch(self, image_paths: List[str], prompt: Optional[str] = None) -> List[Dict[str, Any]]:
        """Analyze multiple images in batch.
        
        Args:
            image_paths (list): List of paths to image files.
            prompt (str, optional): Custom prompt for analysis. If not provided, uses default.
            
        Returns:
            list: List of analysis results for each image.
        """
        results = []
        for image_path in image_paths:
            result = self.analyze_image(image_path, prompt)
            results.append(result)
        return results
    
    def get_productivity_summary(self, time_period: int = 3600) -> Dict[str, Any]:
        """Generate a summary of productivity over a time period.
        
        Args:
            time_period (int): Time period in seconds to analyze (default: 1 hour).
            
        Returns:
            dict: Summary of productivity including:
                - 'productive_percentage': Percentage of time spent productively
                - 'common_apps': Most commonly detected applications
                - 'common_activities': Most commonly detected activities
                - 'summary_text': Text summary of productivity
        """
        # Filter history to the specified time period
        current_time = time.time()
        relevant_history = [
            entry for entry in self.analysis_history 
            if current_time - datetime.fromisoformat(entry["timestamp"]).timestamp() <= time_period
        ]
        
        if not relevant_history:
            return {
                "productive_percentage": 0,
                "common_apps": [],
                "common_activities": [],
                "summary_text": "No data available for the specified time period."
            }
        
        # Calculate productive percentage
        productive_entries = [entry for entry in relevant_history if entry["is_productive"]]
        productive_percentage = (len(productive_entries) / len(relevant_history)) * 100
        
        # Get common apps and activities
        all_apps = []
        all_activities = []
        
        for entry in relevant_history:
            all_apps.extend(entry["detected_apps"])
            all_activities.extend(entry["detected_activities"])
        
        # Count occurrences
        app_counts = {}
        for app in all_apps:
            app_counts[app] = app_counts.get(app, 0) + 1
        
        activity_counts = {}
        for activity in all_activities:
            activity_counts[activity] = activity_counts.get(activity, 0) + 1
        
        # Sort by count
        common_apps = sorted(app_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        common_activities = sorted(activity_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Generate summary text
        if productive_percentage >= 75:
            productivity_level = "highly productive"
        elif productive_percentage >= 50:
            productivity_level = "moderately productive"
        elif productive_percentage >= 25:
            productivity_level = "somewhat productive"
        else:
            productivity_level = "not very productive"
        
        summary_text = f"You've been {productivity_level} in the last {time_period // 60} minutes, "
        
        if common_apps:
            top_app = common_apps[0][0]
            summary_text += f"primarily using {top_app}. "
        
        if common_activities:
            top_activity = common_activities[0][0]
            summary_text += f"Your main activity has been {top_activity}."
        
        return {
            "productive_percentage": productive_percentage,
            "common_apps": [app for app, count in common_apps],
            "common_activities": [activity for activity, count in common_activities],
            "summary_text": summary_text
        }
    
    def _assess_productivity(self, content: str) -> bool:
        """Assess if the content indicates productive activity.
        
        Args:
            content (str): Analysis content from GPT-4 Vision.
            
        Returns:
            bool: True if the content appears to indicate productive activity.
        """
        # Simple keyword matching for productivity assessment
        productive_keywords = [
            "coding", "programming", "writing", "document", "spreadsheet", 
            "presentation", "research", "studying", "reading", "work", 
            "productive", "development", "analysis", "design", "project"
        ]
        
        distraction_keywords = [
            "social media", "youtube", "entertainment", "game", "gaming",
            "distraction", "unrelated", "non-productive", "streaming", "video",
            "browsing", "shopping", "non-work"
        ]
        
        # Count matches
        productive_count = sum(1 for keyword in productive_keywords if keyword.lower() in content.lower())
        distraction_count = sum(1 for keyword in distraction_keywords if keyword.lower() in content.lower())
        
        # If explicitly mentioned as productive or distraction
        if "productive" in content.lower() and "not productive" not in content.lower():
            return True
        if "distraction" in content.lower() or "non-productive" in content.lower():
            return False
        
        # Otherwise compare counts
        return productive_count > distraction_count
    
    def _extract_applications(self, content: str) -> List[str]:
        """Extract mentioned applications from the analysis content.
        
        Args:
            content (str): Analysis content from GPT-4 Vision.
            
        Returns:
            list: List of detected applications.
        """
        common_apps = [
            "Chrome", "Firefox", "Safari", "Edge", "Visual Studio Code", "VS Code",
            "PyCharm", "IntelliJ", "Word", "Excel", "PowerPoint", "Outlook",
            "Slack", "Discord", "Teams", "Zoom", "Terminal", "Command Prompt",
            "Notepad", "TextEdit", "Photoshop", "Illustrator", "Figma", "Sketch"
        ]
        
        detected = []
        for app in common_apps:
            if app.lower() in content.lower():
                detected.append(app)
        
        return detected
    
    def _extract_activities(self, content: str) -> List[str]:
        """Extract mentioned activities from the analysis content.
        
        Args:
            content (str): Analysis content from GPT-4 Vision.
            
        Returns:
            list: List of detected activities.
        """
        common_activities = [
            "coding", "programming", "writing", "reading", "browsing",
            "watching", "gaming", "chatting", "messaging", "emailing",
            "researching", "designing", "editing", "analyzing", "presenting"
        ]
        
        detected = []
        for activity in common_activities:
            if activity.lower() in content.lower():
                detected.append(activity)
        
        return detected


def analyze_screen_capture(image_path: str) -> Dict[str, Any]:
    """Utility function to analyze a single screen capture without creating an analyzer instance.
    
    Args:
        image_path (str): Path to the image file.
        
    Returns:
        dict: Analysis results.
    """
    analyzer = VisionAnalyzer()
    return analyzer.analyze_image(image_path)


if __name__ == "__main__":
    # Simple test if run directly
    import sys
    
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        print(f"Analyzing image: {image_path}")
        result = analyze_screen_capture(image_path)
        print(json.dumps(result, indent=2))
    else:
        print("Please provide an image path as argument")
