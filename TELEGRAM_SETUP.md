# Telegram Bot Setup Guide 🤖

This guide will help you set up your Jarvis AI Agent to work with Telegram, so you can chat with your AI assistant directly through Telegram!

## Quick Setup (5 minutes)

### Step 1: Create a Telegram Bot

1. **Open Telegram** and search for `@BotFather`
2. **Send the command** `/newbot`
3. **Choose a name** for your bot (e.g., "My Jarvis AI")
4. **Choose a username** (must end with 'bot', e.g., "my_jarvis_bot")
5. **Copy the token** that BotFather gives you (it looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Step 2: Add the Token to Your Environment

1. **Open your `.env` file** in the jarvis project
2. **Add this line:**
   ```
   TELEGRAM_BOT_TOKEN=your_token_here
   ```
3. **Replace `your_token_here`** with the token you got from BotFather

### Step 3: Start Your Server

```bash
# Make sure you're in the jarvis directory
cd jarvis

# Activate your virtual environment
source venv/bin/activate

# Start the server
python3 main.py
```

### Step 4: Start Chatting!

1. **Find your bot** on Telegram (using the username you created)
2. **Send `/start`** to begin
3. **Start chatting** with your AI!

## Available Commands

Once your bot is running, you can use these commands:

- **`/start`** - Welcome message and introduction
- **`/help`** - Show all available commands
- **`/history`** - Show your recent conversation history
- **`/clear`** - Clear your conversation history and start fresh
- **Any message** - Chat with your AI assistant!

## Example Conversation

```
You: /start
Bot: 🤖 Welcome to Jarvis AI Agent!

I'm your personal AI assistant. You can:
• Send me any message and I'll respond
• Use /history to see our conversation
• Use /clear to start fresh
• Use /help for more commands

Just start chatting with me!

You: What's the weather like today?
Bot: I don't have access to real-time weather data, but I can help you with many other things! What would you like to know about?

You: Tell me a joke
Bot: Here's a classic one: Why don't scientists trust atoms? Because they make up everything! 😄
```

## Troubleshooting

### "Bot not responding"
- Make sure your server is running (`python3 main.py`)
- Check that your `TELEGRAM_BOT_TOKEN` is correct
- Look at the server logs for any error messages

### "Invalid token"
- Double-check the token from BotFather
- Make sure there are no extra spaces in your `.env` file
- The token should look like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`

### "Server won't start"
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Check that your `.env` file is in the correct location
- Look for any error messages in the terminal

### "Bot works locally but not on cloud"
- Make sure you added `TELEGRAM_BOT_TOKEN` to your cloud environment variables
- Check that your cloud deployment is running
- The bot needs to be able to reach your server URL

## Security Notes

- **Never share your bot token** - it gives full control of your bot
- **Keep your `.env` file private** - don't commit it to public repositories
- **Use environment variables** in cloud deployments, not hardcoded tokens

## Advanced Features

### Custom Bot Commands

You can add custom commands by editing `telegram_bot.py`. For example:

```python
async def custom_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("This is a custom command!")
```

### Bot Settings

You can customize your bot with BotFather:
- `/setdescription` - Set bot description
- `/setabouttext` - Set about text
- `/setuserpic` - Set bot profile picture
- `/setcommands` - Set command list

### Webhook vs Polling

By default, the bot uses polling (continuously checks for messages). For production, you might want to use webhooks for better performance.

## Need Help?

If you're having trouble:
1. Check the server logs for error messages
2. Make sure all environment variables are set correctly
3. Test the basic API first: `curl http://localhost:8000/`
4. Try the test script: `python3 test_telegram.py`

## What's Next?

Once your Telegram bot is working, you can:
- Build a web interface for your AI
- Add more AI models and capabilities
- Integrate with other messaging platforms
- Add file upload/download features
- Create custom AI personalities

---

**Happy chatting with your AI assistant! 🤖✨** 