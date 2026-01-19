import { NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

// Lazy client creation to avoid build-time errors
function getSupabase() {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const key = process.env.NEXT_PUBLIC_SUPABASE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

  if (!url || !key) {
    throw new Error('Missing Supabase configuration');
  }

  return createClient(url, key);
}

export async function POST(request: Request) {
  try {
    const supabase = getSupabase();
    const { user_id, file_path } = await request.json();

    // Get file info from GCS (this would typically be done via backend)
    // For now, we'll simulate getting file size from the path
    const fileName = file_path.split('/').pop() || '';
    const estimatedSize = fileName.includes('pdf') ? 1024 * 1024 : 512 * 1024; // 1MB for PDF, 512KB for others

    // Update user's storage usage
    const { data: profile } = await supabase
      .from('user_profiles')
      .select('storage_used_mb')
      .eq('id', user_id)
      .single();

    if (profile) {
      const newUsage = Math.max(0, profile.storage_used_mb - Math.ceil(estimatedSize / (1024 * 1024)));

      await supabase
        .from('user_profiles')
        .update({ storage_used_mb: newUsage })
        .eq('id', user_id);
    }

    return NextResponse.json({
      success: true,
      size: estimatedSize,
      new_usage: profile ? Math.max(0, profile.storage_used_mb - Math.ceil(estimatedSize / (1024 * 1024))) : 0
    });

  } catch (error: any) {
    console.error('Error deleting file:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Unknown error" },
      { status: 500 }
    );
  }
}
