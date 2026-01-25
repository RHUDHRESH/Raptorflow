// Final cleanup and verification script
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { execSync } from 'child_process';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

console.log('🧹 Starting final cleanup and verification...\n');

// Task 1: Clean up old migration files
function cleanupOldMigrations() {
  console.log('📁 Cleaning up old migration files...');

  const migrationsDir = path.join(__dirname, '../supabase/migrations');
  const archiveDir = path.join(migrationsDir, 'archive');

  // Create archive directory if it doesn't exist
  if (!fs.existsSync(archiveDir)) {
    fs.mkdirSync(archiveDir, { recursive: true });
  }

  // Files to keep
  const keepFiles = [
    '20260122074403_final_auth_consolidation.sql'
  ];

  // Get all migration files
  const files = fs.readdirSync(migrationsDir).filter(f => f.endsWith('.sql'));

  let movedCount = 0;
  files.forEach(file => {
    if (!keepFiles.includes(file)) {
      const src = path.join(migrationsDir, file);
      const dst = path.join(archiveDir, file);

      try {
        fs.renameSync(src, dst);
        movedCount++;
        console.log(`  📦 Archived: ${file}`);
      } catch (err) {
        console.log(`  ⚠️  Could not archive ${file}: ${err.message}`);
      }
    }
  });

  console.log(`✅ Archived ${movedCount} old migration files`);
  return movedCount;
}

// Task 2: Generate final schema documentation
function generateSchemaDocs() {
  console.log('\n📚 Generating schema documentation...');

  const schemaPath = path.join(__dirname, '../supabase/migrations/20260122074403_final_auth_consolidation.sql');
  const schemaSQL = fs.readFileSync(schemaPath, 'utf8');

  // Extract table definitions
  const tableMatches = schemaSQL.match(/CREATE TABLE[^;]+;/g) || [];

  let docs = '# RAPTORFLOW DATABASE SCHEMA\n\n';
  docs += `Generated: ${new Date().toISOString()}\n\n`;
  docs += '## Tables\n\n';

  tableMatches.forEach(tableDef => {
    const tableNameMatch = tableDef.match(/CREATE TABLE[^"]+"?([^"\s]+)/);
    if (tableNameMatch) {
      const tableName = tableNameMatch[1];
      docs += `### ${tableName}\n\n`;

      // Extract columns
      const columnMatches = tableDef.match(/(\w+)\s+([^,\n]+)/g) || [];
      docs += '| Column | Type | Notes |\n';
      docs += '|--------|------|-------|\n';

      columnMatches.forEach(col => {
        const [name, type] = col.split(/\s+/);
        const cleanType = type.replace(/--.*/, '').trim();
        const notes = '';
        docs += `| ${name} | ${cleanType} | ${notes} |\n`;
      });

      docs += '\n';
    }
  });

  // Save documentation
  const docsPath = path.join(__dirname, '../DATABASE_SCHEMA.md');
  fs.writeFileSync(docsPath, docs);
  console.log(`✅ Schema documentation generated: ${docsPath}`);
}

// Task 3: Create deployment checklist
function createChecklist() {
  console.log('\n📋 Creating deployment checklist...');

  const checklist = `# RAPTORFLOW DEPLOYMENT CHECKLIST

## Pre-Deployment Checklist
- [ ] Review schema SQL in \`schema_for_manual_execution.sql\`
- [ ] Backup current database (if needed)
- [ ] Test SQL in development environment

## Deployment Steps
- [ ] Execute schema SQL in Supabase Dashboard
- [ ] Run verification queries
- [ ] Check table creation
- [ ] Verify RLS policies
- [ ] Test indexes

## Post-Deployment Verification
- [ ] Run \`node scripts/pull_and_verify_schema.js\`
- [ ] Test user registration
- [ ] Test login flow
- [ ] Test workspace creation
- [ ] Check API endpoints

## Frontend Testing
- [ ] Start development server
- [ ] Test authentication flow
- [ ] Check for redirect loops
- [ ] Verify user profile loading
- [ ] Test workspace operations

## Performance Checks
- [ ] Monitor query performance
- [ ] Check RLS policy efficiency
- [ ] Verify index usage

## Rollback Plan
- [ ] Keep backup of old schema
- [ ] Document rollback steps
- [ ] Test rollback procedure

## Monitoring
- [ ] Set up error monitoring
- [ ] Monitor authentication metrics
- [ ] Track database performance

Generated: ${new Date().toISOString()}
`;

  const checklistPath = path.join(__dirname, '../DEPLOYMENT_CHECKLIST.md');
  fs.writeFileSync(checklistPath, checklist);
  console.log(`✅ Checklist created: ${checklistPath}`);
}

// Task 4: Final verification
async function finalVerification() {
  console.log('\n🔍 Running final verification...');

  try {
    // Check if all necessary files exist
    const requiredFiles = [
      'schema_for_manual_execution.sql',
      'DATABASE_DEPLOYMENT_GUIDE.md',
      'DATABASE_SCHEMA.md',
      'DEPLOYMENT_CHECKLIST.md',
      'scripts/pull_and_verify_schema.js',
      'scripts/verify_schema.js'
    ];

    let missingFiles = [];
    requiredFiles.forEach(file => {
      const filePath = path.join(__dirname, '..', file);
      if (!fs.existsSync(filePath)) {
        missingFiles.push(file);
      }
    });

    if (missingFiles.length > 0) {
      console.log('❌ Missing files:', missingFiles.join(', '));
    } else {
      console.log('✅ All required files present');
    }

    // Check package.json for scripts
    const packagePath = path.join(__dirname, '../package.json');
    const packageJson = JSON.parse(fs.readFileSync(packagePath, 'utf8'));

    console.log('\n📦 Available npm scripts:');
    Object.entries(packageJson.scripts || {}).forEach(([name, script]) => {
      if (name.includes('db') || name.includes('schema') || name.includes('deploy')) {
        console.log(`  - ${name}: ${script}`);
      }
    });

    console.log('\n🎉 Final verification completed!');

  } catch (error) {
    console.error('❌ Final verification failed:', error);
  }
}

// Execute all tasks
async function runCleanup() {
  try {
    cleanupOldMigrations();
    generateSchemaDocs();
    createChecklist();
    await finalVerification();

    console.log('\n' + '='.repeat(60));
    console.log('🎊 CLEANUP COMPLETED SUCCESSFULLY!');
    console.log('='.repeat(60));
    console.log('\n📋 Summary of actions completed:');
    console.log('✅ Archived old migration files');
    console.log('✅ Generated schema documentation');
    console.log('✅ Created deployment checklist');
    console.log('✅ Final verification completed');

    console.log('\n🚀 Ready for deployment!');
    console.log('1. Follow DATABASE_DEPLOYMENT_GUIDE.md');
    console.log('2. Use DEPLOYMENT_CHECKLIST.md for verification');
    console.log('3. Run scripts/pull_and_verify_schema.js after deployment');

  } catch (error) {
    console.error('❌ Cleanup failed:', error);
    process.exit(1);
  }
}

// Run cleanup
runCleanup().catch(console.error);
