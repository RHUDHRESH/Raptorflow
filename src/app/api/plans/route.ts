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
      // Fallback to original industrial pricing for 2026
      const fallbackPlans = [
        {
          id: 'ascent',
          name: 'Ascent',
          slug: 'ascent',
          description: 'For founders just getting started with systematic marketing.',
          price_monthly_paise: 500000,  // ₹5,000/month
          price_yearly_paise: 5000000, // ₹50,000/year
          features: ["Foundation setup", "3 weekly Moves", "Basic Muse AI", "Matrix analytics", "Email support"],
          sort_order: 1,
          is_active: true
        },
        {
          id: 'glide',
          name: 'Glide',
          slug: 'glide',
          description: 'For founders scaling their marketing engine.',
          price_monthly_paise: 700000,  // ₹7,000/month
          price_yearly_paise: 7000000, // ₹70,000/year
          features: ["Everything in Ascent", "Unlimited Moves", "Advanced Muse", "Cohort segmentation", "Priority support"],
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
          features: ["Everything in Glide", "Unlimited team seats", "Custom AI training", "API access", "Dedicated support"],
          sort_order: 3,
          is_active: true
        }
      ]
      return NextResponse.json({ plans: fallbackPlans })
    }

    // Even if we got data from DB, use the original pricing if IDs match
    const updatedPlans = (plans || []).map(p => {
      // Convert database field names to frontend field names
      const planData = {
        id: p.slug, // Use slug as ID for frontend
        name: p.name,
        slug: p.slug,
        description: p.description,
        price_monthly_paise: p.price_monthly, // Convert to paise field name
        price_yearly_paise: p.price_annual, // Convert to paise field name
        features: p.features,
        is_active: p.is_active,
        sort_order: p.sort_order
      };

      if (p.slug === 'ascent') return { 
        ...planData, 
        id: 'ascent',
        name: 'Ascent',
        slug: 'ascent',
        price_monthly_paise: 500000,  // ₹5,000/month
        price_yearly_paise: 5000000, // ₹50,000/year
        features: ["Foundation setup", "3 weekly Moves", "Basic Muse AI", "Matrix analytics", "Email support"]
      };
      if (p.slug === 'glide') return { 
        ...planData, 
        id: 'glide',
        name: 'Glide',
        slug: 'glide',
        price_monthly_paise: 700000,  // ₹7,000/month
        price_yearly_paise: 7000000, // ₹70,000/year
        features: ["Everything in Ascent", "Unlimited Moves", "Advanced Muse", "Cohort segmentation", "Priority support"],
        popular: true
      };
      if (p.slug === 'soar') return { 
        ...planData, 
        id: 'soar',
        name: 'Soar',
        slug: 'soar',
        price_monthly_paise: 1000000, // ₹10,000/month
        price_yearly_paise: 10000000, // ₹100,000/year
        features: ["Everything in Glide", "Unlimited team seats", "Custom AI training", "API access", "Dedicated support"]
      };
      return planData;
    });

    return NextResponse.json({ plans: updatedPlans })

  } catch (err) {
    console.error('Plans API error:', err)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
