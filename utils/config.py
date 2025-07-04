"""
Configuration settings and constants for the Focus Buddy application.
This module centralizes all configuration parameters used across the application.
"""

import os
import toml
from pathlib import Path

# Base paths
ROOT_DIR = Path(__file__).parent.parent.absolute()
DATA_DIR = os.path.join(ROOT_DIR, "data")
SESSION_LOGS_DIR = os.path.join(DATA_DIR, "session_logs")

# Ensure directories exist
os.makedirs(SESSION_LOGS_DIR, exist_ok=True)

# Load secrets from .streamlit/secrets.toml
try:
    SECRETS_PATH = os.path.join(ROOT_DIR, ".streamlit", "secrets.toml")
    secrets = toml.load(SECRETS_PATH)
    OPENAI_API_KEY = secrets.get("OPENAI_API_KEY", "")
except Exception as e:
    print(f"Warning: Could not load secrets file: {e}")
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

# OpenAI API settings
OPENAI_API_BASE = "https://api.openai.com/v1"
GPT4O_MODEL = "gpt-4o"  # For vision analysis

# Screen capture settings
SCREEN_CAPTURE_INTERVAL = 10  # Seconds between screen captures (default 10 seconds)
MAX_SCREEN_CAPTURES = 10  # Maximum number of screen captures to store
SCREEN_CAPTURE_QUALITY = 70  # JPEG quality (0-100)
SCREEN_CAPTURE_FORMAT = "JPEG"  # Image format

# Session settings
MIN_SESSION_DURATION = 5 * 60  # Minimum session duration in seconds (5 minutes)
DEFAULT_SESSION_DURATION = 120 * 60  # Default session duration in seconds (120 minutes)
CHECK_IN_INTERVAL = 60  # Seconds between check-ins (default 1 minute)

# UI settings
UI_REFRESH_RATE = 1  # Seconds between UI refreshes
UI_THEME_COLOR = "#FF5733"  # Primary theme color
UI_SECONDARY_COLOR = "#33A1FF"  # Secondary theme color

# Logging settings
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# System settings
DEBUG_MODE = False  # Set to True to enable debug mode
