#!/usr/bin/env python3
"""
Test script for Telegram bot functionality
This script shows how to set up and test the Telegram bot integration
"""

import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_telegram_setup():
    """Check if Telegram bot is properly configured"""
    print("🤖 Telegram Bot Setup Check")
    print("=" * 40)
    
    # Check if token is set
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if token:
        print("✅ TELEGRAM_BOT_TOKEN is set")
        print(f"   Token: {token[:10]}...{token[-10:]}")
    else:
        print("❌ TELEGRAM_BOT_TOKEN is not set")
        print("   Add it to your .env file to enable Telegram bot")
    
    # Check if server is running
    try:
        import httpx
        response = httpx.get("http://localhost:8000/")
        if response.status_code == 200:
            print("✅ Jarvis server is running")
        else:
            print("❌ Jarvis server is not responding")
    except Exception as e:
        print(f"❌ Cannot connect to Jarvis server: {e}")
    
    print("\n📋 Setup Instructions:")
    print("1. Create a Telegram bot with @BotFather")
    print("2. Add TELEGRAM_BOT_TOKEN to your .env file")
    print("3. Start the server with: python3 main.py")
    print("4. Find your bot on Telegram and start chatting!")
    
    print("\n🔧 Commands available in Telegram:")
    print("• /start - Welcome message")
    print("• /help - Show help")
    print("• /history - Show conversation history")
    print("• /clear - Clear conversation history")
    print("• Any message - Chat with your AI!")

if __name__ == "__main__":
    check_telegram_setup() 