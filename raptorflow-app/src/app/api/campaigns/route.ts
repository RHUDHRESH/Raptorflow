import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseKey =
  process.env.SUPABASE_SERVICE_ROLE_KEY ||
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
const supabase =
  supabaseUrl && supabaseKey ? createClient(supabaseUrl, supabaseKey) : null;

const supabaseUnavailable = () =>
  NextResponse.json(
    { error: 'Supabase not configured for campaigns API.' },
    { status: 503 }
  );

export async function GET(req: NextRequest) {
  try {
    if (!supabase) {
      return supabaseUnavailable();
    }
    const { data, error } = await supabase
      .from('campaigns')
      .select('*')
      .neq('status', 'archived');

    if (error) {
      throw error;
    }
    return NextResponse.json(data || []);
  } catch (e) {
    console.error('Supabase fetch error', e);
    return NextResponse.json(
      { error: 'Failed to fetch campaigns.' },
      { status: 500 }
    );
  }
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();

    if (!supabase) {
      return supabaseUnavailable();
    }
    const { data, error } = await supabase
      .from('campaigns')
      .insert({
        ...body,
        tenant_id: '00000000-0000-0000-0000-000000000000', // Default tenant
      })
      .select()
      .single();

    if (error) throw error;
    return NextResponse.json(data);
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
