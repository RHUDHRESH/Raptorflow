import { createServerSupabaseClient } from '@/lib/auth-server'
import { NextResponse } from 'next/server'

export async function GET() {
  try {
    const supabase = createServerSupabaseClient()

    // Fetch all active plans
    const { data: plans, error } = await supabase
      .from('plans')
      .select('*')
      .eq('is_active', true)
      .order('display_order', { ascending: true })

    if (error) {
      console.error('Plans fetch error:', error)
      // Fallback to hardcoded industrial pricing for 2026
      const fallbackPlans = [
        {
          id: 'ascent',
          name: 'Ascent',
          slug: 'ascent',
          description: 'For founders just getting started with systematic marketing.',
          price_monthly_paise: 500000,
          price_yearly_paise: 5000000,
          storage_limit_bytes: 5 * 1024 * 1024 * 1024,
          features: { projects: 3, team_members: 1, support: 'email' },
          display_order: 1,
          is_active: true
        },
        {
          id: 'glide',
          name: 'Glide',
          slug: 'glide',
          description: 'For founders scaling their marketing engine.',
          price_monthly_paise: 700000,
          price_yearly_paise: 7000000,
          storage_limit_bytes: 25 * 1024 * 1024 * 1024,
          features: { projects: 10, team_members: 5, support: 'priority' },
          display_order: 2,
          popular: true,
          is_active: true
        },
        {
          id: 'soar',
          name: 'Soar',
          slug: 'soar',
          description: 'For teams running multi-channel campaigns.',
          price_monthly_paise: 1000000,
          price_yearly_paise: 10000000,
          storage_limit_bytes: 100 * 1024 * 1024 * 1024,
          features: { projects: -1, team_members: -1, support: 'dedicated' },
          display_order: 3,
          is_active: true
        }
      ]
      return NextResponse.json({ plans: fallbackPlans })
    }

    // Even if we got data from DB, override with latest 2026 industrial pricing if slugs match
    const updatedPlans = plans.map(p => {
      if (p.slug === 'ascent') return { ...p, price_monthly_paise: 500000, price_yearly_paise: 5000000 };
      if (p.slug === 'glide') return { ...p, price_monthly_paise: 700000, price_yearly_paise: 7000000 };
      if (p.slug === 'soar') return { ...p, price_monthly_paise: 1000000, price_yearly_paise: 10000000 };
      return p;
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
