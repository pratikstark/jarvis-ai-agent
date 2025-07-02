# Deployment Instructions 🚀

This guide will help you deploy your Jarvis AI Agent to Render for continuous operation.

## Prerequisites

1. **OpenRouter API Key**: Get one from [OpenRouter](https://openrouter.ai/)
2. **GitHub Account**: To host your code
3. **Render Account**: Free tier available at [Render](https://render.com/)

## Step 1: Prepare Your Repository

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Jarvis AI Agent"
   git branch -M main
   git remote add origin https://github.com/yourusername/jarvis-ai-agent.git
   git push -u origin main
   ```

2. **Verify Files**: Ensure these files are in your repository:
   - `main.py` - Main application
   - `requirements.txt` - Python dependencies
   - `render.yaml` - Render configuration
   - `README.md` - Documentation

## Step 2: Deploy to Render

### Option A: One-Click Deploy (Recommended)

1. Click the "Deploy to Render" button in the README
2. Connect your GitHub account
3. Select your repository
4. Render will automatically detect the `render.yaml` configuration

### Option B: Manual Deploy

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: `jarvis-ai-agent`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`

## Step 3: Configure Environment Variables

In your Render service dashboard, go to "Environment" and add these variables:

### Required Variables
```
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

### Optional Variables
```
AI_MODEL=anthropic/claude-3-sonnet
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_anon_key_here
```

## Step 4: Set Up Supabase (Optional)

If you want to use Supabase for persistent storage:

1. **Create Supabase Project**:
   - Go to [Supabase](https://supabase.com/)
   - Create a new project
   - Wait for setup to complete

2. **Get Credentials**:
   - Go to Settings → API
   - Copy the "Project URL" and "anon public" key

3. **Set Up Database**:
   - Go to SQL Editor
   - Run the contents of `supabase_setup.sql`

4. **Add to Render**:
   - Add `SUPABASE_URL` and `SUPABASE_KEY` to your environment variables

## Step 5: Test Your Deployment

1. **Check Health**: Visit your Render URL (e.g., `https://jarvis-ai-agent.onrender.com/`)
2. **Test API**: Use the test script:
   ```bash
   # Update BASE_URL in test_agent.py
   python test_agent.py
   ```

3. **Manual Test**:
   ```bash
   curl -X POST "https://your-app.onrender.com/talk" \
     -H "Content-Type: application/json" \
     -d '{"text": "Hello!", "user_id": "test123"}'
   ```

## Step 6: Monitor and Maintain

### View Logs
- Go to your Render service dashboard
- Click "Logs" tab
- Monitor for errors and agent activity

### Check Health
- Visit `https://your-app.onrender.com/` for status
- Response should show "healthy" status

### Scale (if needed)
- Free tier: 750 hours/month
- Paid tiers available for more resources

## Troubleshooting

### Common Issues

1. **Build Fails**:
   - Check `requirements.txt` syntax
   - Verify Python version compatibility
   - Check build logs in Render dashboard

2. **Runtime Errors**:
   - Check environment variables are set correctly
   - Verify API keys are valid
   - Check application logs

3. **API Not Responding**:
   - Verify the service is running (green status)
   - Check if the service is sleeping (free tier limitation)
   - Test with a simple GET request first

4. **Database Connection Issues**:
   - Verify Supabase credentials
   - Check if tables exist
   - Ensure RLS policies are configured

### Getting Help

1. **Check Logs**: Always check Render logs first
2. **Test Locally**: Run `python main.py` locally to isolate issues
3. **Verify Configuration**: Double-check all environment variables
4. **API Documentation**: Visit `/docs` on your deployed app for interactive API docs

## Alternative Deployment Options

### Railway
1. Connect your GitHub repo to Railway
2. Set environment variables
3. Deploy automatically

### Heroku
1. Create `Procfile`:
   ```
   web: python main.py
   ```
2. Deploy using Heroku CLI or GitHub integration

### DigitalOcean App Platform
1. Connect your repository
2. Configure as Python app
3. Set environment variables

## Security Considerations

1. **API Keys**: Never commit API keys to your repository
2. **Environment Variables**: Use Render's secure environment variable system
3. **CORS**: The app allows all origins for development; restrict for production
4. **Rate Limiting**: Consider adding rate limiting for production use

## Cost Optimization

1. **Free Tier**: Render free tier includes 750 hours/month
2. **Sleep Mode**: Free services sleep after 15 minutes of inactivity
3. **Warm-up**: First request after sleep may take 30-60 seconds
4. **Upgrade**: Consider paid tier for always-on service

---

**Your Jarvis AI Agent is now ready to serve! 🤖✨** 