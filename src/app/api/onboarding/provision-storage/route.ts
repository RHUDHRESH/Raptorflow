import { createServerSupabaseClient } from '@/lib/auth-server'
import { NextResponse } from 'next/server'
import { Storage } from '@google-cloud/storage'

// Initialize Google Cloud Storage
const storage = new Storage({
  projectId: process.env.GCP_PROJECT_ID,
  credentials: JSON.parse(process.env.GCP_SERVICE_ACCOUNT_KEY || '{}'),
})

const MAIN_BUCKET = process.env.GCS_MAIN_BUCKET!

export async function POST(request: Request) {
  try {
    const supabase = createServerSupabaseClient()

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

    // Create folder structure in GCS
    // We use a shared bucket with user-specific folders
    const bucket = storage.bucket(MAIN_BUCKET)
    const userFolder = `workspaces/${workspace.slug}/`

    // Create placeholder files to establish folder structure
    const folders = [
      `${userFolder}uploads/`,
      `${userFolder}exports/`,
      `${userFolder}temp/`,
      `${userFolder}backups/`,
      `${userFolder}assets/`,
    ]

    try {
      for (const folder of folders) {
        const file = bucket.file(`${folder}.keep`)
        await file.save('', {
          metadata: {
            contentType: 'text/plain',
            cacheControl: 'no-cache',
          },
        })
      }
    } catch (gcsError) {
      console.error('GCS folder creation error:', gcsError)
      return NextResponse.json(
        { error: 'Failed to create storage folders' },
        { status: 500 }
      )
    }

    // Set up IAM permissions for the user folder
    // Note: In production, you might want to use signed URLs or Cloud IAM
    // For now, we'll rely on application-level access control

    // Update workspace with storage info
    const { error: workspaceError } = await supabase
      .from('workspaces')
      .update({
        gcs_bucket_name: MAIN_BUCKET,
        gcs_folder_path: userFolder,
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
        bucket: MAIN_BUCKET,
        folder: userFolder,
        region: 'asia-south1', // Mumbai
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
