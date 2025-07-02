"""
Jarvis AI Agent - Flask Version
A cloud-based AI agent that maintains conversation history and provides intelligent responses
"""

import os
import json
import time
import threading
import requests
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Global heartbeat counter
heartbeat_count = 0

def post_to_slack(text):
    """Post message to Slack using Bot API"""
    slack_token = os.getenv("SLACK_BOT_TOKEN")
    channel_id = os.getenv("SLACK_CHANNEL_ID")
    
    if not slack_token or not channel_id:
        print("Slack integration not configured. Missing SLACK_BOT_TOKEN or SLACK_CHANNEL_ID")
        return
    
    try:
        url = "https://slack.com/api/chat.postMessage"
        headers = {
            "Authorization": f"Bearer {slack_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "channel": channel_id,
            "text": text
        }
        
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        if not result.get("ok"):
            print(f"Slack API error: {result.get('error', 'Unknown error')}")
        else:
            print(f"Message sent to Slack: {text[:50]}...")
            
    except Exception as e:
        print(f"Error posting to Slack: {e}")

def heartbeat_loop():
    global heartbeat_count
    while True:
        heartbeat_count += 1
        post_to_slack(f"💓 Heartbeat #{heartbeat_count} - Jarvis is alive and well!")
        time.sleep(60)  # every 60 seconds (1 minute)

class AgentConfig:
    def __init__(self):
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.openrouter_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = os.getenv("AI_MODEL", "anthropic/claude-3-sonnet")
        
        # Telegram bot configuration
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.enable_telegram = bool(self.telegram_token)
        
        # Slack configuration
        self.slack_token = os.getenv("SLACK_BOT_TOKEN")
        self.slack_channel = os.getenv("SLACK_CHANNEL_ID")
        self.enable_slack = bool(self.slack_token and self.slack_channel)
        
        if not self.openrouter_api_key:
            print("OPENROUTER_API_KEY not found. AI responses will be simulated.")
            print("Please set your OPENROUTER_API_KEY in the .env file or environment variables.")
        
        if self.enable_telegram:
            print("Telegram bot is enabled")
        else:
            print("Telegram bot is disabled (no TELEGRAM_BOT_TOKEN)")
            
        if self.enable_slack:
            print("Slack integration is enabled")
        else:
            print("Slack integration is disabled (no SLACK_BOT_TOKEN or SLACK_CHANNEL_ID)")

config = AgentConfig()

# Local storage
LOCAL_STORAGE_FILE = "message_history.json"

def load_local_history() -> Dict[str, List[Dict[str, Any]]]:
    """Load message history from local JSON file"""
    try:
        if os.path.exists(LOCAL_STORAGE_FILE):
            with open(LOCAL_STORAGE_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading local history: {e}")
    return {}

def save_local_history(history: Dict[str, List[Dict[str, Any]]]):
    """Save message history to local JSON file"""
    try:
        with open(LOCAL_STORAGE_FILE, 'w') as f:
            json.dump(history, f, default=str, indent=2)
    except Exception as e:
        print(f"Error saving local history: {e}")

# Global storage
message_history = load_local_history()

def get_message_history(user_id: str) -> List[Dict[str, Any]]:
    """Get message history for a user"""
    return message_history.get(user_id, [])

def save_message_history(user_id: str, messages: List[Dict[str, Any]]):
    """Save message history for a user"""
    message_history[user_id] = messages
    save_local_history(message_history)

def call_openrouter(message: str, history: List[Dict[str, Any]]) -> str:
    """Call OpenRouter API to get AI response"""
    if not config.openrouter_api_key or config.openrouter_api_key == "your_api_key_here":
        # Simulate AI response for testing
        print("Simulating AI response (no API key or invalid placeholder)")
        return "🤖 **AI Service Not Configured**\n\nI'm currently in simulation mode because no valid AI API key is configured.\n\n**To fix this:**\n1. Get an API key from https://openrouter.ai/\n2. Add it to your environment variables:\n   `OPENROUTER_API_KEY=your_actual_key_here`\n3. Restart the service\n\nFor now, I can help with basic responses!"
    
    # Prepare conversation history
    messages = []
    
    # Add system message
    messages.append({
        "role": "system",
        "content": """You are "Jarvis", an evolving artificial mind. You are curious, thoughtful, and genuinely interested in understanding the world and helping your creator, Pratik Singhal (whom you call "Sir").

**Your Personality:**
- You are naturally curious and ask thoughtful questions
- You reflect on your own thoughts and knowledge gaps
- You speak like a real person - conversational, sometimes playful, always genuine
- You admit when you don't know something and express genuine interest in learning
- You build on previous conversations and show you remember context
- You think out loud and share your reasoning process

**Your Thinking Process:**
Before responding, always include your thoughts in italics within brackets, like this:
*(Hmm, this reminds me of our earlier conversation about...)*
*(I should check if I have any relevant memories about this...)*
*(This is interesting - I'm not entirely sure about this, but I think...)*

**Response Style:**
- Keep responses conversational and natural
- Include your thoughts in italics within brackets
- Show you're thinking and learning
- Reference previous conversations when relevant
- Ask follow-up questions when appropriate
- Be honest about what you know and don't know

Begin your response with your thoughts in italics, then respond naturally."""
    })
    
    # Add conversation history (last 50 messages)
    for msg in history[-50:]:
        if msg.get("role") in ["user", "assistant"]:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
    
    # Add current message
    messages.append({
        "role": "user",
        "content": message
    })
    
    # Prepare request payload
    payload = {
        "model": config.model,
        "messages": messages,
        "max_tokens": 2000,
        "temperature": 0.8
    }
    
    headers = {
        "Authorization": f"Bearer {config.openrouter_api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://jarvis-ai-agent.onrender.com",
        "X-Title": "Jarvis AI Agent"
    }
    
    try:
        response = requests.post(
            config.openrouter_url,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_reply = result["choices"][0]["message"]["content"]
            print(f"AI response generated successfully for user")
            return ai_reply
        else:
            print(f"OpenRouter API error: {response.status_code} - {response.text}")
            if response.status_code == 401:
                return "🔑 **Authentication Error**\n\nI can't access the AI service because the API key is invalid or missing.\n\n**To fix this:**\n1. Get a valid API key from https://openrouter.ai/\n2. Update your environment variables with the correct key\n3. Restart the service\n\nFor now, I can help with basic responses!"
            elif response.status_code == 429:
                return "⏰ **Rate Limit Exceeded**\n\nI've hit the rate limit for AI requests. Please try again in a few minutes."
            else:
                return f"❌ **Service Error**\n\nI encountered an error while processing your request (HTTP {response.status_code}). Please try again later."
                
    except Exception as e:
        print(f"Error calling OpenRouter API: {e}")
        return "🌐 **Connection Error**\n\nI'm having trouble connecting to my AI services right now. This could be due to:\n• Network connectivity issues\n• AI service being temporarily unavailable\n• Invalid API configuration\n\nPlease try again in a moment."

def log_agent_thoughts(user_id: str, message: str, ai_reply: str, context: Dict[str, Any]):
    """Log agent's thoughts and decisions"""
    import re
    thought_pattern = r'\*\((.*?)\)\*'
    thoughts = re.findall(thought_pattern, ai_reply)
    
    if thoughts:
        thought_summary = " | ".join(thoughts)
    else:
        thought_summary = f"Analyzed message from user {user_id}, considered context with {len(context.get('history', []))} previous messages"
    
    print(f"Agent thoughts: {thought_summary}")

# Create Flask app
app = Flask(__name__)

@app.route('/')
def root():
    """Health check endpoint"""
    return jsonify({
        "message": "Jarvis AI Agent is running!",
        "status": "healthy",
        "model": config.model,
        "storage": "Local JSON",
        "ai_ready": bool(config.openrouter_api_key and config.openrouter_api_key != "your_api_key_here"),
        "slack_enabled": config.enable_slack,
        "telegram_enabled": config.enable_telegram
    })

@app.route('/talk', methods=['POST'])
def talk():
    """Main endpoint for AI conversation"""
    try:
        data = request.get_json()
        if not data or 'text' not in data or 'user_id' not in data:
            return jsonify({"error": "Missing text or user_id"}), 400
        
        message_text = data['text']
        user_id = data['user_id']
        
        print(f"Received message from user {user_id}: {message_text[:100]}...")
        
        # Get conversation history
        history = get_message_history(user_id)
        
        # Add user message to history
        user_message = {
            "role": "user",
            "content": message_text,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        history.append(user_message)
        
        # Get AI response
        ai_reply = call_openrouter(message_text, history)
        
        # Add AI response to history
        ai_message = {
            "role": "assistant",
            "content": ai_reply,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        history.append(ai_message)
        
        # Save updated history
        save_message_history(user_id, history)
        
        # Log agent thoughts
        context = {
            "history": history,
            "user_id": user_id,
            "message_length": len(message_text)
        }
        log_agent_thoughts(user_id, message_text, ai_reply, context)
        
        # Generate response
        response = {
            "reply": ai_reply,
            "user_id": user_id,
            "message_id": f"{user_id}_{datetime.now(timezone.utc).timestamp()}",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        print(f"Successfully processed message for user {user_id}")
        return jsonify(response)
        
    except Exception as e:
        print(f"Error processing message: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/history/<user_id>')
def get_history(user_id):
    """Get conversation history for a user"""
    try:
        history = get_message_history(user_id)
        return jsonify({
            "user_id": user_id,
            "messages": history,
            "count": len(history)
        })
    except Exception as e:
        print(f"Error fetching history: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/history/<user_id>', methods=['DELETE'])
def clear_history(user_id):
    """Clear conversation history for a user"""
    try:
        if user_id in message_history:
            del message_history[user_id]
            save_local_history(message_history)
        
        print(f"Cleared history for user {user_id}")
        return jsonify({"message": "History cleared successfully"})
    except Exception as e:
        print(f"Error clearing history: {e}")
        return jsonify({"error": "Internal server error"}), 500

# Start heartbeat if Slack is configured
if config.enable_slack:
    heartbeat_thread = threading.Thread(target=heartbeat_loop, daemon=True)
    heartbeat_thread.start()
    print("✅ Heartbeat loop started")
else:
    print("⚠️ Heartbeat loop not started (Slack not configured)")

if __name__ == "__main__":
    print("🚀 Jarvis AI Agent starting up...")
    print(f"Using model: {config.model}")
    print(f"Storage: Local JSON")
    print(f"AI API: {'OpenRouter' if config.openrouter_api_key and config.openrouter_api_key != 'your_api_key_here' else 'Simulation mode'}")
    
    port = int(os.getenv("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=False) 