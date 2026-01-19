import { createRouteHandlerClient } from '@supabase/auth-helpers-nextjs'
import { cookies } from 'next/headers'
import { NextResponse } from 'next/server'
import { authenticator } from 'otplib'
import QRCode from 'qrcode'

export async function POST(request: Request) {
  try {
    const supabase = createRouteHandlerClient({ cookies })
    
    // Get current user
    const { data: { session } } = await supabase.auth.getSession()
    
    if (!session) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }
    
    // Check if user is admin
    const { data: user } = await supabase
      .from('users')
      .select('id, role, mfa_enabled')
      .eq('auth_user_id', session.user.id)
      .single()
    
    if (!user || !['admin', 'super_admin'].includes(user.role)) {
      return NextResponse.json({ error: 'MFA only available for admin users' }, { status: 403 })
    }
    
    // Generate secret
    const secret = authenticator.generateSecret()
    const issuer = 'Raptorflow'
    const label = `${user.email}@${issuer}`
    const uri = authenticator.keyuri(label, issuer, secret)
    
    // Generate QR code
    const qrCodeDataURL = await QRCode.toDataURL(uri)
    
    // Generate backup codes
    const backupCodes = Array.from({ length: 10 }, () => 
      authenticator.generateSecret().slice(0, 8).toUpperCase()
    )
    
    // Store secret temporarily (not enabled yet)
    await supabase
      .from('users')
      .update({
        mfa_secret: secret,
        backup_codes: backupCodes
      })
      .eq('id', user.id)
    
    // Log the action
    await supabase
      .from('security_events')
      .insert({
        user_id: user.id,
        event_type: 'mfa_enabled',
        details: { action: 'setup_initiated' }
      })
    
    return NextResponse.json({
      secret,
      qrCode: qrCodeDataURL,
      backupCodes,
      message: 'Scan the QR code with your authenticator app'
    })
    
  } catch (error) {
    console.error('MFA setup error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

export async function PUT(request: Request) {
  try {
    const { token } = await request.json()
    
    const supabase = createRouteHandlerClient({ cookies })
    
    // Get current user
    const { data: { session } } = await supabase.auth.getSession()
    
    if (!session) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }
    
    // Get user with MFA secret
    const { data: user } = await supabase
      .from('users')
      .select('id, mfa_secret, mfa_enabled')
      .eq('auth_user_id', session.user.id)
      .single()
    
    if (!user || !user.mfa_secret) {
      return NextResponse.json({ error: 'MFA setup not initiated' }, { status: 400 })
    }
    
    // Verify token
    const isValid = authenticator.verify({
      token,
      secret: user.mfa_secret
    })
    
    if (!isValid) {
      // Log failed attempt
      await supabase
        .from('security_events')
        .insert({
          user_id: user.id,
          event_type: 'login_failure',
          details: { reason: 'invalid_mfa_token' }
        })
      
      return NextResponse.json({ error: 'Invalid token' }, { status: 400 })
    }
    
    // Enable MFA
    await supabase
      .from('users')
      .update({ mfa_enabled: true })
      .eq('id', user.id)
    
    // Log success
    await supabase
      .from('security_events')
      .insert({
        user_id: user.id,
        event_type: 'mfa_enabled',
        details: { action: 'setup_completed' }
      })
    
    return NextResponse.json({
      success: true,
      message: 'MFA enabled successfully'
    })
    
  } catch (error) {
    console.error('MFA verification error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

export async function DELETE(request: Request) {
  try {
    const { password } = await request.json()
    
    const supabase = createRouteHandlerClient({ cookies })
    
    // Get current user
    const { data: { session } } = await supabase.auth.getSession()
    
    if (!session) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }
    
    // Verify password
    const { error: signInError } = await supabase.auth.signInWithPassword({
      email: session.user.email!,
      password
    })
    
    if (signInError) {
      return NextResponse.json({ error: 'Invalid password' }, { status: 400 })
    }
    
    // Get user
    const { data: user } = await supabase
      .from('users')
      .select('id, role')
      .eq('auth_user_id', session.user.id)
      .single()
    
    if (!user) {
      return NextResponse.json({ error: 'User not found' }, { status: 404 })
    }
    
    // Check if MFA is required for this role
    const { data: mfaRequired } = await supabase
      .from('system_settings')
      .select('value')
      .eq('key', 'enable_mfa_for_admins')
      .single()
    
    if (mfaRequired?.value === true && ['admin', 'super_admin'].includes(user.role)) {
      return NextResponse.json({ 
        error: 'MFA cannot be disabled for admin users' 
      }, { status: 400 })
    }
    
    // Disable MFA
    await supabase
      .from('users')
      .update({
        mfa_enabled: false,
        mfa_secret: null,
        backup_codes: null
      })
      .eq('id', user.id)
    
    // Log the action
    await supabase
      .from('security_events')
      .insert({
        user_id: user.id,
        event_type: 'mfa_disabled',
        details: { action: 'disabled_by_user' }
      })
    
    return NextResponse.json({
      success: true,
      message: 'MFA disabled successfully'
    })
    
  } catch (error) {
    console.error('MFA disable error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
