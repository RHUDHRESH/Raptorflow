import { createServerSupabaseClient } from '@/lib/auth-server'
import { NextResponse } from 'next/server'
import crypto from 'crypto'
// eslint-disable-next-line @typescript-eslint/no-require-imports
const jwt = require('jsonwebtoken')

export async function POST(request: Request) {
  try {
    const { targetUserId } = await request.json()

    const supabase = await createServerSupabaseClient()

    // Get current user
    const { data: { session } } = await supabase.auth.getSession()

    if (!session) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    // Check if user is admin
    const { data: currentUser } = await supabase
      .from('users')
      .select('role, id')
      .eq('auth_user_id', session.user.id)
      .single()

    if (!currentUser || !['admin', 'super_admin'].includes(currentUser.role)) {
      return NextResponse.json({ error: 'Insufficient permissions' }, { status: 403 })
    }

    // Get target user
    const { data: targetUser } = await supabase
      .from('users')
      .select('auth_user_id, email, role')
      .eq('id', targetUserId)
      .single()

    if (!targetUser) {
      return NextResponse.json({ error: 'User not found' }, { status: 404 })
    }

    // Log impersonation
    await supabase
      .from('admin_actions')
      .insert({
        admin_id: currentUser.id,
        target_user_id: targetUserId,
        action: 'impersonate_user',
        details: {
          target_email: targetUser.email,
          target_role: targetUser.role
        },
        ip_address: request.headers.get('x-forwarded-for') || 'unknown',
        user_agent: request.headers.get('user-agent') || 'unknown'
      })

    // Create impersonation token
    const impersonationToken = jwt.sign(
      {
        type: 'impersonation',
        originalUserId: currentUser.id,
        targetUserId: targetUserId,
        targetAuthUserId: targetUser.auth_user_id,
        expiresAt: Date.now() + 60 * 60 * 1000 // 1 hour
      },
      process.env.IMPERSONATION_SECRET || crypto.randomBytes(32).toString('hex'),
      { expiresIn: '1h' }
    )

    return NextResponse.json({
      token: impersonationToken,
      originalUserId: currentUser.id,
      targetUserId: targetUserId
    })

  } catch (error) {
    console.error('Impersonation error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
