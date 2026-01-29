import { createServerSupabaseClient } from '@/lib/auth-server'
import { NextResponse } from 'next/server'

function generateSlug(name: string): string {
  return name
    .toLowerCase()
    .replace(/[^a-z0-9 -]/g, '') // Remove special characters
    .replace(/\s+/g, '-') // Replace spaces with hyphens
    .replace(/-+/g, '-') // Replace multiple hyphens with single
    .trim()
}

export async function POST(request: Request) {
  try {
    const { name } = await request.json()

    if (!name || name.length < 3) {
      return NextResponse.json(
        { error: 'Workspace name must be at least 3 characters' },
        { status: 400 }
      )
    }

    if (name.length > 50) {
      return NextResponse.json(
        { error: 'Workspace name must be 50 characters or less' },
        { status: 400 }
      )
    }

    const supabase = await createServerSupabaseClient()

    // Get current user
    const { data: { session } } = await supabase.auth.getSession()

    if (!session) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    // Get user record
    const { data: user, error: userError } = await supabase
      .from('users')
      .select('id, onboarding_status')
      .eq('auth_user_id', session.user.id)
      .single()

    if (userError || !user) {
      return NextResponse.json({ error: 'User not found' }, { status: 404 })
    }

    // Verify user is at correct onboarding step
    if (user.onboarding_status !== 'pending_workspace') {
      return NextResponse.json(
        { error: 'Invalid onboarding state' },
        { status: 400 }
      )
    }

    // Check if workspace already exists
    const { data: existingWorkspace } = await supabase
      .from('workspaces')
      .select('id')
      .eq('user_id', user.id)
      .single()

    if (existingWorkspace) {
      // Workspace already exists, update status and redirect
      await supabase
        .from('users')
        .update({ onboarding_status: 'pending_storage' })
        .eq('id', user.id)

      return NextResponse.json({
        message: 'Workspace already exists',
        workspace: existingWorkspace
      })
    }

    // Generate unique slug
    const baseSlug = generateSlug(name)
    let slug = baseSlug
    let counter = 1

    while (true) {
      const { data: existing } = await supabase
        .from('workspaces')
        .select('id')
        .eq('slug', slug)
        .single()

      if (!existing) break
      slug = `${baseSlug}-${counter}`
      counter++

      // Prevent infinite loop
      if (counter > 1000) {
        return NextResponse.json(
          { error: 'Unable to generate unique workspace name' },
          { status: 500 }
        )
      }
    }

    // Create workspace
    const { data: workspace, error: workspaceError } = await supabase
      .from('workspaces')
      .insert({
        user_id: user.id,
        name,
        slug,
        status: 'provisioning'
      })
      .select()
      .single()

    if (workspaceError) {
      console.error('Workspace creation error:', workspaceError)
      return NextResponse.json(
        { error: 'Failed to create workspace' },
        { status: 500 }
      )
    }

    // Update user onboarding status
    const { error: updateError } = await supabase
      .from('users')
      .update({ onboarding_status: 'pending_storage' })
      .eq('id', user.id)

    if (updateError) {
      console.error('User update error:', updateError)
      // Don't fail - workspace was created
    }

    // Log the action
    await supabase.from('audit_logs').insert({
      actor_id: user.id,
      action: 'workspace_created',
      action_category: 'onboarding',
      description: `Created workspace: ${name}`,
      target_type: 'workspace',
      target_id: workspace.id,
      ip_address: request.headers.get('x-forwarded-for') || 'unknown',
      user_agent: request.headers.get('user-agent') || 'unknown',
    })

    return NextResponse.json({
      message: 'Workspace created successfully',
      workspace
    })

  } catch (err) {
    console.error('Create workspace error:', err)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
