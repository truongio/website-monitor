-- Migration 002: Add Forum Thread Monitoring Support
-- This migration extends the page_states table to support forum thread monitoring

-- Add new columns to page_states table
ALTER TABLE page_states
ADD COLUMN IF NOT EXISTS monitoring_type TEXT DEFAULT 'page' CHECK (monitoring_type IN ('page', 'forum_thread'));

ALTER TABLE page_states
ADD COLUMN IF NOT EXISTS last_post_id TEXT;

ALTER TABLE page_states
ADD COLUMN IF NOT EXISTS last_post_number INTEGER;

ALTER TABLE page_states
ADD COLUMN IF NOT EXISTS metadata JSONB;

-- Create index for efficient queries by monitoring type
CREATE INDEX IF NOT EXISTS idx_page_states_monitoring_type ON page_states(monitoring_type);

-- Add comment to document the schema
COMMENT ON COLUMN page_states.monitoring_type IS 'Type of monitoring: page (regular hash-based) or forum_thread (post-level tracking)';
COMMENT ON COLUMN page_states.last_post_id IS 'For forum threads: ID of the last seen post (e.g., post-3164190)';
COMMENT ON COLUMN page_states.last_post_number IS 'For forum threads: Sequential number of the last seen post';
COMMENT ON COLUMN page_states.metadata IS 'Flexible JSON storage for additional tracking data (thread_id, page_number, etc.)';
