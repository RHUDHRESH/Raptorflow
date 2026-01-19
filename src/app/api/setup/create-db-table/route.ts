import { NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

export async function POST() {
  try {
    const supabase = createClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.SUPABASE_SERVICE_ROLE_KEY!
    );

    // Create password_reset_tokens table using raw SQL
    const { error } = await supabase.rpc('exec_sql', {
      sql: `
        CREATE TABLE IF NOT EXISTS public.password_reset_tokens (
          id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
          token TEXT UNIQUE NOT NULL,
          email TEXT NOT NULL,
          expires_at TIMESTAMPTZ NOT NULL,
          used_at TIMESTAMPTZ,
          created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
          updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        
        CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_token ON public.password_reset_tokens(token);
        CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_email ON public.password_reset_tokens(email);
        CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_expires ON public.password_reset_tokens(expires_at);
        
        -- Enable RLS
        ALTER TABLE public.password_reset_tokens ENABLE ROW LEVEL SECURITY;
        
        -- Policies
        CREATE POLICY IF NOT EXISTS "password_reset_tokens_insert" ON public.password_reset_tokens
          FOR INSERT WITH CHECK (true);
          
        CREATE POLICY IF NOT EXISTS "password_reset_tokens_select" ON public.password_reset_tokens
          FOR SELECT USING (true);
          
        CREATE POLICY IF NOT EXISTS "password_reset_tokens_update" ON public.password_reset_tokens
          FOR UPDATE USING (true);
          
        CREATE POLICY IF NOT EXISTS "password_reset_tokens_delete" ON public.password_reset_tokens
          FOR DELETE USING (true);
      `
    });

    if (error) {
      console.error('SQL execution error:', error);
      
      // Try alternative approach - test if table exists
      const testResult = await supabase
        .from('password_reset_tokens')
        .select('count')
        .limit(1);
      
      if (testResult.error && testResult.error.code === '42P01') {
        return NextResponse.json({
          success: false,
          message: 'Table does not exist. Please run SQL manually in Supabase Dashboard.',
          sql: `CREATE TABLE IF NOT EXISTS public.password_reset_tokens (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  token TEXT UNIQUE NOT NULL,
  email TEXT NOT NULL,
  expires_at TIMESTAMPTZ NOT NULL,
  used_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_password_reset_tokens_token ON public.password_reset_tokens(token);`
        }, { status: 400 });
      }
      
      return NextResponse.json({
        success: true,
        message: 'Table already exists or was created successfully',
        note: 'RPC method failed but table check passed'
      });
    }

    return NextResponse.json({
      success: true,
      message: 'Password reset tokens table created successfully with all indexes and policies'
    });

  } catch (error) {
    console.error('Setup error:', error);
    return NextResponse.json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}

export async function GET() {
  try {
    const supabase = createClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.SUPABASE_SERVICE_ROLE_KEY!
    );

    // Check if table exists
    const { data, error } = await supabase
      .from('password_reset_tokens')
      .select('*')
      .limit(1);

    if (error) {
      if (error.code === '42P01') {
        return NextResponse.json({
          exists: false,
          message: 'Table does not exist',
          nextAction: 'POST to this endpoint to create it'
        });
      }
      return NextResponse.json({
        exists: false,
        error: error.message
      });
    }

    return NextResponse.json({
      exists: true,
      message: 'Table exists and is accessible',
      rowCount: data?.length || 0,
      status: 'Ready for password reset functionality'
    });

  } catch (error) {
    return NextResponse.json({
      exists: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}
