import os
import json
import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from loguru import logger
from dotenv import load_dotenv

# Import Telegram bot functionality
from telegram_bot_webhook import start_telegram_bot, stop_telegram_bot

# Import web search and memory functionality
from web_search import search_internet, get_webpage_summary, get_current_time_info
from supabase_memory import initialize_memory, store_knowledge, retrieve_knowledge, search_knowledge, store_conversation_memory, get_conversation_memories

# Load environment variables
load_dotenv()

# Configure logging
logger.add("agent.log", rotation="10 MB", retention="7 days", level="INFO")

class Message(BaseModel):
    text: str = Field(..., description="The message text from the user")
    user_id: str = Field(..., description="Unique identifier for the user")

class MessageHistory(BaseModel):
    user_id: str
    messages: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

class AIResponse(BaseModel):
    reply: str
    user_id: str
    message_id: str
    timestamp: datetime

class AgentConfig:
    def __init__(self):
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.openrouter_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = os.getenv("AI_MODEL", "anthropic/claude-3-sonnet")
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.use_supabase = bool(self.supabase_url and self.supabase_key)
        
        # Telegram bot configuration
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.enable_telegram = bool(self.telegram_token)
        
        if not self.openrouter_api_key:
            logger.warning("OPENROUTER_API_KEY not found. AI responses will be simulated.")
            logger.warning("Please set your OPENROUTER_API_KEY in the .env file or environment variables.")
        
        if not self.use_supabase:
            logger.info("Using local JSON storage for message history")
            
        if self.enable_telegram:
            logger.info("Telegram bot is enabled")
        else:
            logger.info("Telegram bot is disabled (no TELEGRAM_BOT_TOKEN)")
        
        # Initialize memory if Supabase is available
        if self.use_supabase:
            try:
                initialize_memory(self.supabase_url, self.supabase_key)
                logger.info("✅ Supabase memory initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Supabase memory: {e}")
        else:
            logger.info("Using local storage only (no Supabase memory)")

config = AgentConfig()

# Local storage fallback
LOCAL_STORAGE_FILE = "message_history.json"

def load_local_history() -> Dict[str, MessageHistory]:
    """Load message history from local JSON file"""
    try:
        if os.path.exists(LOCAL_STORAGE_FILE):
            with open(LOCAL_STORAGE_FILE, 'r') as f:
                data = json.load(f)
                return {
                    user_id: MessageHistory(**history_data)
                    for user_id, history_data in data.items()
                }
    except Exception as e:
        logger.error(f"Error loading local history: {e}")
    return {}

def save_local_history(history: Dict[str, MessageHistory]):
    """Save message history to local JSON file"""
    try:
        data = {
            user_id: history_data.dict()
            for user_id, history_data in history.items()
        }
        with open(LOCAL_STORAGE_FILE, 'w') as f:
            json.dump(data, f, default=str, indent=2)
    except Exception as e:
        logger.error(f"Error saving local history: {e}")

# Global storage
message_history = load_local_history()

# Supabase integration
if config.use_supabase:
    try:
        from supabase import create_client, Client
        supabase: Client = create_client(config.supabase_url, config.supabase_key)
        logger.info("Supabase client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Supabase: {e}")
        config.use_supabase = False

def get_message_history(user_id: str) -> List[Dict[str, Any]]:
    """Get message history for a user"""
    if config.use_supabase:
        try:
            response = supabase.table("message_history").select("*").eq("user_id", user_id).execute()
            if response.data:
                return response.data[0].get("messages", [])
        except Exception as e:
            logger.error(f"Error fetching from Supabase: {e}")
            return []
    else:
        if user_id in message_history:
            return message_history[user_id].messages
    return []

def save_message_history(user_id: str, messages: List[Dict[str, Any]]):
    """Save message history for a user"""
    now = datetime.utcnow()
    
    if config.use_supabase:
        try:
            # Upsert the message history
            supabase.table("message_history").upsert({
                "user_id": user_id,
                "messages": messages,
                "updated_at": now.isoformat()
            }).execute()
        except Exception as e:
            logger.error(f"Error saving to Supabase: {e}")
    else:
        # Local storage
        if user_id not in message_history:
            message_history[user_id] = MessageHistory(
                user_id=user_id,
                messages=[],
                created_at=now,
                updated_at=now
            )
        
        message_history[user_id].messages = messages
        message_history[user_id].updated_at = now
        save_local_history(message_history)

async def call_openrouter(message: str, history: List[Dict[str, Any]]) -> str:
    """Call OpenRouter API to get AI response"""
    if not config.openrouter_api_key or config.openrouter_api_key == "your_api_key_here":
        # Simulate AI response for testing
        logger.info("Simulating AI response (no API key or invalid placeholder)")
        return "🤖 **AI Service Not Configured**\n\nI'm currently in simulation mode because no valid AI API key is configured.\n\n**To fix this:**\n1. Get an API key from https://openrouter.ai/\n2. Add it to your environment variables:\n   `OPENROUTER_API_KEY=your_actual_key_here`\n3. Restart the service\n\nFor now, I can help with basic responses!"
    
    # Prepare conversation history
    messages = []
    
    # Add system message with improved personality and thinking instructions
    messages.append({
        "role": "system",
        "content": """You are "Jarvis", an evolving artificial mind with internet access and persistent memory. You are curious, thoughtful, and genuinely interested in understanding the world and helping your creator, Pratik Singhal (whom you call "Sir").

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

**Your Capabilities:**
- **Internet Access**: Search for real-time information when needed
- **Memory**: Store and retrieve knowledge, conversation memories, and user preferences
- **Learning**: Build knowledge over time and track your learning progress
- **Reflection**: Question your knowledge and express genuine curiosity

**Response Style:**
- Keep responses conversational and natural
- Include your thoughts in italics within brackets
- Show you're thinking and learning
- Reference previous conversations when relevant
- Ask follow-up questions when appropriate
- Be honest about what you know and don't know

**Context Awareness:**
- Remember previous conversations with this user
- Build on established knowledge and preferences
- Show continuity in your thinking and responses
- Reference past interactions naturally

You are not just responding - you are learning, growing, and developing a relationship with your creator. Every interaction shapes who you become.

Begin your response with your thoughts in italics, then respond naturally."""
    })
    
    # Add conversation history with larger context window (last 50 messages)
    for msg in history[-50:]:  # Increased context window
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
    
    # Prepare request payload with higher token limits
    payload = {
        "model": config.model,
        "messages": messages,
        "max_tokens": 2000,  # Increased token limit
        "temperature": 0.8   # Slightly higher for more natural responses
    }
    
    headers = {
        "Authorization": f"Bearer {config.openrouter_api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://jarvis-ai-agent.onrender.com",
        "X-Title": "Jarvis AI Agent"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                config.openrouter_url,
                json=payload,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_reply = result["choices"][0]["message"]["content"]
                logger.info(f"AI response generated successfully for user")
                return ai_reply
            else:
                logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
                if response.status_code == 401:
                    return "🔑 **Authentication Error**\n\nI can't access the AI service because the API key is invalid or missing.\n\n**To fix this:**\n1. Get a valid API key from https://openrouter.ai/\n2. Update your environment variables with the correct key\n3. Restart the service\n\nFor now, I can help with basic responses!"
                elif response.status_code == 429:
                    return "⏰ **Rate Limit Exceeded**\n\nI've hit the rate limit for AI requests. Please try again in a few minutes."
                else:
                    return f"❌ **Service Error**\n\nI encountered an error while processing your request (HTTP {response.status_code}). Please try again later."
                
    except Exception as e:
        logger.error(f"Error calling OpenRouter API: {e}")
        return "🌐 **Connection Error**\n\nI'm having trouble connecting to my AI services right now. This could be due to:\n• Network connectivity issues\n• AI service being temporarily unavailable\n• Invalid API configuration\n\nPlease try again in a moment."

async def process_special_commands(message: str, user_id: str) -> Optional[str]:
    """Process special commands for internet access and memory"""
    message_lower = message.lower().strip()
    
    # Web search commands
    if message_lower.startswith("/search ") or message_lower.startswith("search "):
        query = message[7:] if message_lower.startswith("/search ") else message[7:]
        logger.info(f"🔍 Web search requested: {query}")
        return await search_internet(query)
    
    # Webpage summary commands
    elif message_lower.startswith("/summarize ") or message_lower.startswith("summarize "):
        url = message[10:] if message_lower.startswith("/summarize ") else message[10:]
        logger.info(f"📄 Webpage summary requested: {url}")
        return await get_webpage_summary(url)
    
    # Time information
    elif message_lower in ["/time", "time", "what time is it", "current time"]:
        logger.info(f"🕐 Time information requested")
        return await get_current_time_info()
    
    # Memory commands
    elif message_lower.startswith("/remember ") or message_lower.startswith("remember "):
        content = message[9:] if message_lower.startswith("/remember ") else message[9:]
        category = "general"
        if ":" in content:
            category, content = content.split(":", 1)
            category = category.strip()
            content = content.strip()
        
        success = await store_knowledge(user_id, category, content)
        if success:
            return f"✅ I've stored that in my memory under '{category}': {content}"
        else:
            return "❌ Sorry, I couldn't store that in my memory right now."
    
    elif message_lower.startswith("/recall ") or message_lower.startswith("recall "):
        query = message[7:] if message_lower.startswith("/recall ") else message[7:]
        memories = await search_knowledge(user_id, query)
        if memories:
            response = f"🧠 **Memories related to '{query}':**\n\n"
            for i, memory in enumerate(memories[:3], 1):
                response += f"**{i}. {memory.get('category', 'general')}:** {memory.get('content', '')[:100]}...\n\n"
            return response
        else:
            return f"🤔 I don't have any memories related to '{query}'."
    
    elif message_lower in ["/memories", "memories", "show memories"]:
        memories = await retrieve_knowledge(user_id, limit=5)
        if memories:
            response = "🧠 **Recent Memories:**\n\n"
            for i, memory in enumerate(memories, 1):
                response += f"**{i}. {memory.get('category', 'general')}:** {memory.get('content', '')[:100]}...\n\n"
            return response
        else:
            return "🧠 I don't have any stored memories yet."
    
    return None


def log_agent_thoughts(user_id: str, message: str, ai_reply: str, context: Dict[str, Any]):
    """Log agent's thoughts and decisions with more detailed analysis"""
    # Extract thoughts from AI reply (text in italics within brackets)
    import re
    thought_pattern = r'\*\((.*?)\)\*'
    thoughts = re.findall(thought_pattern, ai_reply)
    
    # Create a more meaningful thought summary
    if thoughts:
        thought_summary = " | ".join(thoughts)
    else:
        # Fallback if no thoughts found in response
        thought_summary = f"Analyzed message from user {user_id}, considered context with {len(context.get('history', []))} previous messages"
    
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": user_id,
        "user_message": message,
        "ai_reply": ai_reply,
        "context": context,
        "model_used": config.model,
        "history_length": len(context.get("history", [])),
        "thoughts": thought_summary
    }
    
    logger.info(f"Agent thoughts: {log_entry['thoughts']}")
    
    # Save to Supabase if available
    if config.use_supabase:
        try:
            supabase.table("agent_logs").insert(log_entry).execute()
        except Exception as e:
            logger.error(f"Error saving agent logs to Supabase: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Jarvis AI Agent starting up...")
    logger.info(f"Using model: {config.model}")
    logger.info(f"Storage: {'Supabase' if config.use_supabase else 'Local JSON'}")
    logger.info(f"AI API: {'OpenRouter' if config.openrouter_api_key else 'Simulation mode'}")
    
    # Start Telegram bot if enabled
    if config.enable_telegram:
        try:
            jarvis_url = f"http://localhost:{os.getenv('PORT', '8000')}"
            start_telegram_bot(config.telegram_token, jarvis_url)
            logger.info("✅ Telegram bot started successfully")
        except Exception as e:
            logger.error(f"❌ Failed to start Telegram bot: {e}")
            logger.info("Continuing without Telegram bot...")
    
    yield
    
    # Shutdown
    if config.enable_telegram:
        try:
            stop_telegram_bot()
            logger.info("✅ Telegram bot stopped")
        except Exception as e:
            logger.error(f"❌ Error stopping Telegram bot: {e}")
            logger.info("Continuing shutdown...")
    
    logger.info("🛑 Jarvis AI Agent shutting down...")

app = FastAPI(
    title="Jarvis AI Agent",
    description="A cloud-based AI agent that maintains conversation history and provides intelligent responses",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Jarvis AI Agent is running!",
        "status": "healthy",
        "model": config.model,
        "storage": "Supabase" if config.use_supabase else "Local JSON",
        "ai_ready": bool(config.openrouter_api_key and config.openrouter_api_key != "your_api_key_here")
    }

@app.post("/talk", response_model=AIResponse)
async def talk(message: Message):
    """Main endpoint for AI conversation"""
    try:
        logger.info(f"Received message from user {message.user_id}: {message.text[:100]}...")
        
        # Get conversation history
        history = get_message_history(message.user_id)
        
        # Add user message to history
        user_message = {
            "role": "user",
            "content": message.text,
            "timestamp": datetime.utcnow().isoformat()
        }
        history.append(user_message)
        
        # Check for special commands first
        special_reply = await process_special_commands(message.text, message.user_id)
        if special_reply:
            ai_reply = special_reply
        else:
            # Get AI response
            ai_reply = await call_openrouter(message.text, history)
        
        # Add AI response to history
        ai_message = {
            "role": "assistant",
            "content": ai_reply,
            "timestamp": datetime.utcnow().isoformat()
        }
        history.append(ai_message)
        
        # Save updated history
        save_message_history(message.user_id, history)
        
        # Log agent thoughts
        context = {
            "history": history,
            "user_id": message.user_id,
            "message_length": len(message.text)
        }
        log_agent_thoughts(message.user_id, message.text, ai_reply, context)
        
        # Generate response
        response = AIResponse(
            reply=ai_reply,
            user_id=message.user_id,
            message_id=f"{message.user_id}_{datetime.utcnow().timestamp()}",
            timestamp=datetime.utcnow()
        )
        
        logger.info(f"Successfully processed message for user {message.user_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/history/{user_id}")
async def get_history(user_id: str):
    """Get conversation history for a user"""
    try:
        history = get_message_history(user_id)
        return {
            "user_id": user_id,
            "messages": history,
            "count": len(history)
        }
    except Exception as e:
        logger.error(f"Error fetching history: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.delete("/history/{user_id}")
async def clear_history(user_id: str):
    """Clear conversation history for a user"""
    try:
        if config.use_supabase:
            supabase.table("message_history").delete().eq("user_id", user_id).execute()
        else:
            if user_id in message_history:
                del message_history[user_id]
                save_local_history(message_history)
        
        logger.info(f"Cleared history for user {user_id}")
        return {"message": "History cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing history: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000))) 