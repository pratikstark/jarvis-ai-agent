"""
Web Search and Internet Access Module for Jarvis AI Agent
Provides capabilities to search the web and access real-time information
"""

import asyncio
import aiohttp
import httpx
from bs4 import BeautifulSoup
from loguru import logger
from typing import List, Dict, Any, Optional
import json
import re
from urllib.parse import urljoin, urlparse
import time


class WebSearch:
    def __init__(self):
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def search_web(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search the web using DuckDuckGo (no API key required)
        """
        try:
            # Use DuckDuckGo instant answer API
            url = "https://api.duckduckgo.com/"
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
            
            results = []
            
            # Add instant answer if available
            if data.get('Abstract'):
                results.append({
                    'title': data.get('Heading', 'Instant Answer'),
                    'snippet': data.get('Abstract', ''),
                    'url': data.get('AbstractURL', ''),
                    'source': 'DuckDuckGo Instant Answer'
                })
            
            # Add related topics
            for topic in data.get('RelatedTopics', [])[:max_results]:
                if isinstance(topic, dict) and topic.get('Text'):
                    results.append({
                        'title': topic.get('FirstURL', '').split('/')[-1].replace('_', ' '),
                        'snippet': topic.get('Text', ''),
                        'url': topic.get('FirstURL', ''),
                        'source': 'DuckDuckGo Related Topics'
                    })
            
            return results[:max_results]
            
        except Exception as e:
            logger.error(f"Error searching web: {e}")
            return []
    
    async def fetch_webpage_content(self, url: str, max_length: int = 2000) -> Optional[str]:
        """
        Fetch and extract text content from a webpage
        """
        try:
            if not self.session:
                async with aiohttp.ClientSession(headers=self.headers) as session:
                    return await self._fetch_with_session(session, url, max_length)
            else:
                return await self._fetch_with_session(self.session, url, max_length)
                
        except Exception as e:
            logger.error(f"Error fetching webpage {url}: {e}")
            return None
    
    async def _fetch_with_session(self, session: aiohttp.ClientSession, url: str, max_length: int) -> Optional[str]:
        """Helper method to fetch content with existing session"""
        try:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.decompose()
                    
                    # Get text content
                    text = soup.get_text()
                    
                    # Clean up whitespace
                    lines = (line.strip() for line in text.splitlines())
                    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                    text = ' '.join(chunk for chunk in chunks if chunk)
                    
                    # Truncate if too long
                    if len(text) > max_length:
                        text = text[:max_length] + "..."
                    
                    return text
                else:
                    logger.warning(f"Failed to fetch {url}: HTTP {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error in _fetch_with_session: {e}")
            return None
    
    async def get_current_time(self) -> Dict[str, Any]:
        """Get current time and date information"""
        import datetime
        now = datetime.datetime.now()
        return {
            'current_time': now.strftime('%H:%M:%S'),
            'current_date': now.strftime('%Y-%m-%d'),
            'day_of_week': now.strftime('%A'),
            'timezone': 'Local time',
            'timestamp': now.isoformat()
        }
    
    async def get_weather_info(self, location: str = "current") -> Optional[Dict[str, Any]]:
        """
        Get weather information (simplified - in production you'd use a weather API)
        """
        try:
            # This is a placeholder - in a real implementation you'd use a weather API
            # For now, return a message about the capability
            return {
                'location': location,
                'message': 'Weather information requires a weather API key (like OpenWeatherMap)',
                'capability': 'Available with API integration'
            }
        except Exception as e:
            logger.error(f"Error getting weather: {e}")
            return None


# Global web search instance
web_search = WebSearch()


async def search_internet(query: str, max_results: int = 3) -> str:
    """
    Search the internet and return formatted results
    """
    try:
        async with WebSearch() as search:
            results = await search.search_web(query, max_results)
            
            if not results:
                return "I couldn't find any information about that on the web."
            
            response = f"🌐 **Web Search Results for: '{query}'**\n\n"
            
            for i, result in enumerate(results, 1):
                response += f"**{i}. {result['title']}**\n"
                response += f"{result['snippet'][:200]}...\n"
                if result['url']:
                    response += f"Source: {result['url']}\n"
                response += "\n"
            
            return response
            
    except Exception as e:
        logger.error(f"Error in search_internet: {e}")
        return "Sorry, I encountered an error while searching the web."


async def get_webpage_summary(url: str) -> str:
    """
    Fetch and summarize a webpage
    """
    try:
        async with WebSearch() as search:
            content = await search.fetch_webpage_content(url)
            
            if not content:
                return f"Sorry, I couldn't access the webpage at {url}"
            
            # Create a simple summary
            summary = content[:500] + "..." if len(content) > 500 else content
            
            return f"📄 **Webpage Summary: {url}**\n\n{summary}"
            
    except Exception as e:
        logger.error(f"Error in get_webpage_summary: {e}")
        return f"Sorry, I couldn't summarize the webpage at {url}"


async def get_current_time_info() -> str:
    """
    Get current time and date information
    """
    try:
        async with WebSearch() as search:
            time_info = await search.get_current_time()
            
            return f"🕐 **Current Time Information**\n\n" \
                   f"**Time:** {time_info['current_time']}\n" \
                   f"**Date:** {time_info['current_date']}\n" \
                   f"**Day:** {time_info['day_of_week']}\n" \
                   f"**Timezone:** {time_info['timezone']}"
                   
    except Exception as e:
        logger.error(f"Error getting time info: {e}")
        return "Sorry, I couldn't get the current time information." 