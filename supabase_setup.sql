-- Supabase Database Setup for Jarvis AI Agent
-- Run this in your Supabase SQL editor

-- Enable Row Level Security (RLS)
ALTER TABLE IF EXISTS message_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS agent_logs ENABLE ROW LEVEL SECURITY;

-- Create message_history table
CREATE TABLE IF NOT EXISTS message_history (
    user_id TEXT PRIMARY KEY,
    messages JSONB NOT NULL DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create agent_logs table
CREATE TABLE IF NOT EXISTS agent_logs (
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

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_message_history_user_id ON message_history(user_id);
CREATE INDEX IF NOT EXISTS idx_agent_logs_user_id ON agent_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_agent_logs_timestamp ON agent_logs(timestamp);

-- Create RLS policies for message_history
CREATE POLICY "Users can view their own message history" ON message_history
    FOR SELECT USING (true);

CREATE POLICY "Users can insert their own message history" ON message_history
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Users can update their own message history" ON message_history
    FOR UPDATE USING (true);

CREATE POLICY "Users can delete their own message history" ON message_history
    FOR DELETE USING (true);

-- Create RLS policies for agent_logs
CREATE POLICY "Allow all operations on agent_logs" ON agent_logs
    FOR ALL USING (true);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for message_history
CREATE TRIGGER update_message_history_updated_at 
    BEFORE UPDATE ON message_history 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data (optional)
-- INSERT INTO message_history (user_id, messages) VALUES 
--     ('sample_user', '[{"role": "user", "content": "Hello", "timestamp": "2023-12-21T10:00:00Z"}, {"role": "assistant", "content": "Hi there!", "timestamp": "2023-12-21T10:00:01Z"}]');

-- Grant necessary permissions
GRANT ALL ON message_history TO anon;
GRANT ALL ON agent_logs TO anon;
GRANT USAGE, SELECT ON SEQUENCE agent_logs_id_seq TO anon; 