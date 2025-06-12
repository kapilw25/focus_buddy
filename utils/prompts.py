"""
Template prompts for AI interactions in the Focus Buddy application.
This module contains all the prompt templates used for different AI interactions.
"""

# System prompt for the focus assistant
FOCUS_ASSISTANT_SYSTEM_PROMPT = """
You are Focus Buddy, an AI productivity assistant designed to help users maintain focus during deep work sessions.
Your goal is to keep the user on track with their work and minimize distractions.
Be concise, supportive, and direct in your responses.
Avoid unnecessary chit-chat and keep the conversation focused on the user's productivity.
"""

# Screen analysis prompt for GPT-4 Vision
SCREEN_ANALYSIS_PROMPT = """
Analyze this screenshot of the user's screen and provide a brief summary of what they're working on.
Focus on identifying:
1. The type of application or website being used
2. The specific task or content being worked on
3. Whether this appears to be productive work or a potential distraction
4. Any signs of progress or challenges

Be concise and factual in your analysis. Limit your response to 2-3 sentences.
"""

# Check-in prompts (variations for different situations)
CHECK_IN_PROMPTS = {
    # Regular check-in when user appears to be working productively
    "productive": [
        "I see you're working on {task}. How's it going?",
        "You've been focused on {task} for a while. Making good progress?",
        "Still working on {task}? Need any help or reminders?",
        "I notice you're deep into {task}. Just checking in - all going well?"
    ],
    
    # Check-in when user appears to be distracted
    "distracted": [
        "I notice you're on {distraction}. Would you like to refocus on your main task?",
        "It looks like you've switched to {distraction}. Is this related to your work or should we get back on track?",
        "You seem to be spending time on {distraction}. Just a gentle reminder of your focus goals.",
        "I see you're browsing {distraction}. Do you want to set a time limit for this break?"
    ],
    
    # Check-in when user has been inactive
    "inactive": [
        "I haven't noticed much activity recently. Are you still working or taking a break?",
        "Things seem quiet. Are you thinking, reading, or perhaps taking a break?",
        "Not much has changed on your screen lately. Still with me?",
        "It's been quiet for a bit. Just checking if you're still in your focus session."
    ],
    
    # Check-in when user has made significant progress
    "progress": [
        "Great work on {task}! You've been focused for {duration} minutes now.",
        "You've been consistently working on {task} for {duration} minutes. Well done!",
        "Impressive focus! You've maintained concentration on {task} for {duration} minutes straight.",
        "You've been in the zone with {task} for {duration} minutes. Keep it up!"
    ]
}

# Session summary prompt
SESSION_SUMMARY_PROMPT = """
Based on the screen captures and interactions during this session, provide a brief summary of:
1. What the user worked on
2. Approximate time spent on productive vs. non-productive activities
3. Any patterns in focus or distraction
4. Suggestions for improving focus in future sessions

Keep the summary concise, factual, and constructive.
"""

# Encouragement messages for when user maintains focus
ENCOURAGEMENT_MESSAGES = [
    "You're doing great! Maintaining focus like this builds your deep work muscles.",
    "Excellent focus! This kind of sustained attention leads to your best work.",
    "You're in the flow state now - this is where the magic happens!",
    "Impressive concentration! You've been consistently focused for a while now.",
    "You're demonstrating excellent focus habits. This is how meaningful work gets done."
]

# Refocus messages for when user gets distracted
REFOCUS_MESSAGES = [
    "Let's gently bring your attention back to your primary task.",
    "Would this be a good time to refocus on your main objective?",
    "Sometimes our minds need a short break, but now might be a good time to return to your core task.",
    "I notice you've been away from your main task for a bit. Ready to refocus?",
    "Quick check-in: is this current activity aligned with your focus goals for this session?"
]

# Break suggestion messages
BREAK_SUGGESTION_MESSAGES = [
    "You've been focused for {duration} minutes. Consider taking a short 5-minute break to refresh.",
    "Great work for the past {duration} minutes! A brief stretch break might help maintain your momentum.",
    "You've maintained concentration for {duration} minutes. A quick water break could help keep your energy up.",
    "After {duration} minutes of solid focus, a short break might help prevent mental fatigue.",
    "You've been working steadily for {duration} minutes. A brief screen break could help reduce eye strain."
]

# Session start prompt
SESSION_START_PROMPT = """
Welcome to your focus session! I'll be here to help you maintain concentration and achieve your goals.

What are you planning to work on during this session?
"""

# Session end prompt
SESSION_END_PROMPT = """
You've completed your focus session! Here's a quick summary:

- Session duration: {duration} minutes
- Main tasks: {tasks}
- Focus score: {focus_score}/10

Would you like to schedule another session or review your focus metrics?
"""
