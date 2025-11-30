-- ============================================================================
-- Migration: Add Care Period (Start/End Dates) to matching_requests table
-- ============================================================================
-- Author: Database Migration
-- Date: 2025-11-29
-- Purpose: Store patient's requested care period when creating matching request
--
-- IMPORTANT: Run each step separately in DBeaver (do NOT run all at once)
-- ============================================================================

-- STEP 1: Add new columns to matching_requests table
-- Run this FIRST
ALTER TABLE matching_requests
ADD COLUMN care_start_date DATE DEFAULT NULL;

-- STEP 1b: Add second column (separate from step 1)
-- Run this SECOND
ALTER TABLE matching_requests
ADD COLUMN care_end_date DATE DEFAULT NULL;

-- STEP 2: Add check constraint to validate date logic
-- Run this THIRD (after both columns are added)
ALTER TABLE matching_requests
ADD CONSTRAINT check_care_dates CHECK (
    care_start_date IS NULL OR
    care_end_date IS NULL OR
    care_start_date < care_end_date
);

-- STEP 3: Create index for efficient date range queries
-- Run this FOURTH
CREATE INDEX idx_matching_requests_care_dates
ON matching_requests(care_start_date, care_end_date)
WHERE is_active = true;

-- ============================================================================
-- VERIFICATION QUERIES (Run these to verify success)
-- ============================================================================

-- Check if columns exist
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'matching_requests'
AND column_name IN ('care_start_date', 'care_end_date')
ORDER BY ordinal_position;

-- Check if constraint exists
SELECT constraint_name
FROM information_schema.table_constraints
WHERE table_name = 'matching_requests'
AND constraint_name = 'check_care_dates';

-- Check if index exists
SELECT indexname
FROM pg_indexes
WHERE tablename = 'matching_requests'
AND indexname = 'idx_matching_requests_care_dates';

-- ============================================================================
-- ROLLBACK script (if needed - run only if you want to undo):
-- ============================================================================
-- DROP INDEX IF EXISTS idx_matching_requests_care_dates;
-- ALTER TABLE matching_requests DROP CONSTRAINT IF EXISTS check_care_dates;
-- ALTER TABLE matching_requests DROP COLUMN IF EXISTS care_end_date;
-- ALTER TABLE matching_requests DROP COLUMN IF EXISTS care_start_date;
-- ============================================================================
