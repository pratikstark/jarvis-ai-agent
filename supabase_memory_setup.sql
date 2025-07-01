-- Supabase Memory Setup for Jarvis AI Agent
-- Run this in your Supabase SQL editor to create the memory tables

-- Knowledge Base Table
CREATE TABLE IF NOT EXISTS knowledge_base (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    category TEXT NOT NULL DEFAULT 'general',
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_knowledge_base_user_id ON knowledge_base(user_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_base_category ON knowledge_base(category);
CREATE INDEX IF NOT EXISTS idx_knowledge_base_created_at ON knowledge_base(created_at DESC);

-- Conversation Memories Table
CREATE TABLE IF NOT EXISTS conversation_memories (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    conversation_id TEXT NOT NULL,
    summary TEXT NOT NULL,
    key_points TEXT[] NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_conversation_memories_user_id ON conversation_memories(user_id);
CREATE INDEX IF NOT EXISTS idx_conversation_memories_created_at ON conversation_memories(created_at DESC);

-- User Preferences Table
CREATE TABLE IF NOT EXISTS user_preferences (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT UNIQUE NOT NULL,
    preferences JSONB DEFAULT '{}',
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences(user_id);

-- Learning Progress Table
CREATE TABLE IF NOT EXISTS learning_progress (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    topic TEXT NOT NULL,
    progress JSONB DEFAULT '{}',
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, topic)
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_learning_progress_user_id ON learning_progress(user_id);
CREATE INDEX IF NOT EXISTS idx_learning_progress_topic ON learning_progress(topic);

-- Enable Row Level Security (RLS)
ALTER TABLE knowledge_base ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversation_memories ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_progress ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
-- Knowledge Base policies
CREATE POLICY "Users can view their own knowledge" ON knowledge_base
    FOR SELECT USING (user_id = current_user);

CREATE POLICY "Users can insert their own knowledge" ON knowledge_base
    FOR INSERT WITH CHECK (user_id = current_user);

CREATE POLICY "Users can update their own knowledge" ON knowledge_base
    FOR UPDATE USING (user_id = current_user);

CREATE POLICY "Users can delete their own knowledge" ON knowledge_base
    FOR DELETE USING (user_id = current_user);

-- Conversation Memories policies
CREATE POLICY "Users can view their own conversation memories" ON conversation_memories
    FOR SELECT USING (user_id = current_user);

CREATE POLICY "Users can insert their own conversation memories" ON conversation_memories
    FOR INSERT WITH CHECK (user_id = current_user);

CREATE POLICY "Users can update their own conversation memories" ON conversation_memories
    FOR UPDATE USING (user_id = current_user);

CREATE POLICY "Users can delete their own conversation memories" ON conversation_memories
    FOR DELETE USING (user_id = current_user);

-- User Preferences policies
CREATE POLICY "Users can view their own preferences" ON user_preferences
    FOR SELECT USING (user_id = current_user);

CREATE POLICY "Users can insert their own preferences" ON user_preferences
    FOR INSERT WITH CHECK (user_id = current_user);

CREATE POLICY "Users can update their own preferences" ON user_preferences
    FOR UPDATE USING (user_id = current_user);

CREATE POLICY "Users can delete their own preferences" ON user_preferences
    FOR DELETE USING (user_id = current_user);

-- Learning Progress policies
CREATE POLICY "Users can view their own learning progress" ON learning_progress
    FOR SELECT USING (user_id = current_user);

CREATE POLICY "Users can insert their own learning progress" ON learning_progress
    FOR INSERT WITH CHECK (user_id = current_user);

CREATE POLICY "Users can update their own learning progress" ON learning_progress
    FOR UPDATE USING (user_id = current_user);

CREATE POLICY "Users can delete their own learning progress" ON learning_progress
    FOR DELETE USING (user_id = current_user);

-- Create functions for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for automatic timestamp updates
CREATE TRIGGER update_knowledge_base_updated_at 
    BEFORE UPDATE ON knowledge_base 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_preferences_updated_at 
    BEFORE UPDATE ON user_preferences 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_learning_progress_updated_at 
    BEFORE UPDATE ON learning_progress 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data for testing (optional)
-- INSERT INTO knowledge_base (user_id, category, content) VALUES 
--     ('test_user', 'personal', 'User prefers dark mode'),
--     ('test_user', 'technical', 'User is learning Python programming'),
--     ('test_user', 'general', 'User likes coffee in the morning');

-- INSERT INTO user_preferences (user_id, preferences) VALUES 
--     ('test_user', '{"theme": "dark", "language": "en", "notifications": true}');

-- INSERT INTO learning_progress (user_id, topic, progress) VALUES 
--     ('test_user', 'python', '{"level": "beginner", "completed_lessons": 5, "current_lesson": "functions"}');

COMMIT; 