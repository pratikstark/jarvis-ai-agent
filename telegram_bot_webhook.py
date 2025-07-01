import os
import json
import threading
import time
from datetime import datetime
from typing import Dict, Any
import requests
from loguru import logger

class WebhookTelegramBot:
    def __init__(self, token: str, jarvis_url: str):
        self.token = token
        self.jarvis_url = jarvis_url
        self.api_url = f"https://api.telegram.org/bot{token}"
        self.is_running = False
        self.last_update_id = 0
        
    def get_updates(self):
        """Get updates from Telegram"""
        try:
            params = {
                'offset': self.last_update_id + 1,
                'timeout': 30
            }
            response = requests.get(f"{self.api_url}/getUpdates", params=params, timeout=35)
            if response.status_code == 200:
                data = response.json()
                if data.get('ok') and data.get('result'):
                    return data['result']
            return []
        except Exception as e:
            logger.error(f"Error getting updates: {e}")
            return []
    
    def send_message(self, chat_id: str, text: str, parse_mode: str = None):
        """Send message to Telegram"""
        try:
            data = {
                'chat_id': chat_id,
                'text': text
            }
            if parse_mode:
                data['parse_mode'] = parse_mode
                
            response = requests.post(f"{self.api_url}/sendMessage", json=data, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False
    
    def send_chat_action(self, chat_id: str, action: str = "typing"):
        """Send chat action (typing indicator)"""
        try:
            data = {
                'chat_id': chat_id,
                'action': action
            }
            requests.post(f"{self.api_url}/sendChatAction", json=data, timeout=5)
        except Exception as e:
            logger.warning(f"Error sending chat action: {e}")
    
    def handle_start_command(self, chat_id: str, user_id: str):
        """Handle /start command"""
        welcome_message = (
            "🤖 **Welcome to Jarvis AI Agent!**\n\n"
            "I'm your personal AI assistant. You can:\n"
            "• Send me any message and I'll respond\n"
            "• Use /history to see our conversation\n"
            "• Use /clear to start fresh\n"
            "• Use /help for more commands\n\n"
            "Just start chatting with me!"
        )
        self.send_message(chat_id, welcome_message, "Markdown")
    
    def handle_help_command(self, chat_id: str, user_id: str):
        """Handle /help command"""
        help_message = (
            "🤖 **Jarvis AI Agent Commands:**\n\n"
            "• Just send me a message to chat!\n"
            "• `/start` - Welcome message\n"
            "• `/help` - Show this help\n"
            "• `/history` - Show our conversation history\n"
            "• `/clear` - Clear our conversation history\n\n"
            "I remember our conversations and can help with anything!"
        )
        self.send_message(chat_id, help_message, "Markdown")
    
    def handle_history_command(self, chat_id: str, user_id: str):
        """Handle /history command"""
        try:
            response = requests.get(f"{self.jarvis_url}/history/{user_id}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                messages = data.get("messages", [])
                
                if not messages:
                    self.send_message(chat_id, "No conversation history yet. Start chatting with me!")
                    return
                
                # Show last 5 messages
                recent_messages = messages[-5:]
                history_text = "📚 **Recent Conversation:**\n\n"
                
                for msg in recent_messages:
                    role = "👤 You" if msg["role"] == "user" else "🤖 Jarvis"
                    content = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
                    history_text += f"**{role}:** {content}\n\n"
                
                self.send_message(chat_id, history_text, "Markdown")
            else:
                self.send_message(chat_id, "❌ Could not fetch conversation history.")
                
        except Exception as e:
            logger.error(f"Error fetching history: {e}")
            self.send_message(chat_id, "❌ Error fetching conversation history.")
    
    def handle_clear_command(self, chat_id: str, user_id: str):
        """Handle /clear command"""
        try:
            response = requests.delete(f"{self.jarvis_url}/history/{user_id}", timeout=10)
            
            if response.status_code == 200:
                self.send_message(chat_id, "🗑️ Conversation history cleared! Let's start fresh.")
            else:
                self.send_message(chat_id, "❌ Could not clear conversation history.")
                
        except Exception as e:
            logger.error(f"Error clearing history: {e}")
            self.send_message(chat_id, "❌ Error clearing conversation history.")
    
    def handle_message(self, chat_id: str, user_id: str, message_text: str):
        """Handle regular message"""
        # Show typing indicator
        self.send_chat_action(chat_id, "typing")
        
        try:
            # Send message to Jarvis AI Agent
            response = requests.post(
                f"{self.jarvis_url}/talk",
                json={
                    "text": message_text,
                    "user_id": user_id
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_reply = data.get("reply", "Sorry, I couldn't process that.")
                
                # Send AI response
                self.send_message(chat_id, ai_reply)
            else:
                self.send_message(chat_id, "❌ Sorry, I'm having trouble processing your message right now.")
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            self.send_message(chat_id, "❌ Sorry, I encountered an error. Please try again later.")
    
    def process_update(self, update):
        """Process a single update from Telegram"""
        try:
            if 'message' not in update:
                return
            
            message = update['message']
            chat_id = str(message['chat']['id'])
            user_id = str(message['from']['id'])
            
            if 'text' not in message:
                return
            
            text = message['text'].strip()
            
            # Handle commands
            if text.startswith('/'):
                if text == '/start':
                    self.handle_start_command(chat_id, user_id)
                elif text == '/help':
                    self.handle_help_command(chat_id, user_id)
                elif text == '/history':
                    self.handle_history_command(chat_id, user_id)
                elif text == '/clear':
                    self.handle_clear_command(chat_id, user_id)
                else:
                    self.send_message(chat_id, "Unknown command. Use /help to see available commands.")
            else:
                # Handle regular message
                self.handle_message(chat_id, user_id, text)
                
        except Exception as e:
            logger.error(f"Error processing update: {e}")
    
    def poll_updates(self):
        """Poll for updates from Telegram"""
        logger.info("🤖 Starting Telegram bot polling...")
        self.is_running = True
        
        while self.is_running:
            try:
                updates = self.get_updates()
                
                for update in updates:
                    self.process_update(update)
                    self.last_update_id = update['update_id']
                
                # Small delay to avoid hitting rate limits
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error in polling loop: {e}")
                time.sleep(5)  # Wait longer on error
    
    def start_bot(self):
        """Start the bot in a separate thread"""
        try:
            # Test bot connection
            response = requests.get(f"{self.api_url}/getMe", timeout=10)
            if response.status_code == 200:
                bot_info = response.json()
                if bot_info.get('ok'):
                    logger.info(f"✅ Connected to Telegram bot: {bot_info['result']['first_name']}")
                else:
                    raise Exception("Invalid bot token")
            else:
                raise Exception("Could not connect to Telegram API")
            
            # Start polling in a separate thread
            bot_thread = threading.Thread(target=self.poll_updates, daemon=True)
            bot_thread.start()
            logger.info("✅ Telegram bot is running!")
            
        except Exception as e:
            logger.error(f"Failed to start Telegram bot: {e}")
            raise
    
    def stop_bot(self):
        """Stop the bot"""
        logger.info("🛑 Stopping Telegram bot...")
        self.is_running = False
        logger.info("✅ Telegram bot stopped!")

# Global bot instance
telegram_bot = None

def start_telegram_bot(token: str, jarvis_url: str):
    """Start the Telegram bot"""
    global telegram_bot
    try:
        telegram_bot = WebhookTelegramBot(token, jarvis_url)
        telegram_bot.start_bot()
    except Exception as e:
        logger.error(f"Failed to start Telegram bot: {e}")
        raise

def stop_telegram_bot():
    """Stop the Telegram bot"""
    global telegram_bot
    if telegram_bot:
        telegram_bot.stop_bot() 