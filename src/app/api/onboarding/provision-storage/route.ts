import { createServerSupabaseClient } from '@/lib/auth-server'
import { NextResponse } from 'next/server'
import { createClient } from '@supabase/supabase-js'

// Initialize Supabase client
const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
)

export async function POST(request: Request) {
  try {

    // Get current user
    const { data: { session } } = await supabase.auth.getSession()

    if (!session) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    // Get user and workspace
    const { data: user } = await supabase
      .from('users')
      .select('id, onboarding_status')
      .eq('auth_user_id', session.user.id)
      .single()

    if (!user || user.onboarding_status !== 'pending_storage') {
      return NextResponse.json(
        { error: 'Invalid onboarding state' },
        { status: 400 }
      )
    }

    const { data: workspace } = await supabase
      .from('workspaces')
      .select('id, slug')
      .eq('user_id', user.id)
      .single()

    if (!workspace) {
      return NextResponse.json(
        { error: 'Workspace not found' },
        { status: 404 }
      )
    }

    // Create folder structure in Supabase Storage
    // We use workspace-specific buckets with standardized paths
    const { generateWorkspacePath } = await import('../../../../lib/storage-paths')
    
    // Create placeholder files to establish folder structure
    const folders = [
      { category: 'uploads', filename: '.keep' },
      { category: 'exports', filename: '.keep' },
      { category: 'temp', filename: '.keep' },
      { category: 'backups', filename: '.keep' },
      { category: 'assets', filename: '.keep' },
    ]

    try {
      for (const folder of folders) {
        const storagePath = generateWorkspacePath(workspace.slug, folder.category, folder.filename)
        const bucket = folder.category === 'assets' ? 'workspace-assets' : `workspace-${folder.category}`
        
        // Upload empty file to create folder structure
        const { error } = await supabase.storage
          .from(bucket)
          .upload(storagePath, new Uint8Array(), {
            contentType: 'text/plain',
            metadata: {
              folder_structure: true,
              category: folder.category,
              workspace_slug: workspace.slug
            }
          })
        
        if (error) {
          console.warn(`Failed to create folder ${folder.category}:`, error)
        }
      }
    } catch (supabaseError) {
      console.error('Supabase folder creation error:', supabaseError)
      return NextResponse.json(
        { error: 'Failed to create storage folders' },
        { status: 500 }
      )
    }

    // Update workspace with storage info
    const { error: workspaceError } = await supabase
      .from('workspaces')
      .update({
        supabase_bucket: 'workspace-uploads',
        supabase_folder_path: `workspace/${workspace.slug}/`,
        status: 'active'
      })
      .eq('id', workspace.id)

    if (workspaceError) {
      console.error('Workspace update error:', workspaceError)
      return NextResponse.json(
        { error: 'Failed to update workspace' },
        { status: 500 }
      )
    }

    // Update user onboarding status
    await supabase
      .from('users')
      .update({ onboarding_status: 'pending_plan_selection' })
      .eq('id', user.id)

    // Log the action
    await supabase.from('audit_logs').insert({
      actor_id: user.id,
      action: 'storage_provisioned',
      action_category: 'onboarding',
      description: `Storage provisioned for workspace: ${workspace.slug}`,
      target_type: 'workspace',
      target_id: workspace.id,
      ip_address: request.headers.get('x-forwarded-for') || 'unknown',
      user_agent: request.headers.get('user-agent') || 'unknown',
    })

    return NextResponse.json({
      success: true,
      storage: {
        provider: 'supabase',
        workspace_slug: workspace.slug,
        buckets: ['workspace-uploads', 'workspace-exports', 'workspace-backups', 'workspace-assets', 'workspace-temp'],
        capacity: '5 GB',
      }
    })

  } catch (err) {
    console.error('Provision storage error:', err)
    return NextResponse.json(
      { error: 'Failed to provision storage' },
      { status: 500 }
    )
  }
}
