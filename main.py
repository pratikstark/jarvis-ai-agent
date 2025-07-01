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
        
        if not self.openrouter_api_key:
            logger.warning("OPENROUTER_API_KEY not found. AI responses will be simulated.")
        
        if not self.use_supabase:
            logger.info("Using local JSON storage for message history")

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
    if not config.openrouter_api_key:
        # Simulate AI response for testing
        logger.info("Simulating AI response (no API key)")
        return "Hello! I'm your AI agent. I'm currently running in simulation mode. Please set your OPENROUTER_API_KEY to enable real AI responses."
    
    # Prepare conversation history
    messages = []
    
    # Add system message
    messages.append({
        "role": "system",
        "content": """You are Jarvis, an intelligent AI assistant. You are helpful, creative, and always try to provide thoughtful responses. 
        You have access to conversation history and should maintain context across messages. 
        Be conversational but professional, and always aim to be genuinely helpful."""
    })
    
    # Add conversation history
    for msg in history[-10:]:  # Keep last 10 messages for context
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
        "max_tokens": 1000,
        "temperature": 0.7
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
                return f"Sorry, I encountered an error while processing your request. Please try again later."
                
    except Exception as e:
        logger.error(f"Error calling OpenRouter API: {e}")
        return "I'm having trouble connecting to my AI services right now. Please try again in a moment."

def log_agent_thoughts(user_id: str, message: str, ai_reply: str, context: Dict[str, Any]):
    """Log agent's thoughts and decisions"""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": user_id,
        "user_message": message,
        "ai_reply": ai_reply,
        "context": context,
        "model_used": config.model,
        "history_length": len(context.get("history", [])),
        "thoughts": f"Processed message from user {user_id}. History contains {len(context.get('history', []))} messages. Generated response using {config.model}."
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
    
    yield
    
    # Shutdown
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
        "ai_ready": bool(config.openrouter_api_key)
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