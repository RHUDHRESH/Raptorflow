// Generate consolidated SQL for manual execution
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

console.log('🚀 Generating consolidated schema SQL...');

// Read the latest migration file
const migrationPath = path.join(__dirname, '../supabase/migrations/20260122074403_final_auth_consolidation.sql');
const migrationSQL = fs.readFileSync(migrationPath, 'utf8');

// Add header
const header = `-- ============================================================================
-- RAPTORFLOW DATABASE SCHEMA - MANUAL EXECUTION SCRIPT
-- Project: vpwwzsanuyhpkvgorcnc
-- Generated: ${new Date().toISOString()}
-- Instructions: Execute this in Supabase Dashboard > SQL Editor
-- ============================================================================

`;

// Add verification queries
const footer = `

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Check if tables exist
SELECT table_name, table_type 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('profiles', 'subscriptions', 'payments', 'email_logs', 'workspaces')
ORDER BY table_name;

-- Check RLS policies
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual 
FROM pg_policies 
WHERE schemaname = 'public' 
ORDER BY tablename, policyname;

-- Check indexes
SELECT indexname, tablename 
FROM pg_indexes 
WHERE schemaname = 'public' 
AND tablename IN ('profiles', 'subscriptions', 'payments', 'email_logs', 'workspaces')
ORDER BY tablename, indexname;

-- Sample data check (optional)
-- SELECT COUNT(*) as profile_count FROM profiles;
-- SELECT COUNT(*) as workspace_count FROM workspaces;

`;

const fullSQL = header + migrationSQL + footer;

// Write to output file
const outputPath = path.join(__dirname, '../schema_for_manual_execution.sql');
fs.writeFileSync(outputPath, fullSQL);

console.log('✅ Schema SQL generated successfully!');
console.log('📁 Output file:', outputPath);
console.log('');
console.log('📋 Next steps:');
console.log('1. Open Supabase Dashboard: https://app.supabase.com/project/vpwwzsanuyhpkvgorcnc');
console.log('2. Go to SQL Editor');
console.log('3. Copy and paste the contents of:', outputPath);
console.log('4. Execute the SQL');
console.log('');
console.log('🔍 After execution, run the verification queries to confirm everything is set up correctly.');
