import { getSupabaseAdmin } from './supabase-factory';
import fs from 'fs';
import path from 'path';

/**
 * Industrial Migration Engine
 * Tracks and executes SQL migrations via Supabase RPC exec_sql
 */
export const migrationEngine = {
  /**
   * Run all pending migrations from supabase/migrations
   */
  async runMigrations() {
    const admin = getSupabaseAdmin();
    const migrationsDir = path.join(process.cwd(), 'supabase/migrations');
    
    // 1. Ensure migrations table exists
    await admin.rpc('exec_sql', { 
      sql: `CREATE TABLE IF NOT EXISTS public._migrations (
        name TEXT PRIMARY KEY,
        applied_at TIMESTAMPTZ DEFAULT NOW()
      );` 
    });

    // 2. Get applied migrations
    const { data: applied } = await admin.from('_migrations').select('name');
    const appliedNames = new Set(applied?.map(m => m.name) || []);

    // 3. Read migration files
    const files = fs.readdirSync(migrationsDir)
      .filter(f => f.endsWith('.sql'))
      .sort();

    const results = [];

    for (const file of files) {
      if (appliedNames.has(file)) continue;

      console.log(`🚀 Applying migration: ${file}...`);
      const sql = fs.readFileSync(path.join(migrationsDir, file), 'utf8');
      
      try {
        await admin.rpc('exec_sql', { sql });
        await admin.from('_migrations').insert({ name: file });
        results.push({ file, status: 'success' });
      } catch (error: any) {
        console.error(`❌ Migration failed: ${file}`, error.message);
        results.push({ file, status: 'failed', error: error.message });
        break; // Stop on failure
      }
    }

    return results;
  }
};
