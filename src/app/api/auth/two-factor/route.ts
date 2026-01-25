import { NextResponse } from 'next/server';
import { ValidationError, AuthenticationError, createDatabaseError } from '@/lib/security/error-handler';
import { validateEmail, sanitizeInput } from '@/lib/security/input-validation';
import { serviceAuth } from '@/lib/auth-service';
import crypto from 'crypto';

export async function POST(request: Request) {
  try {
    const { email, action, code, backupCode } = await request.json();
    
    // Validate input
    if (!email || typeof email !== 'string') {
      throw new ValidationError('Email is required');
    }
    
    const sanitizedEmail = sanitizeInput(email);
    
    if (!validateEmail(sanitizedEmail)) {
      throw new ValidationError('Invalid email format');
    }
    
    if (!action || typeof action !== 'string') {
      throw new ValidationError('Action is required');
    }
    
    const sanitizedAction = sanitizeInput(action);
    
    // Get service auth client for admin operations
    const supabase = serviceAuth.getSupabaseClient();
    
    switch (sanitizedAction) {
      case 'enable':
        return await enableTwoFactor(supabase, sanitizedEmail);
      case 'disable':
        return await disableTwoFactor(supabase, sanitizedEmail);
      case 'verify':
        return await verifyTwoFactor(supabase, sanitizedEmail, code, backupCode);
      case 'generate-backup':
        return await generateBackupCodes(supabase, sanitizedEmail);
      default:
        throw new ValidationError('Invalid action');
    }
    
  } catch (error) {
    console.error('Two-factor authentication error:', error);
    
    if (error instanceof ValidationError) {
      return NextResponse.json(
        { error: error.message },
        { status: 400 }
      );
    }
    
    if (error instanceof AuthenticationError) {
      return NextResponse.json(
        { error: error.message },
        { status: 401 }
      );
    }
    
    return NextResponse.json(
      { error: 'Failed to process two-factor authentication' },
      { status: 500 }
    );
  }
}

async function enableTwoFactor(supabase: any, email: string) {
  // Get user by email
  const { data: userData, error: userError } = await supabase.auth.admin.listUsers();
  
  if (userError) {
    throw createDatabaseError('get user by email', userError);
  }
  
  const user = userData.users.find((u: any) => u.email === email);
  
  if (!user) {
    throw new AuthenticationError('User not found');
  }
  
  // Generate backup codes
  const backupCodes = generateBackupCodesArray();
  
  // Store two-factor settings
  const { error: settingsError } = await supabase
    .from('two_factor_settings')
    .upsert({
      user_id: user.id,
      enabled: true,
      backup_codes: backupCodes,
      created_at: new Date().toISOString()
    });
  
  if (settingsError) {
    throw createDatabaseError('store two-factor settings', settingsError);
  }
  
  // Generate QR code data (simplified - in production, use proper TOTP library)
  const secret = generateTOTPSecret();
  const qrCodeData = generateQRCodeData(email, secret);
  
  return NextResponse.json({
    message: 'Two-factor authentication enabled',
    secret,
    qrCodeData,
    backupCodes
  });
}

async function disableTwoFactor(supabase: any, email: string) {
  // Get user by email
  const { data: userData, error: userError } = await supabase.auth.admin.listUsers();
  
  if (userError) {
    throw createDatabaseError('get user by email', userError);
  }
  
  const user = userData.users.find((u: any) => u.email === email);
  
  if (!user) {
    throw new AuthenticationError('User not found');
  }
  
  // Disable two-factor
  const { error: settingsError } = await supabase
    .from('two_factor_settings')
    .update({ enabled: false })
    .eq('user_id', user.id);
  
  if (settingsError) {
    throw createDatabaseError('disable two-factor', settingsError);
  }
  
  return NextResponse.json({
    message: 'Two-factor authentication disabled'
  });
}

async function verifyTwoFactor(supabase: any, email: string, code?: string, backupCode?: string) {
  // Get user by email
  const { data: userData, error: userError } = await supabase.auth.admin.listUsers();
  
  if (userError) {
    throw createDatabaseError('get user by email', userError);
  }
  
  const user = userData.users.find((u: any) => u.email === email);
  
  if (!user) {
    throw new AuthenticationError('User not found');
  }
  
  // Get two-factor settings
  const { data: settingsData, error: settingsError } = await supabase
    .from('two_factor_settings')
    .select('*')
    .eq('user_id', user.id)
    .single();
  
  if (settingsError || !settingsData) {
    throw new AuthenticationError('Two-factor authentication not enabled');
  }
  
  let isValid = false;
  
  if (code) {
    // Verify TOTP code (simplified - in production, use proper TOTP library)
    isValid = verifyTOTPCode(code, settingsData.secret);
  } else if (backupCode) {
    // Verify backup code
    isValid = verifyBackupCode(backupCode, settingsData.backup_codes);
  }
  
  if (!isValid) {
    throw new AuthenticationError('Invalid verification code');
  }
  
  return NextResponse.json({
    message: 'Two-factor authentication verified',
    verified: true
  });
}

async function generateBackupCodes(supabase: any, email: string) {
  // Get user by email
  const { data: userData, error: userError } = await supabase.auth.admin.listUsers();
  
  if (userError) {
    throw createDatabaseError('get user by email', userError);
  }
  
  const user = userData.users.find((u: any) => u.email === email);
  
  if (!user) {
    throw new AuthenticationError('User not found');
  }
  
  // Generate new backup codes
  const backupCodes = generateBackupCodesArray();
  
  // Update backup codes
  const { error: updateError } = await supabase
    .from('two_factor_settings')
    .update({ backup_codes: backupCodes })
    .eq('user_id', user.id);
  
  if (updateError) {
    throw createDatabaseError('update backup codes', updateError);
  }
  
  return NextResponse.json({
    message: 'Backup codes regenerated',
    backupCodes
  });
}

// Helper functions (simplified - in production, use proper libraries)
function generateTOTPSecret(): string {
  return crypto.randomBytes(20).toString('base64').replace(/[^A-Za-z0-9]/g, '').substring(0, 32);
}

function generateQRCodeData(email: string, secret: string): string {
  // Simplified QR code generation - in production, use proper TOTP library
  return `otpauth://totp/RaptorFlow:${email}?secret=${secret}&issuer=RaptorFlow`;
}

function verifyTOTPCode(code: string, secret: string): boolean {
  // Simplified TOTP verification - in production, use proper TOTP library
  // This is a placeholder implementation
  return code.length === 6 && /^\d+$/.test(code);
}

function generateBackupCodesArray(): string[] {
  const codes = [];
  for (let i = 0; i < 10; i++) {
    codes.push(Math.random().toString().substring(2, 8));
  }
  return codes;
}

function verifyBackupCode(backupCode: string, storedCodes: string[]): boolean {
  return storedCodes.includes(backupCode);
}
