import { NextRequest, NextResponse } from 'next/server';
import { createOnboardingGraph } from '@/lib/agents/spine';
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY || '';
const supabase = (supabaseUrl && supabaseKey) ? createClient(supabaseUrl, supabaseKey) : null;

export async function POST(req: NextRequest) {
    try {
        const foundationData = await req.json();

        if (!foundationData) {
            return NextResponse.json({ error: 'Missing foundation data' }, { status: 400 });
        }

        const graph = createOnboardingGraph();

        // Invoke the graph
        const finalState = await graph.invoke({
            foundation: foundationData,
            status: ['Starting synthesis...'],
            errors: [],
        });

        if (finalState.errors && finalState.errors.length > 0) {
            return NextResponse.json({
                error: 'Synthesis failed',
                details: finalState.errors
            }, { status: 500 });
        }

        // Persist to Supabase if available
        if (supabase) {
            if (finalState.campaign) {
                await supabase.from('campaigns').insert({
                    id: finalState.campaign.id,
                    tenant_id: '00000000-0000-0000-0000-000000000000',
                    title: finalState.campaign.name,
                    objective: finalState.campaign.objective,
                    status: finalState.campaign.status,
                    created_at: finalState.campaign.createdAt
                });
            }

            if (finalState.moves && finalState.moves.length > 0) {
                const dbMoves = finalState.moves.map((m: any) => ({
                    id: m.id,
                    campaign_id: m.campaignId,
                    title: m.name,
                    description: m.description,
                    status: m.status,
                    priority: 1,
                    created_at: m.createdAt,
                    checklist: m.checklist
                }));
                await supabase.from('moves').insert(dbMoves);
            }
        }

        return NextResponse.json({
            success: true,
            message: 'Synthesis complete',
            icps: finalState.icps,
            moves: finalState.moves,
            campaign: finalState.campaign,
            status: finalState.status
        });

    } catch (error: any) {
        console.error('Onboarding API Error:', error);
        return NextResponse.json({
            error: 'Internal Server Error',
            message: error.message
        }, { status: 500 });
    }
}
