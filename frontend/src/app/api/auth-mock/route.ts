import { NextResponse } from 'next/server';

// Mock user database
const mockUsers = new Map();

export async function POST(request: Request) {
  try {
    const { email, password, fullName, action } = await request.json();

    if (action === 'signup') {
      // Mock signup
      const userId = `mock-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      const mockUser = {
        id: userId,
        email: email,
        full_name: fullName,
        created_at: new Date().toISOString(),
        subscription_plan: 'soar',
        subscription_status: 'active'
      };

      mockUsers.set(userId, mockUser);

      return NextResponse.json({
        success: true,
        user: {
          id: userId,
          email: email,
          user_metadata: { full_name: fullName }
        },
        session: {
          access_token: 'mock-access-token',
          refresh_token: 'mock-refresh-token',
          expires_at: new Date(Date.now() + 3600000).toISOString()
        }
      });
    }

    if (action === 'login') {
      // Mock login
      const user = Array.from(mockUsers.values()).find(u => u.email === email);

      if (user && password === 'mockpassword') {
        return NextResponse.json({
          success: true,
          user: {
            id: user.id,
            email: user.email,
            user_metadata: { full_name: user.full_name }
          },
          session: {
            access_token: 'mock-access-token',
            refresh_token: 'mock-refresh-token',
            expires_at: new Date(Date.now() + 3600000).toISOString()
          }
        });
      }

      return NextResponse.json({ success: false, error: 'Invalid credentials' });
    }

    return NextResponse.json({ success: false, error: 'Invalid action' });

  } catch (error: any) {
    return NextResponse.json({ error: error instanceof Error ? error.message : "Unknown error" }, { status: 500 });
  }
}
