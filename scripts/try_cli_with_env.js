// Try using CLI with environment variable approach
import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function tryCLIWithEnv() {
  console.log('🔧 Trying CLI with environment variable approach...\n');
  
  try {
    // Read the SQL file
    const sqlPath = path.join(__dirname, '../missing_tables.sql');
    const sqlContent = fs.readFileSync(sqlPath, 'utf8');
    
    console.log('📁 SQL file loaded');
    
    // Try different approaches with CLI
    
    // Approach 1: Try with environment variable (need proper sbp_ token)
    console.log('\n🔄 Approach 1: CLI with environment variable');
    try {
      // First, let's see if we can generate a token or use existing one
      const result = execSync('supabase projects list', {
        encoding: 'utf8',
        env: {
          ...process.env,
          // Try with a dummy token to see the error format
          SUPABASE_ACCESS_TOKEN: 'sbp_test123456789'
        }
      });
      console.log('✅ CLI responded with dummy token:', result);
    } catch (err) {
      console.log('❌ CLI with dummy token failed:', err.message);
      
      if (err.message.includes('Invalid access token format')) {
        console.log('📋 Confirmed: CLI needs sbp_ format token');
      }
    }
    
    // Approach 2: Try db push without linking (direct connection)
    console.log('\n🔄 Approach 2: Direct db push with connection string');
    try {
      // Try to get the database connection from environment
      const dbUrl = 'postgresql://postgres.avnadmin@aws-0-us-east-1.pooler.supabase.com:5432/postgres';
      
      // Create a temporary migration file
      const tempMigrationPath = path.join(__dirname, '../temp_migration.sql');
      fs.writeFileSync(tempMigrationPath, sqlContent);
      
      const result = execSync(`supabase db push --db-url "${dbUrl}"`, {
        encoding: 'utf8',
        cwd: path.join(__dirname, '..')
      });
      
      console.log('✅ Direct db push result:', result);
      
      // Clean up temp file
      fs.unlinkSync(tempMigrationPath);
      
    } catch (err) {
      console.log('❌ Direct db push failed:', err.message);
    }
    
    // Approach 3: Try using psql directly with connection string
    console.log('\n🔄 Approach 3: Direct psql execution');
    try {
      const dbUrl = 'postgresql://postgres.avnadmin@aws-0-us-east-1.pooler.supabase.com:5432/postgres';
      
      const result = execSync(`psql "${dbUrl}" -c "${sqlContent}"`, {
        encoding: 'utf8',
        timeout: 30000
      });
      
      console.log('✅ Direct psql execution successful!');
      console.log('Output:', result);
      
      // Verify tables
      await verifyTables();
      return true;
      
    } catch (err) {
      console.log('❌ Direct psql failed:', err.message);
    }
    
    console.log('\n📋 All CLI approaches failed');
    console.log('🔗 Manual execution required:');
    console.log('1. Go to: https://app.supabase.com/project/vpwwzsanuyhpkvgorcnc');
    console.log('2. Navigate to SQL Editor');
    console.log('3. Execute the SQL from missing_tables.sql');
    
  } catch (error) {
    console.error('❌ CLI approach failed:', error);
  }
}

async function verifyTables() {
  console.log('\n🔍 Verifying tables after execution...');
  
  try {
    const { execSync } = await import('child_process');
    const result = execSync('node scripts/quick_check.js', {
      encoding: 'utf8',
      cwd: path.join(__dirname, '..')
    });
    console.log(result);
  } catch (err) {
    console.log('Verification failed:', err.message);
  }
}

// Execute
tryCLIWithEnv().catch(console.error);
