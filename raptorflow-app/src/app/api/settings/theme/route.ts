import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

export const dynamic = 'force-dynamic';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
const supabase = supabaseUrl && supabaseKey ? createClient(supabaseUrl, supabaseKey) : null;

// Default theme settings
const DEFAULT_THEME_SETTINGS = {
  theme_mode: 'auto',
  accent_color: '#3b82f6',
  design_tokens: {
    // Default design tokens for advanced customization
    borderRadius: {
      sm: '0.125rem',
      md: '0.375rem',
      lg: '0.5rem',
      xl: '0.75rem'
    },
    fontFamily: {
      sans: ['Inter', 'system-ui', 'sans-serif'],
      mono: ['JetBrains Mono', 'Consolas', 'monospace']
    },
    spacing: {
      xs: '0.25rem',
      sm: '0.5rem',
      md: '1rem',
      lg: '1.5rem',
      xl: '2rem'
    }
  }
};

export async function GET(req: NextRequest) {
  try {
    // Get workspace from query params or headers
    const workspaceId = req.headers.get('x-workspace-id') ||
                       req.nextUrl.searchParams.get('workspace_id');

    if (!workspaceId) {
      return NextResponse.json(
        { error: 'Workspace ID is required' },
        { status: 400 }
      );
    }

    if (!supabase) {
      // Fallback to defaults if no Supabase connection
      return NextResponse.json({
        ...DEFAULT_THEME_SETTINGS,
        workspace_id: workspaceId,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      });
    }

    // Fetch workspace settings
    const { data, error } = await supabase
      .from('workspace_settings')
      .select('*')
      .eq('workspace_id', workspaceId)
      .single();

    if (error && error.code !== 'PGRST116') { // PGRST116 = no rows found
      console.error('Supabase fetch error:', error);
      return NextResponse.json(
        { error: 'Failed to fetch workspace settings' },
        { status: 500 }
      );
    }

    // If no settings exist, return defaults
    if (!data) {
      const defaultSettings = {
        ...DEFAULT_THEME_SETTINGS,
        workspace_id: workspaceId,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };

      return NextResponse.json(defaultSettings);
    }

    // Merge saved settings with defaults (for any missing fields)
    const mergedSettings = {
      theme_mode: data.theme_mode || DEFAULT_THEME_SETTINGS.theme_mode,
      accent_color: data.accent_color || DEFAULT_THEME_SETTINGS.accent_color,
      design_tokens: {
        ...DEFAULT_THEME_SETTINGS.design_tokens,
        ...(data.design_tokens || {})
      },
      workspace_id: data.workspace_id,
      created_at: data.created_at,
      updated_at: data.updated_at
    };

    return NextResponse.json(mergedSettings);

  } catch (error) {
    console.error('Theme settings GET error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function PUT(req: NextRequest) {
  try {
    // Get workspace from query params or headers
    const workspaceId = req.headers.get('x-workspace-id') ||
                       req.nextUrl.searchParams.get('workspace_id');

    if (!workspaceId) {
      return NextResponse.json(
        { error: 'Workspace ID is required' },
        { status: 400 }
      );
    }

    // Parse request body
    const body = await req.json();

    // Validate theme_mode
    const validThemeModes = ['light', 'dark', 'auto'];
    if (body.theme_mode && !validThemeModes.includes(body.theme_mode)) {
      return NextResponse.json(
        { error: 'Invalid theme_mode. Must be one of: light, dark, auto' },
        { status: 400 }
      );
    }

    // Validate accent_color (hex color format)
    if (body.accent_color && !/^#[0-9A-Fa-f]{6}$/.test(body.accent_color)) {
      return NextResponse.json(
        { error: 'Invalid accent_color. Must be a valid hex color (e.g., #3b82f6)' },
        { status: 400 }
      );
    }

    // Validate design_tokens (must be object if provided)
    if (body.design_tokens && (typeof body.design_tokens !== 'object' || Array.isArray(body.design_tokens))) {
      return NextResponse.json(
        { error: 'Invalid design_tokens. Must be a valid JSON object' },
        { status: 400 }
      );
    }

    if (!supabase) {
      // Fallback response if no Supabase connection
      return NextResponse.json(
        { error: 'Database connection not available' },
        { status: 503 }
      );
    }

    // Prepare update data
    const updateData: any = {
      updated_at: new Date().toISOString()
    };

    if (body.theme_mode !== undefined) {
      updateData.theme_mode = body.theme_mode;
    }

    if (body.accent_color !== undefined) {
      updateData.accent_color = body.accent_color;
    }

    if (body.design_tokens !== undefined) {
      updateData.design_tokens = body.design_tokens;
    }

    // Check if settings exist for this workspace
    const { data: existingSettings, error: fetchError } = await supabase
      .from('workspace_settings')
      .select('id')
      .eq('workspace_id', workspaceId)
      .single();

    if (fetchError && fetchError.code !== 'PGRST116') {
      console.error('Supabase fetch error:', fetchError);
      return NextResponse.json(
        { error: 'Failed to check existing settings' },
        { status: 500 }
      );
    }

    let result;

    if (existingSettings) {
      // Update existing settings
      const { data, error } = await supabase
        .from('workspace_settings')
        .update(updateData)
        .eq('workspace_id', workspaceId)
        .select()
        .single();

      if (error) {
        console.error('Supabase update error:', error);
        return NextResponse.json(
          { error: 'Failed to update workspace settings' },
          { status: 500 }
        );
      }

      result = data;
    } else {
      // Insert new settings
      const newSettings = {
        workspace_id: workspaceId,
        theme_mode: body.theme_mode || DEFAULT_THEME_SETTINGS.theme_mode,
        accent_color: body.accent_color || DEFAULT_THEME_SETTINGS.accent_color,
        design_tokens: body.design_tokens || DEFAULT_THEME_SETTINGS.design_tokens,
        ...updateData
      };

      const { data, error } = await supabase
        .from('workspace_settings')
        .insert(newSettings)
        .select()
        .single();

      if (error) {
        console.error('Supabase insert error:', error);
        return NextResponse.json(
          { error: 'Failed to create workspace settings' },
          { status: 500 }
        );
      }

      result = data;
    }

    // Return the updated/created settings
    return NextResponse.json({
      message: existingSettings ? 'Settings updated successfully' : 'Settings created successfully',
      settings: result
    }, { status: existingSettings ? 200 : 201 });

  } catch (error) {
    console.error('Theme settings PUT error:', error);

    if (error instanceof SyntaxError) {
      return NextResponse.json(
        { error: 'Invalid JSON in request body' },
        { status: 400 }
      );
    }

    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
