# 👩‍💻 Focus Buddy (Streamlit Version) – AI-Powered Coder & Study Companion

A Streamlit web app that keeps you focused by observing your screen and nudging you every few minutes using GPT‑4 Vision. Designed for coders and researchers who want to boost their deep-work sessions to 120+ minutes.

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

- Periodic screen capture + GPT‑4 Vision context analysis
- Smart focus reminders to maintain productivity
- Dashboard-style session logs and productivity stats
- Customizable settings for check-in frequency and style

---

## 🔧 How It Works

## 🖥️ 1. Real-Time Screen Monitoring

MacOS-based periodic screen capture (e.g., every 60 seconds):

- Tools: `screencapture`, Python + `pyobjc`
- Feed images into **GPT‑4 Vision API**
- Detect what you're working on ("Editing Jupyter", "Watching YouTube", etc.)

---

## ⏱️ 2. Scheduled Check-Ins & Focus Reminders

Create a loop (Python) to:

1. Capture screen → extract context with Vision API
2. Every 60–120s: generate a friendly check-in
   - Example: "Hey, still working on that notebook?"
3. Display reminders in the Streamlit interface
4. Log responses to track progress

---

## 🧠 3. Managing Context & Memory

Avoid token overflow:

- Summarize status every few turns (e.g., "30 mins in, debugging training loop")
- Feed summaries into the next round of assistant prompts

Keeps context on-topic and efficient.

---

## 💡 4. Prototype Components

| Component              | Tool/Tech                             |
|------------------------|----------------------------------------|
| Screen context         | `screencapture`, GPT-4 Vision API      |
| Orchestration logic    | Python + Streamlit                     |
| Summarization / memory | GPT-4 summarization logic              |

---

## 🔧 5. Key Practical Considerations

| Aspect          | Concern & Solution                                  |
|-----------------|-----------------------------------------------------|
| Cost            | Minimal cost for GPT-4 Vision API calls             |
| Privacy         | Ensure you're okay with OpenAI accessing the data   |
| Focus strategy  | Friendly, non-intrusive nudges only                 |
| Context window  | Use summaries to reduce prompt size & stay focused  |

---

## ✅ Step-by-Step Starter Guide

1. **Access** GPT‑4 Vision API
2. **Build screen-capture script** (e.g., cron every 60s)
   - Input → GPT-4 Vision → extract summary
3. **Main loop**
   - Periodically check screen context
   - Display check-in reminders
   - Log session status
4. **Track progress**
   - Log sessions, durations, summaries
   - Celebrate when you hit 120 mins!

---

## 🔮 Why This Works

- **Visual context awareness**: GPT-4 Vision understands what you're doing
- **Context-aware**: Vision analysis + summaries = relevant prompts
- **Positive reinforcement**: timely, helpful nudges
- **Customizable**: tune prompt style, interval, verbosity

---

**Built for coders, learners, and researchers who want to fight distractions with AI.**
