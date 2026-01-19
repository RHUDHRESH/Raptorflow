/**
 * ✅ ONBOARDING COMPLETION API
 * 
 * Called when user completes onboarding:
 * 1. Generates business context JSON
 * 2. Stores in Supabase storage
 * 3. Updates workspace with context URL
 * 4. Marks onboarding as complete
 */

import { NextRequest, NextResponse } from 'next/server';
import { getSupabaseAdmin } from '@/lib/supabase-admin';

export async function POST(request: NextRequest) {
    const supabase = getSupabaseAdmin();
    try {
        const { workspaceId, userId, steps, businessContext } = await request.json();

        // Validate required fields
        if (!workspaceId || !userId) {
            return NextResponse.json(
                { success: false, error: 'Missing required fields' },
                { status: 400 }
            );
        }

        // Generate filename
        const filename = `business_context_${workspaceId}_${Date.now()}.json`;
        const filepath = `business-contexts/${workspaceId}/${filename}`;

        // Store business context in Supabase storage
        const contextJson = JSON.stringify(businessContext, null, 2);
        const contextBlob = new Blob([contextJson], { type: 'application/json' });

        const { data: uploadData, error: uploadError } = await supabase
            .storage
            .from('raptorflow-assets')
            .upload(filepath, contextBlob, {
                contentType: 'application/json',
                upsert: true,
            });

        if (uploadError) {
            console.error('Failed to upload business context:', uploadError);
            // Try to create the bucket if it doesn't exist
            if (uploadError.message.includes('not found')) {
                await supabase.storage.createBucket('raptorflow-assets', {
                    public: false,
                });

                // Retry upload
                const { error: retryError } = await supabase
                    .storage
                    .from('raptorflow-assets')
                    .upload(filepath, contextBlob, {
                        contentType: 'application/json',
                        upsert: true,
                    });

                if (retryError) {
                    console.error('Retry upload failed:', retryError);
                }
            }
        }

        // Get signed URL for the file
        const { data: signedUrlData } = await supabase
            .storage
            .from('raptorflow-assets')
            .createSignedUrl(filepath, 60 * 60 * 24 * 365); // 1 year

        const businessContextUrl = signedUrlData?.signedUrl || filepath;

        // Also store in database for quick access
        const { error: dbError } = await supabase
            .from('business_contexts')
            .upsert({
                workspace_id: workspaceId,
                user_id: userId,
                context_data: businessContext,
                context_url: businessContextUrl,
                version: businessContext.version || '1.0.0',
                created_at: new Date().toISOString(),
                updated_at: new Date().toISOString(),
            }, {
                onConflict: 'workspace_id',
            });

        if (dbError) {
            console.error('Failed to store context in database:', dbError);
            // Not fatal - continue
        }

        // Update workspace to mark onboarding as complete
        const { error: updateError } = await supabase
            .from('workspaces')
            .update({
                onboarding_completed: true,
                onboarding_step: 24,
                business_context_url: businessContextUrl,
                updated_at: new Date().toISOString(),
            })
            .eq('id', workspaceId);

        if (updateError) {
            console.error('Failed to update workspace:', updateError);
            return NextResponse.json(
                { success: false, error: 'Failed to update workspace' },
                { status: 500 }
            );
        }

        return NextResponse.json({
            success: true,
            message: 'Onboarding completed successfully',
            businessContextUrl,
            filepath,
        });

    } catch (error) {
        console.error('Onboarding completion error:', error);
        return NextResponse.json(
            { success: false, error: 'Internal server error' },
            { status: 500 }
        );
    }
}

/**
 * GET: Retrieve business context for a workspace
 */
export async function GET(request: NextRequest) {
    const supabase = getSupabaseAdmin();
    try {
        const { searchParams } = new URL(request.url);
        const workspaceId = searchParams.get('workspaceId');

        if (!workspaceId) {
            return NextResponse.json(
                { success: false, error: 'Workspace ID is required' },
                { status: 400 }
            );
        }

        // Get from database
        const { data, error } = await supabase
            .from('business_contexts')
            .select('*')
            .eq('workspace_id', workspaceId)
            .single();

        if (error || !data) {
            return NextResponse.json(
                { success: false, error: 'Business context not found' },
                { status: 404 }
            );
        }

        return NextResponse.json({
            success: true,
            businessContext: data.context_data,
            url: data.context_url,
            version: data.version,
            updatedAt: data.updated_at,
        });

    } catch (error) {
        console.error('Get business context error:', error);
        return NextResponse.json(
            { success: false, error: 'Internal server error' },
            { status: 500 }
        );
    }
}
