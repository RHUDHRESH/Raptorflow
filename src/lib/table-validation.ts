/**
 * Runtime Supabase Table Validation
 * Checks for required database tables at runtime
 */

import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'

interface TableValidationResult {
  isValid: boolean
  missing: string[]
  existing: string[]
}

/**
 * Required tables for RaptorFlow authentication
 */
const REQUIRED_TABLES = [
  'users',
  'user_subscriptions'
]

/**
 * Check if required Supabase tables exist
 */
export async function validateSupabaseTables(): Promise<TableValidationResult> {
  try {
    const cookieStore = cookies()
    const supabase = createServerClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
      {
        cookies: {
          getAll() {
            return cookieStore.getAll()
          },
          setAll(cookiesToSet: any[]) {
            try {
              cookiesToSet.forEach(({ name, value, options }: any) =>
                cookieStore.set(name, value, options)
              )
            } catch {
              // Ignore cookie errors in validation
            }
          },
        },
      }
    )

    // Check if we can access the database
    const { data: tables, error } = await supabase
      .from('information_schema.tables')
      .select('table_name')
      .eq('table_schema', 'public')
      .eq('table_type', 'BASE TABLE')

    if (error) {
      console.error('Failed to query database tables:', error)
      return {
        isValid: false,
        missing: REQUIRED_TABLES,
        existing: []
      }
    }

    const existingTableNames = tables?.map(t => t.table_name) || []
    const missingTables = REQUIRED_TABLES.filter(table => 
      !existingTableNames.includes(table)
    )

    return {
      isValid: missingTables.length === 0,
      missing: missingTables,
      existing: existingTableNames
    }

  } catch (error) {
    console.error('Error validating Supabase tables:', error)
    return {
      isValid: false,
      missing: REQUIRED_TABLES,
      existing: []
    }
  }
}

/**
 * Validate tables and log results
 */
export async function validateAndLogTables(): Promise<boolean> {
  const validation = await validateSupabaseTables()
  
  if (validation.isValid) {
    console.log('✅ All required Supabase tables exist:', validation.existing.join(', '))
    return true
  } else {
    console.error('❌ Missing required Supabase tables:', validation.missing.join(', '))
    console.error('Existing tables:', validation.existing.join(', '))
    
    // Provide helpful SQL for missing tables
    if (validation.missing.includes('users')) {
      console.error(`
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  auth_user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT NOT NULL,
  full_name TEXT,
  onboarding_status TEXT DEFAULT 'pending',
  default_workspace_id UUID,
  is_active BOOLEAN DEFAULT true,
  is_banned BOOLEAN DEFAULT false,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);`)
    }
    
    if (validation.missing.includes('user_subscriptions')) {
      console.error(`
CREATE TABLE user_subscriptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  plan_id TEXT NOT NULL,
  status TEXT DEFAULT 'inactive',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);`)
    }
    
    return false
  }
}

/**
 * Check if a specific table exists
 */
export async function tableExists(tableName: string): Promise<boolean> {
  const validation = await validateSupabaseTables()
  return validation.existing.includes(tableName)
}

/**
 * Get table schema information
 */
export async function getTableSchema(tableName: string): Promise<any> {
  try {
    const cookieStore = cookies()
    const supabase = createServerClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
      {
        cookies: {
          getAll() {
            return cookieStore.getAll()
          },
          setAll(cookiesToSet: any[]) {
            try {
              cookiesToSet.forEach(({ name, value, options }: any) =>
                cookieStore.set(name, value, options)
              )
            } catch {
              // Ignore cookie errors in validation
            }
          },
        },
      }
    )

    const { data, error } = await supabase
      .from('information_schema.columns')
      .select('column_name, data_type, is_nullable')
      .eq('table_schema', 'public')
      .eq('table_name', tableName)
      .order('ordinal_position')

    if (error) {
      console.error(`Failed to get schema for table ${tableName}:`, error)
      return null
    }

    return data

  } catch (error) {
    console.error(`Error getting schema for table ${tableName}:`, error)
    return null
  }
}
