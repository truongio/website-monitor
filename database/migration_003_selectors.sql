-- Migration to add selectors support for targeted element monitoring
-- This allows users to monitor specific elements on a page instead of the entire content

-- Add selectors column to page_states table (JSON array of CSS selectors)
ALTER TABLE page_states
ADD COLUMN IF NOT EXISTS selectors JSONB DEFAULT NULL;

-- Add selectors column to subscriptions table
ALTER TABLE subscriptions
ADD COLUMN IF NOT EXISTS selectors JSONB DEFAULT NULL;

-- Add comment to explain the feature
COMMENT ON COLUMN page_states.selectors IS 'JSON array of CSS selectors to monitor specific elements instead of entire page';
COMMENT ON COLUMN subscriptions.selectors IS 'JSON array of CSS selectors to monitor specific elements instead of entire page';
