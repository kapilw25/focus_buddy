# 👩‍💻 Focus Buddy (Streamlit Version) – AI-Powered Coder & Study Companion

A Streamlit web app that keeps you focused by observing your screen, listening to your environment, and nudging you every few minutes using OpenAI’s Realtime API and GPT‑4 Vision. Designed for coders and researchers who want to boost their deep-work sessions to 120+ minutes.

---

## 🌐 Live Demo

**🔗 [Launch on Streamlit](https://focus-buddy.streamlit.app)**  
Uses shared OpenAI API Key (subject to rate limits).

---

## 🔑 API Key (Preconfigured)

This version includes a shared OpenAI key for demo/testing.  
You can replace it with your own key in `.streamlit/secrets.toml`.

---

## 🎯 Key Features

- Realtime conversation using GPT‑4o Realtime API (WebRTC)
- Periodic screen capture + GPT‑4 Vision context analysis
- Audio feedback with periodic nudges to stay focused
- Dashboard-style session logs and productivity stats

---

## 🔧 How It Works


## 🎙️ 1. Realtime Voice Conversational Flow

Leverage **OpenAI GPT‑4o Realtime API** (via WebSockets or WebRTC):

- Live speech-to-speech conversations
- Handles interruptions, streaming, and context
- Ideal for real-time productivity check-ins

---

## 🖥️ 2. Real-Time Screen Monitoring

MacOS-based periodic screen capture (e.g., every 60 seconds):

- Tools: `screencapture`, Python + `pyobjc`
- Feed images into **GPT‑4 Vision API**
- Detect what you’re working on ("Editing Jupyter", "Watching YouTube", etc.)

---

## 🔊 3. Dual Audio Capture (Mic + System Audio)

Route both mic + speaker audio into the assistant:

- Use **BlackHole** or **Loopback** on macOS
- Combine:
  - Your voice (mic input)
  - System sound (video/tutorials)

Send merged stream into the OpenAI Realtime API so the assistant "hears everything".

---

## ⏱️ 4. Scheduled Check-Ins & Focus Reminders

Create a loop (Python or Node.js) to:

1. Capture screen → extract context with Vision API
2. Every 60–120s: synthesize a friendly check-in
   - Example: “Hey, still working on that notebook?”
3. Use Realtime API for TTS voice output
4. Listen and log your response to track progress

---

## 🧠 5. Managing Context & Memory

Avoid token overflow:

- Summarize status every few turns (e.g., “30 mins in, debugging training loop”)
- Feed summaries into the next round of assistant prompts

Keeps conversation on-topic and efficient.

---

## 💡 6. Prototype Components

| Component              | Tool/Tech                             |
|------------------------|----------------------------------------|
| Voice assistant        | GPT-4o Realtime API via WebRTC         |
| Screen context         | `screencapture`, GPT-4 Vision API      |
| Audio routing          | BlackHole / Loopback (macOS)           |
| Orchestration logic    | Node.js or Python                      |
| Summarization / memory | GPT-4 summarization logic              |

---

## 🔧 7. Key Practical Considerations

| Aspect          | Concern & Solution                                  |
|-----------------|-----------------------------------------------------|
| Latency         | Use WebRTC for low-latency speech handling          |
| Cost            | ~$0.06/min input + ~$0.24/min output (≈ $25/2hr)    |
| Privacy         | Ensure you're okay with OpenAI accessing the data   |
| Focus strategy  | Friendly, non-intrusive nudges only                 |
| Context window  | Use summaries to reduce prompt size & stay focused  |

---

## ✅ Step-by-Step Starter Guide

1. **Access** OpenAI Realtime API + GPT‑4 Vision
2. **Build screen-capture script** (e.g., cron every 60s)
   - Input → GPT-4 Vision → extract summary
3. **Route dual audio**
   - Mic + system audio → merged input stream
4. **Setup Realtime streaming**
   - Stream audio to OpenAI → get voice response → play aloud
5. **Main loop**
   - Periodically check screen context
   - Speak check-in via TTS
   - Listen to reply & log session status
6. **Track progress**
   - Log sessions, durations, summaries
   - Celebrate when you hit 120 mins!

---

## 🔮 Why This Works

- **Multimodal input**: screen + mic + system audio
- **Context-aware**: GPT-4 Vision + summaries = relevant prompts
- **Positive reinforcement**: timely, human-like nudges
- **Customizable**: tune prompt style, interval, verbosity

---

**Built for coders, learners, and researchers who want to fight distractions with AI.**
