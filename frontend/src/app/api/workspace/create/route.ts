/**
 * 🏢 WORKSPACE CREATE API
 * 
 * Creates a workspace for the authenticated user.
 * Called after successful payment processing.
 */

import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

export async function POST(request: NextRequest) {
    try {
        const { userId, workspaceName, planId, email } = await request.json();

        // Validate required fields
        if (!userId) {
            return NextResponse.json(
                { success: false, error: 'User ID is required' },
                { status: 400 }
            );
        }

        // Check if workspace already exists
        const { data: existingWorkspace, error: checkError } = await supabase
            .from('workspaces')
            .select('*')
            .eq('owner_id', userId)
            .single();

        if (existingWorkspace) {
            return NextResponse.json({
                success: true,
                workspace: existingWorkspace,
                message: 'Workspace already exists',
            });
        }

        // Generate workspace name if not provided
        const name = workspaceName || `${email?.split('@')[0] || 'My'}'s Workspace`;

        // Create workspace
        const { data: workspace, error: createError } = await supabase
            .from('workspaces')
            .insert({
                owner_id: userId,
                name: name,
                plan_id: planId || 'free',
                onboarding_completed: false,
                onboarding_step: 1,
                settings: {
                    theme: 'light',
                    notifications: true,
                },
                created_at: new Date().toISOString(),
                updated_at: new Date().toISOString(),
            })
            .select()
            .single();

        if (createError) {
            console.error('Workspace creation error:', createError);
            return NextResponse.json(
                { success: false, error: 'Failed to create workspace' },
                { status: 500 }
            );
        }

        // Also create workspace membership
        await supabase
            .from('workspace_members')
            .insert({
                workspace_id: workspace.id,
                user_id: userId,
                role: 'owner',
                joined_at: new Date().toISOString(),
            });

        return NextResponse.json({
            success: true,
            workspace: workspace,
            message: 'Workspace created successfully',
        });

    } catch (error) {
        console.error('Workspace creation error:', error);
        return NextResponse.json(
            { success: false, error: 'Internal server error' },
            { status: 500 }
        );
    }
}
