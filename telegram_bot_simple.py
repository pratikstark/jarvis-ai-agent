import os
import threading
import time
from datetime import datetime
from typing import Dict, Any
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from loguru import logger

class SimpleTelegramBot:
    def __init__(self, token: str, jarvis_url: str):
        self.token = token
        self.jarvis_url = jarvis_url
        self.updater = None
        self.is_running = False
        
    def setup_handlers(self, dispatcher):
        """Set up command and message handlers"""
        # Command handlers
        dispatcher.add_handler(CommandHandler("start", self.start_command))
        dispatcher.add_handler(CommandHandler("help", self.help_command))
        dispatcher.add_handler(CommandHandler("history", self.history_command))
        dispatcher.add_handler(CommandHandler("clear", self.clear_command))
        
        # Message handler for all text messages
        dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, self.handle_message))
        
    def start_command(self, update: Update, context: CallbackContext):
        """Handle /start command"""
        user_id = str(update.effective_user.id)
        welcome_message = (
            "🤖 **Welcome to Jarvis AI Agent!**\n\n"
            "I'm your personal AI assistant. You can:\n"
            "• Send me any message and I'll respond\n"
            "• Use /history to see our conversation\n"
            "• Use /clear to start fresh\n"
            "• Use /help for more commands\n\n"
            "Just start chatting with me!"
        )
        update.message.reply_text(welcome_message, parse_mode='Markdown')
        
    def help_command(self, update: Update, context: CallbackContext):
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
        update.message.reply_text(help_message, parse_mode='Markdown')
        
    def history_command(self, update: Update, context: CallbackContext):
        """Handle /history command"""
        user_id = str(update.effective_user.id)
        
        try:
            response = requests.get(f"{self.jarvis_url}/history/{user_id}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                messages = data.get("messages", [])
                
                if not messages:
                    update.message.reply_text("No conversation history yet. Start chatting with me!")
                    return
                
                # Show last 5 messages
                recent_messages = messages[-5:]
                history_text = "📚 **Recent Conversation:**\n\n"
                
                for msg in recent_messages:
                    role = "👤 You" if msg["role"] == "user" else "🤖 Jarvis"
                    content = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
                    history_text += f"**{role}:** {content}\n\n"
                
                update.message.reply_text(history_text, parse_mode='Markdown')
            else:
                update.message.reply_text("❌ Could not fetch conversation history.")
                
        except Exception as e:
            logger.error(f"Error fetching history: {e}")
            update.message.reply_text("❌ Error fetching conversation history.")
            
    def clear_command(self, update: Update, context: CallbackContext):
        """Handle /clear command"""
        user_id = str(update.effective_user.id)
        
        try:
            response = requests.delete(f"{self.jarvis_url}/history/{user_id}", timeout=10)
            
            if response.status_code == 200:
                update.message.reply_text("🗑️ Conversation history cleared! Let's start fresh.")
            else:
                update.message.reply_text("❌ Could not clear conversation history.")
                
        except Exception as e:
            logger.error(f"Error clearing history: {e}")
            update.message.reply_text("❌ Error clearing conversation history.")
            
    def handle_message(self, update: Update, context: CallbackContext):
        """Handle incoming text messages"""
        user_id = str(update.effective_user.id)
        message_text = update.message.text
        
        # Show typing indicator
        try:
            context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        except:
            pass  # Ignore typing indicator errors
        
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
                update.message.reply_text(ai_reply)
            else:
                update.message.reply_text("❌ Sorry, I'm having trouble processing your message right now.")
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            update.message.reply_text("❌ Sorry, I encountered an error. Please try again later.")
    
    def start_bot(self):
        """Start the Telegram bot in a separate thread"""
        try:
            logger.info("🤖 Starting Telegram bot...")
            self.updater = Updater(token=self.token, use_context=True)
            self.setup_handlers(self.updater.dispatcher)
            
            # Start polling in a separate thread
            self.updater.start_polling(drop_pending_updates=True)
            self.is_running = True
            logger.info("✅ Telegram bot is running!")
            
        except Exception as e:
            logger.error(f"Failed to start Telegram bot: {e}")
            raise
    
    def stop_bot(self):
        """Stop the Telegram bot"""
        logger.info("🛑 Stopping Telegram bot...")
        try:
            if self.updater and self.is_running:
                self.updater.stop()
                self.is_running = False
        except Exception as e:
            logger.warning(f"Warning stopping updater: {e}")
        logger.info("✅ Telegram bot stopped!")

# Global bot instance
telegram_bot = None

def start_telegram_bot(token: str, jarvis_url: str):
    """Start the Telegram bot in a separate thread"""
    global telegram_bot
    try:
        telegram_bot = SimpleTelegramBot(token, jarvis_url)
        
        # Start bot in a separate thread
        bot_thread = threading.Thread(target=telegram_bot.start_bot, daemon=True)
        bot_thread.start()
        
        # Give it a moment to start
        time.sleep(2)
        
    except Exception as e:
        logger.error(f"Failed to start Telegram bot: {e}")
        raise

def stop_telegram_bot():
    """Stop the Telegram bot"""
    global telegram_bot
    if telegram_bot:
        telegram_bot.stop_bot() 