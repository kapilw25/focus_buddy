# Focus Buddy

An AI-powered productivity assistant that helps you maintain focus during deep work sessions by monitoring your screen, analyzing your environment, and providing timely nudges to keep you on track.

## 🎯 Overview

Focus Buddy is a Streamlit web application designed for coders, researchers, and students who want to extend their deep work sessions to 120+ minutes. It leverages OpenAI's GPT-4o Realtime API and GPT-4 Vision to create an intelligent work companion that understands your context and helps you stay focused.

## ✨ Key Features

- **Real-time Voice Assistant**: Engage in natural conversations with GPT-4o Realtime API
- **Screen Context Analysis**: Periodic screen captures analyzed by GPT-4 Vision
- **Audio Environment Monitoring**: Combines microphone and system audio for comprehensive context
- **Smart Focus Reminders**: Timely, context-aware nudges to maintain productivity
- **Session Tracking**: Monitor your productivity metrics and work patterns
- **Customizable Settings**: Adjust check-in frequency, prompt style, and more

## 🗂️ Project Structure

```
focus_buddy/
│
├── app.py                      # Main Streamlit application entry point
│
├── core/
│   ├── realtime_assistant.py   # Handles OpenAI GPT-4o Realtime API integration
│   ├── vision_analyzer.py      # Processes screen captures with GPT-4 Vision
│   ├── audio_manager.py        # Audio routing and processing
│   └── session_tracker.py      # Tracks productivity metrics and session data
│
├── utils/
│   ├── screen_capture.py       # Screen capture functionality
│   ├── config.py               # Configuration settings and constants
│   └── prompts.py              # Template prompts for AI interactions
│
├── ui/
│   ├── dashboard.py            # Dashboard components for Streamlit
│   ├── settings.py             # Settings UI components
│   └── session_view.py         # Session visualization components
│
├── data/
│   └── session_logs/           # Directory to store session logs
│
├── .streamlit/
│   └── secrets.toml            # API keys and sensitive configuration
│
├── requirements.txt            # Project dependencies
│
└── README.md                   # Project documentation
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- OpenAI API key with access to GPT-4o Realtime API and GPT-4 Vision
- For audio routing: BlackHole (macOS) or similar virtual audio device

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/focus_buddy.git
   cd focus_buddy
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Configure your OpenAI API key:
   - Create a `.streamlit/secrets.toml` file
   - Add your API key: `OPENAI_API_KEY = "your-api-key-here"`

4. Run the application:
   ```
   streamlit run app.py
   ```

## 🔧 Core Components

### 1. Realtime Assistant
Handles WebRTC connection to OpenAI's Realtime API for voice conversations.

### 2. Vision Analyzer
Processes screen captures and extracts context using GPT-4 Vision.

### 3. Audio Manager
Manages audio routing, combining microphone and system audio for comprehensive context.

### 4. Session Tracker
Tracks and summarizes work sessions, providing productivity metrics and insights.

## 📊 UI Components

- **Dashboard**: Overview of current and past sessions
- **Settings**: Configure application behavior
- **Session View**: Detailed view of individual work sessions

## 🛠️ Utilities

- **Screen Capture**: Periodic screen captures for context analysis
- **Config**: Central configuration settings
- **Prompts**: Template prompts for AI interactions

## 📝 Usage

1. Start a new focus session from the dashboard
2. Allow screen capture and microphone access
3. Begin your work while Focus Buddy monitors in the background
4. Receive gentle nudges and reminders to stay on task
5. Review your session metrics when finished

## 🔒 Privacy

- All screen captures and audio are processed through OpenAI's APIs
- No data is stored permanently beyond your local session logs
- You can configure the frequency and type of monitoring to suit your comfort level

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- OpenAI for providing the GPT-4o Realtime API and GPT-4 Vision API
- Streamlit for the web application framework
