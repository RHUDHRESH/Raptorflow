import { createServerSupabaseClient, createServiceSupabaseClient } from '@/lib/auth-server'
import { NextResponse } from 'next/server'

export async function GET() {
  try {
    // Use service client for plans to avoid RLS issues (plans should be publicly readable)
    let supabase;
    try {
      supabase = await createServiceSupabaseClient()
    } catch {
      // Fallback to regular client if service key not available
      supabase = await createServerSupabaseClient()
    }

    // Fetch all active plans
    let plans = null;
    let error = null;

    // Try subscription_plans table first
    const { data: subPlans, error: subError } = await supabase
      .from('subscription_plans')
      .select('*')
      .eq('is_active', true)
      .order('sort_order', { ascending: true });

    if (!subError && subPlans) {
      plans = subPlans;
      error = subError;
    } else {
      // Fallback to plans table
      const { data: fallbackPlans, error: fallbackError } = await supabase
        .from('plans')
        .select('*')
        .eq('is_active', true)
        .order('display_order', { ascending: true });

      plans = fallbackPlans;
      error = fallbackError;
    }

    if (error) {
      console.error('Plans fetch error:', error)
    }

    // Define hardcoded plans with all required fields
    const hardcodedPlans = [
      {
        id: 'ascent',
        name: 'Ascent',
        slug: 'ascent',
        description: 'For founders just getting started with systematic marketing.',
        price_monthly_paise: 500000,  // ₹5,000/month
        price_yearly_paise: 5000000, // ₹50,000/year
        storage_limit_bytes: 5 * 1024 * 1024 * 1024, // 5 GB
        features: {
          projects: 3,
          team_members: 1,
          support: 'email'
        },
        sort_order: 1,
        is_active: true,
        popular: false
      },
      {
        id: 'glide',
        name: 'Glide',
        slug: 'glide',
        description: 'For founders scaling their marketing engine.',
        price_monthly_paise: 700000,  // ₹7,000/month
        price_yearly_paise: 7000000, // ₹70,000/year
        storage_limit_bytes: 25 * 1024 * 1024 * 1024, // 25 GB
        features: {
          projects: -1, // Unlimited
          team_members: 5,
          support: 'priority'
        },
        sort_order: 2,
        popular: true,
        is_active: true
      },
      {
        id: 'soar',
        name: 'Soar',
        slug: 'soar',
        description: 'For teams running multi-channel campaigns.',
        price_monthly_paise: 1000000, // ₹10,000/month
        price_yearly_paise: 10000000, // ₹100,000/year
        storage_limit_bytes: 100 * 1024 * 1024 * 1024, // 100 GB
        features: {
          projects: -1, // Unlimited
          team_members: -1, // Unlimited
          support: 'dedicated'
        },
        sort_order: 3,
        is_active: true,
        popular: false
      }
    ];

    // If no plans from DB, return hardcoded
    if (!plans || plans.length === 0) {
      return NextResponse.json({ plans: hardcodedPlans })
    }

    // Map database plans to frontend format with hardcoded values for known slugs
    const mappedPlans = (plans || []).map(p => {
      const hardcoded = hardcodedPlans.find(hp => hp.slug === p.slug);

      if (hardcoded) {
        return hardcoded;
      }

      // For unknown plans, map database fields
      return {
        id: p.slug || p.id,
        name: p.name,
        slug: p.slug,
        description: p.description,
        price_monthly_paise: p.price_monthly || 0,
        price_yearly_paise: p.price_annual || 0,
        storage_limit_bytes: p.storage_limit_bytes || 5 * 1024 * 1024 * 1024,
        features: p.features || {},
        is_active: p.is_active,
        sort_order: p.sort_order,
        popular: p.popular || false
      };
    });

    return NextResponse.json({ plans: mappedPlans })

  } catch (err) {
    console.error('Plans API error:', err)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
