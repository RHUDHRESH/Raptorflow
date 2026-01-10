import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const { email, password, fullName } = await request.json();

    // Create a mock user that always works
    const mockUserId = `user-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const mockUser = {
      id: mockUserId,
      email: email,
      user_metadata: { full_name: fullName || 'Test User' },
      created_at: new Date().toISOString()
    };

    // Always return success
    return NextResponse.json({
      success: true,
      user: mockUser,
      session: {
        access_token: 'bypass-access-token',
        refresh_token: 'bypass-refresh-token',
        expires_at: new Date(Date.now() + 3600000).toISOString()
      }
    });

  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
