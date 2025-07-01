"""
Supabase Memory Module for Jarvis AI Agent
Provides persistent memory storage and knowledge management
"""

import os
from typing import Dict, List, Any, Optional
from loguru import logger
from datetime import datetime
import json


class SupabaseMemory:
    def __init__(self, supabase_url: str, supabase_key: str):
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Supabase client"""
        try:
            from supabase import create_client, Client
            self.client: Client = create_client(self.supabase_url, self.supabase_key)
            logger.info("✅ Supabase memory client initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Supabase memory: {e}")
            self.client = None
    
    def is_available(self) -> bool:
        """Check if Supabase memory is available"""
        return self.client is not None
    
    async def store_knowledge(self, user_id: str, category: str, content: str, metadata: Dict[str, Any] = None) -> bool:
        """
        Store knowledge in Supabase memory
        """
        if not self.is_available():
            return False
        
        try:
            knowledge_entry = {
                "user_id": user_id,
                "category": category,
                "content": content,
                "metadata": metadata or {},
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            result = self.client.table("knowledge_base").insert(knowledge_entry).execute()
            logger.info(f"✅ Stored knowledge for user {user_id} in category {category}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error storing knowledge: {e}")
            return False
    
    async def retrieve_knowledge(self, user_id: str, category: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve knowledge from Supabase memory
        """
        if not self.is_available():
            return []
        
        try:
            query = self.client.table("knowledge_base").select("*").eq("user_id", user_id)
            
            if category:
                query = query.eq("category", category)
            
            query = query.order("created_at", desc=True).limit(limit)
            result = query.execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"❌ Error retrieving knowledge: {e}")
            return []
    
    async def search_knowledge(self, user_id: str, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search knowledge base using text similarity
        """
        if not self.is_available():
            return []
        
        try:
            # Use Supabase's full-text search if available
            result = self.client.table("knowledge_base").select("*").eq("user_id", user_id).text_search("content", query).limit(limit).execute()
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"❌ Error searching knowledge: {e}")
            # Fallback to simple retrieval
            return await self.retrieve_knowledge(user_id, limit=limit)
    
    async def store_conversation_memory(self, user_id: str, conversation_id: str, summary: str, key_points: List[str]) -> bool:
        """
        Store conversation memory and key points
        """
        if not self.is_available():
            return False
        
        try:
            memory_entry = {
                "user_id": user_id,
                "conversation_id": conversation_id,
                "summary": summary,
                "key_points": key_points,
                "created_at": datetime.now().isoformat()
            }
            
            result = self.client.table("conversation_memories").insert(memory_entry).execute()
            logger.info(f"✅ Stored conversation memory for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error storing conversation memory: {e}")
            return False
    
    async def get_conversation_memories(self, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get recent conversation memories
        """
        if not self.is_available():
            return []
        
        try:
            result = self.client.table("conversation_memories").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"❌ Error retrieving conversation memories: {e}")
            return []
    
    async def store_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """
        Store user preferences and settings
        """
        if not self.is_available():
            return False
        
        try:
            preference_entry = {
                "user_id": user_id,
                "preferences": preferences,
                "updated_at": datetime.now().isoformat()
            }
            
            # Upsert to update existing preferences
            result = self.client.table("user_preferences").upsert(preference_entry).execute()
            logger.info(f"✅ Stored preferences for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error storing user preferences: {e}")
            return False
    
    async def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        Get user preferences
        """
        if not self.is_available():
            return {}
        
        try:
            result = self.client.table("user_preferences").select("*").eq("user_id", user_id).execute()
            if result.data:
                return result.data[0].get("preferences", {})
            return {}
            
        except Exception as e:
            logger.error(f"❌ Error retrieving user preferences: {e}")
            return {}
    
    async def store_learning_progress(self, user_id: str, topic: str, progress: Dict[str, Any]) -> bool:
        """
        Store learning progress for topics
        """
        if not self.is_available():
            return False
        
        try:
            progress_entry = {
                "user_id": user_id,
                "topic": topic,
                "progress": progress,
                "updated_at": datetime.now().isoformat()
            }
            
            result = self.client.table("learning_progress").upsert(progress_entry).execute()
            logger.info(f"✅ Stored learning progress for user {user_id}, topic {topic}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error storing learning progress: {e}")
            return False
    
    async def get_learning_progress(self, user_id: str, topic: str = None) -> List[Dict[str, Any]]:
        """
        Get learning progress
        """
        if not self.is_available():
            return []
        
        try:
            query = self.client.table("learning_progress").select("*").eq("user_id", user_id)
            
            if topic:
                query = query.eq("topic", topic)
            
            result = query.execute()
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"❌ Error retrieving learning progress: {e}")
            return []


# Global memory instance
memory = None


def initialize_memory(supabase_url: str, supabase_key: str) -> SupabaseMemory:
    """Initialize the global memory instance"""
    global memory
    memory = SupabaseMemory(supabase_url, supabase_key)
    return memory


async def store_knowledge(user_id: str, category: str, content: str, metadata: Dict[str, Any] = None) -> bool:
    """Store knowledge in memory"""
    if memory:
        return await memory.store_knowledge(user_id, category, content, metadata)
    return False


async def retrieve_knowledge(user_id: str, category: str = None, limit: int = 10) -> List[Dict[str, Any]]:
    """Retrieve knowledge from memory"""
    if memory:
        return await memory.retrieve_knowledge(user_id, category, limit)
    return []


async def search_knowledge(user_id: str, query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Search knowledge base"""
    if memory:
        return await memory.search_knowledge(user_id, query, limit)
    return []


async def store_conversation_memory(user_id: str, conversation_id: str, summary: str, key_points: List[str]) -> bool:
    """Store conversation memory"""
    if memory:
        return await memory.store_conversation_memory(user_id, conversation_id, summary, key_points)
    return False


async def get_conversation_memories(user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Get conversation memories"""
    if memory:
        return await memory.get_conversation_memories(user_id, limit)
    return []


async def store_user_preferences(user_id: str, preferences: Dict[str, Any]) -> bool:
    """Store user preferences"""
    if memory:
        return await memory.store_user_preferences(user_id, preferences)
    return False


async def get_user_preferences(user_id: str) -> Dict[str, Any]:
    """Get user preferences"""
    if memory:
        return await memory.get_user_preferences(user_id)
    return {}


async def store_learning_progress(user_id: str, topic: str, progress: Dict[str, Any]) -> bool:
    """Store learning progress"""
    if memory:
        return await memory.store_learning_progress(user_id, topic, progress)
    return False


async def get_learning_progress(user_id: str, topic: str = None) -> List[Dict[str, Any]]:
    """Get learning progress"""
    if memory:
        return await memory.get_learning_progress(user_id, topic)
    return [] 