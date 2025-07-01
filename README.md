# Jarvis AI Agent 🤖

A simple AI chat agent that remembers your conversations and runs in the cloud. Think of it as your personal AI assistant that you can talk to anytime.

## What it does

- 💬 **Remembers conversations** - It keeps track of what you've talked about
- 🌐 **Always available** - Runs in the cloud so you can chat anytime
- 🧠 **Smart responses** - Uses advanced AI models to give helpful answers
- 📱 **Easy to use** - Just send a message and get a reply
- 🔒 **Private** - Your conversations stay private

## Quick Start

### Option 1: Deploy to the cloud (Recommended)

1. Click the "Deploy to Render" button below
2. Connect your GitHub account
3. Add your API keys in the settings (see setup guide below)
4. Wait a few minutes for deployment
5. Start chatting with your AI!

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy/schema-new?template=https://github.com/pratikstark/jarvis-ai-agent)

### Option 2: Run locally

```bash
# Download the code
git clone https://github.com/pratikstark/jarvis-ai-agent.git
cd jarvis-ai-agent

# Install Python packages
pip install -r requirements.txt

# Set up your API keys (see setup guide)
cp env.example .env
# Edit .env with your keys

# Start the server
python main.py
```

## Setup Guide

### 1. Get an AI API Key

You'll need an API key to use AI models. Here are your options:

**Option A: OpenRouter (Recommended)**
- Go to [OpenRouter](https://openrouter.ai/)
- Sign up for a free account
- Get your API key from the dashboard
- This gives you access to Claude, GPT, and other models

**Option B: OpenAI**
- Go to [OpenAI](https://platform.openai.com/)
- Create an account and get an API key

### 2. Set up Telegram Bot (Optional)

To chat with your AI through Telegram:

1. **Create a Telegram Bot:**
   - Open Telegram and search for `@BotFather`
   - Send `/newbot` command
   - Follow the instructions to create your bot
   - Copy the token you receive

2. **Add the token to your environment:**
   - Add `TELEGRAM_BOT_TOKEN=your_token_here` to your `.env` file
   - Or add it to your cloud deployment environment variables

3. **Start chatting:**
   - Find your bot on Telegram (using the username you created)
   - Send `/start` to begin
   - Start chatting with your AI!

### 3. Set up your deployment

When you deploy to Render (or any cloud platform), you'll need to add these settings:

**Required:**
- `OPENROUTER_API_KEY` - Your OpenRouter API key

**Optional:**
- `AI_MODEL` - Which AI model to use (default: `anthropic/claude-3-sonnet`)
- `TELEGRAM_BOT_TOKEN` - Your Telegram bot token (for Telegram integration)
- `SUPABASE_URL` - For cloud storage (optional)
- `SUPABASE_KEY` - For cloud storage (optional)

### 4. Test it out

Once deployed, you can:

**Send a message:**
```bash
curl -X POST "https://your-app.onrender.com/talk" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello!", "user_id": "me"}'
```

**Get your chat history:**
```bash
curl "https://your-app.onrender.com/history/me"
```

**Or chat via Telegram:**
- Find your bot on Telegram
- Send any message to start chatting
- Use `/help` to see available commands

## How to use

### Send a message
```
POST /talk
{
  "text": "What's the weather like?",
  "user_id": "your-name"
}
```

### Get your chat history
```
GET /history/your-name
```

### Check if it's working
```
GET /
```

## Features

- **Conversation memory** - Remembers what you've talked about
- **Telegram integration** - Chat with your AI through Telegram
- **Multiple AI models** - Use Claude, GPT, or other models
- **Cloud storage** - Optional database to store conversations
- **Simple API** - Easy to integrate with apps
- **Always online** - Runs continuously in the cloud

## Privacy & Security

- Your API keys are stored securely in environment variables
- No private information is stored in the code
- Conversations are only stored if you set up cloud storage
- You can delete your chat history anytime

## Troubleshooting

**"AI responses will be simulated"**
- You need to set your API key in the environment variables

**"Service not responding"**
- Check if your deployment is running
- Free services may sleep after inactivity

**"Deployment failed"**
- Make sure all required environment variables are set
- Check that your API keys are valid

## Support

If you run into issues:
1. Check the logs in your deployment dashboard
2. Make sure your API keys are correct
3. Try the local version first to test

## What's next?

Once you have this running, you can:
- Build a web interface to chat with your AI
- Connect it to other apps
- Add more features like file uploads
- Customize the AI's personality

---

**Made with ❤️ using FastAPI and modern AI models** 