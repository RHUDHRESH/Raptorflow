-- Add retention_date column to onboarding_files
ALTER TABLE onboarding_files
ADD COLUMN retention_date TIMESTAMPTZ;
