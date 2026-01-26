import { createRouteHandlerClient } from '@supabase/auth-helpers-nextjs'
import { cookies } from 'next/headers'
import { NextResponse } from 'next/server'
import { createClient } from '@supabase/supabase-js'
import crypto from 'crypto'

export async function POST(request: Request) {
  try {
    const { format = 'json' } = await request.json()

    const supabase = createRouteHandlerClient({ cookies })

    // Get current user
    const { data: { session } } = await supabase.auth.getSession()

    if (!session) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    // Get user record
    const { data: user } = await supabase
      .from('users')
      .select('id, email')
      .eq('auth_user_id', session.user.id)
      .single()

    if (!user) {
      return NextResponse.json({ error: 'User not found' }, { status: 404 })
    }

    // Check if there's already a pending export request
    const { data: existingRequest } = await supabase
      .from('data_export_requests')
      .select('*')
      .eq('user_id', user.id)
      .eq('status', 'pending')
      .single()

    if (existingRequest) {
      return NextResponse.json({
        error: 'Export already in progress',
        requestId: existingRequest.id
      }, { status: 409 })
    }

    // Create export request
    const { data: exportRequest, error: requestError } = await supabase
      .from('data_export_requests')
      .insert({
        user_id: user.id,
        format,
        status: 'pending',
        expires_at: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000) // 7 days
      })
      .select()
      .single()

    if (requestError) throw requestError

    // Start async export process
    processDataExport(exportRequest.id, user.id, format)

    // Log the action
    await supabase
      .from('audit_logs')
      .insert({
        actor_id: user.id,
        action: 'data_export_requested',
        action_category: 'security',
        description: `Data export requested in ${format} format`,
        ip_address: request.headers.get('x-forwarded-for') || 'unknown',
        user_agent: request.headers.get('user-agent') || 'unknown'
      })

    return NextResponse.json({
      requestId: exportRequest.id,
      status: 'pending',
      message: 'Your data export is being processed. You will receive an email when it\'s ready.'
    })

  } catch (error) {
    console.error('Data export error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

async function processDataExport(requestId: string, userId: string, format: string) {
  const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!
  )

  try {
    // Fetch all user data
    const userData = await fetchAllUserData(supabase, userId)

    // Create export file
    let exportUrl: string
    let exportData: any

    if (format === 'json') {
      exportData = JSON.stringify(userData, null, 2)
      exportUrl = await uploadExportToStorage(
        supabase,
        userId,
        requestId,
        exportData,
        'application/json'
      )
    } else if (format === 'csv') {
      exportData = convertToCSV(userData)
      exportUrl = await uploadExportToStorage(
        supabase,
        userId,
        requestId,
        exportData,
        'text/csv'
      )
    } else {
      throw new Error('Unsupported format')
    }

    // Update request with download URL
    await supabase
      .from('data_export_requests')
      .update({
        status: 'completed',
        download_url: exportUrl,
        completed_at: new Date().toISOString()
      })
      .eq('id', requestId)

    // Send notification email
    await sendExportReadyEmail(supabase, userId, exportUrl)

  } catch (error) {
    console.error('Export processing error:', error)

    // Update request with error
    await supabase
      .from('data_export_requests')
      .update({
        status: 'failed'
      })
      .eq('id', requestId)
  }
}

async function fetchAllUserData(supabase: any, userId: string) {
  const [
    user,
    workspaces,
    subscriptions,
    transactions,
    sessions,
    auditLogs,
    securityEvents
  ] = await Promise.all([
    supabase.from('users').select('*').eq('id', userId).single(),
    supabase.from('workspaces').select('*').eq('owner_id', userId),
    supabase.from('subscriptions').select('*').eq('user_id', userId),
    supabase.from('payment_transactions').select('*').eq('user_id', userId),
    supabase.from('user_sessions').select('created_at, last_accessed_at, ip_address, user_agent').eq('user_id', userId),
    supabase.from('audit_logs').select('*').eq('actor_id', userId),
    supabase.from('security_events').select('*').eq('user_id', userId)
  ])

  return {
    user: user.data,
    workspaces: workspaces.data,
    subscriptions: subscriptions.data,
    transactions: transactions.data,
    sessions: sessions.data,
    auditLogs: auditLogs.data,
    securityEvents: securityEvents.data,
    exportedAt: new Date().toISOString()
  }
}

function convertToCSV(data: any): string {
  // Simple CSV conversion - in production, use a proper CSV library
  const rows = []

  // Add user data
  if (data.user) {
    rows.push('User Data')
    rows.push(Object.keys(data.user).join(','))
    rows.push(Object.values(data.user).join(','))
    rows.push('')
  }

  // Add other data sections
  ['workspaces', 'subscriptions', 'transactions', 'sessions', 'auditLogs', 'securityEvents'].forEach(section => {
    if (data[section] && data[section].length > 0) {
      rows.push(`${section.toUpperCase()}`)
      rows.push(Object.keys(data[section][0]).join(','))
      data[section].forEach((item: any) => {
        rows.push(Object.values(item).map(v => `"${v}"`).join(','))
      })
      rows.push('')
    }
  })

  return rows.join('\n')
}

async function uploadExportToStorage(
  supabase: any,
  userId: string,
  requestId: string,
  data: string,
  contentType: string
): Promise<string> {
  const fileName = `exports/${userId}/${requestId}/data.${contentType === 'application/json' ? 'json' : 'csv'}`

  const { error } = await supabase.storage
    .from('user-data')
    .upload(fileName, data, {
      contentType,
      upsert: true
    })

  if (error) throw error

  const { data: { publicUrl } } = supabase.storage
    .from('user-data')
    .getPublicUrl(fileName)

  // Create signed URL that expires in 7 days
  const { data: signedUrl } = await supabase.storage
    .from('user-data')
    .createSignedUrl(fileName, 7 * 24 * 60 * 60) // 7 days

  return signedUrl.signedUrl
}

async function sendExportReadyEmail(supabase: any, userId: string, downloadUrl: string) {
  const { data: user } = await supabase
    .from('users')
    .select('email')
    .eq('id', userId)
    .single()

  if (!user) return

  // Log email
  await supabase
    .from('email_logs')
    .insert({
      user_id: userId,
      template_name: 'data_export_ready',
      to_email: user.email,
      subject: 'Your Data Export is Ready',
      status: 'pending'
    })

  // Send via Resend
  const response = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.RESEND_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      from: 'noreply@raptorflow.com',
      to: [user.email],
      subject: 'Your Data Export is Ready',
      html: `
        <h1>Your Data Export is Ready</h1>
        <p>You requested a copy of your data. Your export is now available for download.</p>
        <p><a href="${downloadUrl}" style="background: #3B82F6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px;">Download Your Data</a></p>
        <p><strong>Note:</strong> This download link will expire in 7 days.</p>
        <p>If you didn't request this export, please contact our support team immediately.</p>
      `
    })
  })

  if (response.ok) {
    await supabase
      .from('email_logs')
      .update({ status: 'sent', sent_at: new Date().toISOString() })
      .eq('user_id', userId)
      .eq('template_name', 'data_export_ready')
      .eq('status', 'pending')
  }
}

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url)
    const requestId = searchParams.get('requestId')

    const supabase = createRouteHandlerClient({ cookies })

    // Get current user
    const { data: { session } } = await supabase.auth.getSession()

    if (!session) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    // Get export request
    const { data: exportRequest } = await supabase
      .from('data_export_requests')
      .select('*')
      .eq('id', requestId)
      .eq('user_id', (
        supabase.from('users').select('id').eq('auth_user_id', session.user.id).single()
      ))
      .single()

    if (!exportRequest) {
      return NextResponse.json({ error: 'Export request not found' }, { status: 404 })
    }

    return NextResponse.json({
      id: exportRequest.id,
      status: exportRequest.status,
      downloadUrl: exportRequest.download_url,
      expiresAt: exportRequest.expires_at,
      createdAt: exportRequest.created_at,
      completedAt: exportRequest.completed_at
    })

  } catch (error) {
    console.error('Get export status error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
