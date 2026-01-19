import { NextRequest, NextResponse } from 'next/server';

interface BCMData {
  foundation: {
    company: string;
    mission: string;
    value_prop: string;
  };
  icps: Array<{
    id: string;
    name: string;
    demographics: any;
    psychographics: any;
  }>;
  competitive: {
    competitors: string[];
    positioning: string;
    differentiation: string;
  };
  messaging: {
    one_liner: string;
    value_props: string[];
    brand_voice: {
      tone: string[];
      do_list: string[];
      dont_list: string[];
    };
  };
  meta: {
    source: string;
    token_budget: number;
    version: number;
    checksum: string;
    created_at: string;
    updated_at: string;
  };
}

function calculateChecksum(data: Omit<BCMData, 'meta'>): string {
  const manifestStr = JSON.stringify(data, Object.keys(data).sort());
  let hash = 0;
  for (let i = 0; i < manifestStr.length; i++) {
    const char = manifestStr.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32-bit integer
  }
  return hash.toString(16);
}

function extractFoundation(onboardingData: any): BCMData['foundation'] {
  const stepData = onboardingData.step_1 || {};
  const foundationData = onboardingData.step_2 || {};
  
  return {
    company: stepData.company_name || foundationData.company?.name || 'Unknown Company',
    mission: foundationData.foundation?.mission || 'To solve meaningful problems for our customers',
    value_prop: foundationData.foundation?.value_prop || 'Delivering exceptional value through innovation'
  };
}

function extractICPs(onboardingData: any): BCMData['icps'] {
  const icpData = onboardingData.step_3 || {};
  
  if (icpData.icps && Array.isArray(icpData.icps)) {
    return icpData.icps.map((icp: any, index: number) => ({
      id: icp.id || `icp-${index + 1}`,
      name: icp.name || `ICP ${index + 1}`,
      demographics: icp.demographics || {},
      psychographics: icp.psychographics || {}
    }));
  }
  
  // Default ICP if none found
  return [{
    id: 'icp-1',
    name: 'Default Customer Profile',
    demographics: {
      role: 'Professional',
      company_size: 'Small to Medium',
      industry: 'Technology'
    },
    psychographics: {
      values: ['Efficiency', 'Quality', 'Innovation'],
      challenges: ['Time constraints', 'Budget limitations']
    }
  }];
}

function extractCompetitive(onboardingData: any): BCMData['competitive'] {
  const competitiveData = onboardingData.step_4 || {};
  
  return {
    competitors: competitiveData.competitors || [],
    positioning: competitiveData.positioning || 'Industry leader in quality and innovation',
    differentiation: competitiveData.differentiation || 'Unique approach to solving customer problems'
  };
}

function extractMessaging(onboardingData: any): BCMData['messaging'] {
  const messagingData = onboardingData.step_5 || {};
  const foundationData = onboardingData.step_2 || {};
  
  return {
    one_liner: messagingData.one_liner || foundationData.messaging?.one_liner || 'Solving problems with innovative solutions',
    value_props: messagingData.value_props || foundationData.messaging?.value_props || [
      'Quality and reliability',
      'Exceptional customer service',
      'Innovative approach'
    ],
    brand_voice: {
      tone: messagingData.brand_voice?.tone || foundationData.messaging?.brand_voice?.tone || ['Professional', 'Confident', 'Clear'],
      do_list: messagingData.brand_voice?.do_list || foundationData.messaging?.brand_voice?.do_list || [
        'Be clear and concise',
        'Focus on benefits',
        'Use data-backed claims'
      ],
      dont_list: messagingData.brand_voice?.dont_list || foundationData.messaging?.brand_voice?.dont_list || [
        'Use excessive jargon',
        'Make unrealistic promises',
        'Be vague about outcomes'
      ]
    }
  };
}

export async function POST(request: NextRequest) {
  try {
    const { onboarding_data } = await request.json();
    
    if (!onboarding_data) {
      return NextResponse.json(
        { success: false, error: 'Onboarding data is required' },
        { status: 400 }
      );
    }

    // Extract BCM data from onboarding
    const foundation = extractFoundation(onboarding_data);
    const icps = extractICPs(onboarding_data);
    const competitive = extractCompetitive(onboarding_data);
    const messaging = extractMessaging(onboarding_data);

    // Create BCM without meta for checksum calculation
    const bcmWithoutMeta = {
      foundation,
      icps,
      competitive,
      messaging
    };

    // Calculate checksum
    const checksum = calculateChecksum(bcmWithoutMeta);

    // Create final BCM with meta
    const bcm: BCMData = {
      ...bcmWithoutMeta,
      meta: {
        source: 'onboarding',
        token_budget: 1200,
        version: 1,
        checksum,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }
    };

    return NextResponse.json({
      success: true,
      bcm
    });

  } catch (error) {
    console.error('BCM generation error:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to generate Business Context Model' },
      { status: 500 }
    );
  }
}
