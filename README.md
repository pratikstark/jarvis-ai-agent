# Jarvis AI Agent 🤖

A cloud-based Python AI agent that runs continuously on Render, maintains conversation history, and provides intelligent responses using OpenRouter's AI models.

## Features

- 🌐 **Cloud-based**: Runs continuously on Render with automatic scaling
- 💬 **Conversation Memory**: Stores message history in Supabase or local JSON
- 🧠 **AI Integration**: Uses OpenRouter to access Claude, GPT, and other AI models
- 📝 **Comprehensive Logging**: Logs agent thoughts and decisions
- 🔄 **RESTful API**: Simple HTTP endpoints for easy integration
- 🛡️ **Error Handling**: Graceful fallbacks and error recovery
- 📊 **Health Monitoring**: Built-in health checks and status endpoints

## Quick Start

### 1. Deploy to Render (Recommended)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy/schema-new?template=https://github.com/yourusername/jarvis-ai-agent)

1. Click the "Deploy to Render" button above
2. Connect your GitHub repository
3. Set environment variables in Render dashboard:
   - `OPENROUTER_API_KEY`: Your OpenRouter API key
   - `SUPABASE_URL`: (Optional) Your Supabase URL
   - `SUPABASE_KEY`: (Optional) Your Supabase anon key
   - `AI_MODEL`: (Optional) AI model to use (default: `anthropic/claude-3-sonnet`)

### 2. Local Development

```bash
# Clone the repository
git clone <your-repo-url>
cd jarvis-ai-agent

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.example .env
# Edit .env with your API keys

# Run the server
python main.py
```

## API Endpoints

### POST `/talk`
Send a message to the AI agent.

**Request:**
```json
{
  "text": "Hello, how are you?",
  "user_id": "user123"
}
```

**Response:**
```json
{
  "reply": "Hello! I'm doing great, thank you for asking. How can I help you today?",
  "user_id": "user123",
  "message_id": "user123_1703123456.789",
  "timestamp": "2023-12-21T10:30:56.789Z"
}
```

### GET `/history/{user_id}`
Get conversation history for a user.

**Response:**
```json
{
  "user_id": "user123",
  "messages": [
    {
      "role": "user",
      "content": "Hello",
      "timestamp": "2023-12-21T10:30:00Z"
    },
    {
      "role": "assistant",
      "content": "Hi there! How can I help you?",
      "timestamp": "2023-12-21T10:30:01Z"
    }
  ],
  "count": 2
}
```

### DELETE `/history/{user_id}`
Clear conversation history for a user.

### GET `/`
Health check endpoint.

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `OPENROUTER_API_KEY` | Your OpenRouter API key | Yes | - |
| `AI_MODEL` | AI model to use | No | `anthropic/claude-3-sonnet` |
| `SUPABASE_URL` | Supabase project URL | No | - |
| `SUPABASE_KEY` | Supabase anon key | No | - |
| `PORT` | Server port | No | `8000` |

## Supported AI Models

The agent supports all models available through OpenRouter:

- **Claude Models**: `anthropic/claude-3-sonnet`, `anthropic/claude-3-opus`, `anthropic/claude-3-haiku`
- **GPT Models**: `openai/gpt-4`, `openai/gpt-3.5-turbo`, `openai/gpt-4-turbo`
- **Other Models**: `google/palm-2-chat-bison`, `meta-llama/llama-2-70b-chat`, etc.

## Database Setup (Optional)

If using Supabase, create these tables:

### message_history
```sql
CREATE TABLE message_history (
  user_id TEXT PRIMARY KEY,
  messages JSONB NOT NULL DEFAULT '[]',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### agent_logs
```sql
CREATE TABLE agent_logs (
  id SERIAL PRIMARY KEY,
  timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  user_id TEXT NOT NULL,
  user_message TEXT NOT NULL,
  ai_reply TEXT NOT NULL,
  context JSONB,
  model_used TEXT,
  history_length INTEGER,
  thoughts TEXT
);
```

## Usage Examples

### Python Client
```python
import requests

# Send a message
response = requests.post("https://your-app.onrender.com/talk", json={
    "text": "What's the weather like?",
    "user_id": "user123"
})

print(response.json()["reply"])

# Get history
history = requests.get("https://your-app.onrender.com/history/user123")
print(history.json()["messages"])
```

### JavaScript Client
```javascript
// Send a message
const response = await fetch("https://your-app.onrender.com/talk", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
        text: "Hello, AI!",
        user_id: "user123"
    })
});

const data = await response.json();
console.log(data.reply);
```

### cURL
```bash
# Send a message
curl -X POST "https://your-app.onrender.com/talk" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello!", "user_id": "user123"}'

# Get history
curl "https://your-app.onrender.com/history/user123"
```

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client App    │───▶│  Jarvis Agent   │───▶│   OpenRouter    │
│                 │    │   (FastAPI)     │    │   (AI Models)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Supabase      │
                       │   (Database)    │
                       └─────────────────┘
```

## Logging

The agent logs all activities to `agent.log` with rotation:
- Message processing
- AI API calls
- Database operations
- Error handling
- Agent thoughts and decisions

## Monitoring

- **Health Check**: `GET /` returns service status
- **Logs**: Check `agent.log` for detailed activity
- **Render Dashboard**: Monitor deployment status and logs

## Troubleshooting

### Common Issues

1. **"AI responses will be simulated"**
   - Set your `OPENROUTER_API_KEY` environment variable

2. **"Using local JSON storage"**
   - Set `SUPABASE_URL` and `SUPABASE_KEY` for cloud storage

3. **Deployment fails**
   - Check that all required environment variables are set
   - Verify your API keys are valid

### Getting Help

- Check the logs: `agent.log` for detailed error information
- Monitor Render dashboard for deployment issues
- Verify API keys and database connections

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

---

**Built with ❤️ using FastAPI, OpenRouter, and Render** 