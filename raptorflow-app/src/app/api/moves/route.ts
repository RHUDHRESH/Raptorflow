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
    { error: 'Supabase not configured for moves API.' },
    { status: 503 }
  );

export async function GET(req: NextRequest) {
  try {
    if (!supabase) {
      return supabaseUnavailable();
    }
    const { data, error } = await supabase.from('moves').select('*');

    if (error) {
      throw error;
    }
    return NextResponse.json(data || []);
  } catch (e) {
    console.error('Supabase fetch error', e);
    return NextResponse.json(
      { error: 'Failed to fetch moves.' },
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
      .from('moves')
      .insert({
        ...body,
      })
      .select()
      .single();

    if (error) throw error;
    return NextResponse.json(data);
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}

export async function PUT(req: NextRequest) {
  try {
    const body = await req.json();
    const { id, ...updates } = body;

    if (!id) return NextResponse.json({ error: 'Missing ID' }, { status: 400 });

    if (!supabase) {
      return supabaseUnavailable();
    }
    const { data, error } = await supabase
      .from('moves')
      .update(updates)
      .eq('id', id)
      .select()
      .single();

    if (error) throw error;
    return NextResponse.json(data);

  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
