import os
import asyncio
from datetime import datetime
from typing import Dict, Any
import httpx
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from loguru import logger

class TelegramBot:
    def __init__(self, token: str, jarvis_url: str):
        self.token = token
        self.jarvis_url = jarvis_url
        self.application = Application.builder().token(token).build()
        self.setup_handlers()
        
    def setup_handlers(self):
        """Set up command and message handlers"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("history", self.history_command))
        self.application.add_handler(CommandHandler("clear", self.clear_command))
        
        # Message handler for all text messages
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
        
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        await update.message.reply_text(help_message, parse_mode='Markdown')
        
    async def history_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /history command"""
        user_id = str(update.effective_user.id)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.jarvis_url}/history/{user_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    messages = data.get("messages", [])
                    
                    if not messages:
                        await update.message.reply_text("No conversation history yet. Start chatting with me!")
                        return
                    
                    # Show last 5 messages
                    recent_messages = messages[-5:]
                    history_text = "📚 **Recent Conversation:**\n\n"
                    
                    for msg in recent_messages:
                        role = "👤 You" if msg["role"] == "user" else "🤖 Jarvis"
                        content = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
                        history_text += f"**{role}:** {content}\n\n"
                    
                    await update.message.reply_text(history_text, parse_mode='Markdown')
                else:
                    await update.message.reply_text("❌ Could not fetch conversation history.")
                    
        except Exception as e:
            logger.error(f"Error fetching history: {e}")
            await update.message.reply_text("❌ Error fetching conversation history.")
            
    async def clear_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /clear command"""
        user_id = str(update.effective_user.id)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(f"{self.jarvis_url}/history/{user_id}")
                
                if response.status_code == 200:
                    await update.message.reply_text("🗑️ Conversation history cleared! Let's start fresh.")
                else:
                    await update.message.reply_text("❌ Could not clear conversation history.")
                    
        except Exception as e:
            logger.error(f"Error clearing history: {e}")
            await update.message.reply_text("❌ Error clearing conversation history.")
            
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming text messages"""
        user_id = str(update.effective_user.id)
        message_text = update.message.text
        
        # Show typing indicator
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        try:
            # Send message to Jarvis AI Agent
            async with httpx.AsyncClient() as client:
                response = await client.post(
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
                    await update.message.reply_text(ai_reply)
                else:
                    await update.message.reply_text("❌ Sorry, I'm having trouble processing your message right now.")
                    
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await update.message.reply_text("❌ Sorry, I encountered an error. Please try again later.")
            
    async def start(self):
        """Start the Telegram bot"""
        logger.info("🤖 Starting Telegram bot...")
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        logger.info("✅ Telegram bot is running!")
        
    async def stop(self):
        """Stop the Telegram bot"""
        logger.info("🛑 Stopping Telegram bot...")
        await self.application.updater.stop()
        await self.application.stop()
        await self.application.shutdown()
        logger.info("✅ Telegram bot stopped!")

# Global bot instance
telegram_bot = None

async def start_telegram_bot(token: str, jarvis_url: str):
    """Start the Telegram bot"""
    global telegram_bot
    telegram_bot = TelegramBot(token, jarvis_url)
    await telegram_bot.start()

async def stop_telegram_bot():
    """Stop the Telegram bot"""
    global telegram_bot
    if telegram_bot:
        await telegram_bot.stop() 