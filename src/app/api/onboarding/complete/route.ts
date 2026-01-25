import { NextRequest, NextResponse } from 'next/server';

// Simple onboarding completion endpoint
export async function POST(request: NextRequest) {
    try {
        const { workspaceId, userId, steps, businessContext } = await request.json();

        // Validate required fields
        if (!workspaceId || !userId) {
            return NextResponse.json(
                { success: false, error: 'Missing required fields' },
                { status: 400 }
            );
        }

        // Mock onboarding completion
        return NextResponse.json({
            success: true,
            message: 'Onboarding completed successfully (mock mode)',
            data: {
                workspaceId,
                userId,
                completedAt: new Date().toISOString(),
                stepsCompleted: steps || [],
                businessContext: businessContext || {},
                mockMode: true
            }
        });

    } catch (error) {
        console.error('Onboarding completion error:', error);
        return NextResponse.json(
            { success: false, error: 'Failed to complete onboarding' },
            { status: 500 }
        );
    }
}
