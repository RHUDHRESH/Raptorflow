import {
  BehavioralPrinciple,
  RiskLevel,
  ChannelType,
  GoalType,
} from '../blackbox-types';

export interface LeverTemplate {
  id: string;
  principle: BehavioralPrinciple;
  title: string;
  hypothesis: string;
  control: string;
  variant: string;
  success_metric: string;
  sample_size: string;
  duration_days: number;
  action_steps: string[];
  why: string;
  allowed_goals?: GoalType[];
  allowed_channels?: ChannelType[];
}

export interface ConstraintTemplate {
  id: string;
  description: string;
  risk_level: RiskLevel;
}

export const LEVERS: LeverTemplate[] = [
  // ==============================
  // EMAIL EXPERIMENTS
  // ==============================
  {
    id: 'email_subject_question',
    principle: 'pattern_interrupt',
    title: 'Question Subject Line A/B Test',
    hypothesis:
      'If we use a question in the subject line, then open rates will increase by 20%',
    control: 'Current subject line format (statement-based)',
    variant:
      'Subject line as a direct question the recipient must answer mentally',
    success_metric: 'Email open rate (%)',
    sample_size: '500 emails (250 per variant)',
    duration_days: 7,
    action_steps: [
      'Export next 500 leads from CRM',
      'Write 3 question-based subject lines for your next campaign',
      'Set up A/B test in email tool (50/50 split)',
      'Send to both groups at same time',
      'Measure open rates after 48 hours',
    ],
    why: 'Questions create a cognitive loop that demands resolution, increasing curiosity.',
    allowed_channels: ['email'],
  },
  {
    id: 'email_plain_text',
    principle: 'pattern_interrupt',
    title: 'Plain Text vs HTML Email Test',
    hypothesis:
      'If we send plain text emails instead of designed HTML, then reply rates will increase by 30%',
    control: 'Current branded HTML email template',
    variant: 'Simple plain text email that looks like a personal message',
    success_metric: 'Reply rate (%)',
    sample_size: '400 emails (200 per variant)',
    duration_days: 7,
    action_steps: [
      'Create a plain text version of your next email (no images, no formatting)',
      'Keep it under 100 words',
      'Use a personal sender name, not company name',
      'Split list 50/50 and send both versions',
      'Track replies (not just opens) for each variant',
    ],
    why: 'Plain text feels personal and bypasses "marketing email" pattern recognition.',
    allowed_channels: ['email'],
  },
  {
    id: 'email_reply_cta',
    principle: 'friction',
    title: 'Reply CTA vs Link CTA Test',
    hypothesis:
      'If we ask for a reply instead of a click, then engagement will increase by 25%',
    control: 'Email with "Click here to learn more" CTA button',
    variant: 'Email with "Reply YES if interested" as the only CTA',
    success_metric: 'Engagement rate (replies + clicks combined)',
    sample_size: '600 emails (300 per variant)',
    duration_days: 5,
    action_steps: [
      'Remove all links from the variant email',
      'End with: "Reply with YES if you want me to send details"',
      'Set up auto-responder to send info when they reply YES',
      'Track both click-throughs and replies',
      'Calculate total engaged leads from each variant',
    ],
    why: 'Replying requires less commitment than clicking and signals higher intent.',
    allowed_channels: ['email'],
  },
  {
    id: 'email_short_vs_long',
    principle: 'friction',
    title: 'Short vs Long Email Copy Test',
    hypothesis:
      'If we cut email length to under 50 words, then click-through rate will increase by 15%',
    control: 'Current email (typically 150-300 words)',
    variant: 'Ultra-short email: 1 hook sentence, 1 value prop, 1 CTA',
    success_metric: 'Click-through rate (%)',
    sample_size: '800 emails (400 per variant)',
    duration_days: 7,
    action_steps: [
      'Take your next email and cut it to exactly 3 sentences',
      'Sentence 1: Hook (pain point or curiosity)',
      'Sentence 2: What you offer in 10 words',
      'Sentence 3: Clear CTA',
      'A/B test against your full-length version',
    ],
    why: 'Shorter emails respect reader time and have less friction to action.',
    allowed_channels: ['email'],
  },
  {
    id: 'email_personalization',
    principle: 'identity',
    title: 'Personalized Opening Line Test',
    hypothesis:
      'If we personalize the first line with company/role context, then reply rate will double',
    control: 'Generic opening ("Hope this finds you well...")',
    variant: 'First line references specific company detail or recent news',
    success_metric: 'Reply rate (%)',
    sample_size: '200 emails (100 per variant)',
    duration_days: 14,
    action_steps: [
      'Research 100 prospects (LinkedIn, company news, recent posts)',
      'Write a unique first line for each: "Saw you just [specific thing]..."',
      'Keep rest of email identical',
      'Send personalized batch vs generic batch',
      'Track reply rates and quality of replies',
    ],
    why: 'Personalization signals effort and triggers reciprocity.',
    allowed_channels: ['email', 'linkedin'],
  },

  // ==============================
  // LANDING PAGE EXPERIMENTS
  // ==============================
  {
    id: 'landing_cta_text',
    principle: 'friction',
    title: 'CTA Button Text A/B Test',
    hypothesis:
      'If we use value-focused CTA text instead of action text, conversion will increase by 20%',
    control: '"Sign Up" or "Get Started" button',
    variant: '"Get Your Free [Benefit]" or "See My Results" button',
    success_metric: 'Button click-through rate (%)',
    sample_size: '2000 visitors (1000 per variant)',
    duration_days: 14,
    action_steps: [
      'List 5 value-focused alternatives to your current CTA',
      'Pick the one that emphasizes the outcome, not the action',
      'Set up A/B test in your landing page tool',
      'Run test until statistical significance (min 1000 per variant)',
      'Implement winner site-wide',
    ],
    why: 'Value-focused CTAs answer "what do I get?" not "what do I do?"',
    allowed_channels: ['website'],
  },
  {
    id: 'landing_social_proof',
    principle: 'social_proof',
    title: 'Social Proof Placement Test',
    hypothesis:
      'If we add customer count above the fold, conversion will increase by 15%',
    control: 'Landing page without visible social proof above fold',
    variant: 'Add "Join 2,847 teams already using [Product]" near headline',
    success_metric: 'Page conversion rate (%)',
    sample_size: '3000 visitors (1500 per variant)',
    duration_days: 21,
    action_steps: [
      'Calculate your exact customer/user count',
      'Use a specific number (2,847 not "thousands")',
      'Add it directly below your headline',
      'Use a subtle but visible design',
      'A/B test placement: above fold vs below fold',
    ],
    why: 'Specific numbers are more credible and reduce perceived risk.',
    allowed_channels: ['website'],
  },
  {
    id: 'landing_form_fields',
    principle: 'friction',
    title: 'Form Field Reduction Test',
    hypothesis:
      'If we reduce form fields from 5+ to just email, conversion will increase by 40%',
    control: 'Current form (name, email, company, role, phone)',
    variant: 'Single email field only',
    success_metric: 'Form submission rate (%)',
    sample_size: '1500 visitors (750 per variant)',
    duration_days: 14,
    action_steps: [
      'Audit your current form: which fields are truly required?',
      'Create a variant with only email field',
      'Plan to collect other info in follow-up flow',
      'A/B test for 2 weeks',
      'Calculate cost per lead for each variant',
    ],
    why: 'Every additional form field reduces conversion by ~10%.',
    allowed_channels: ['website'],
  },
  {
    id: 'landing_headline_test',
    principle: 'loss_aversion',
    title: 'Pain vs Gain Headline Test',
    hypothesis:
      'If we lead with what they are losing instead of gaining, conversion will increase by 25%',
    control: 'Benefit-focused headline ("Get more leads...")',
    variant: 'Pain-focused headline ("Stop losing leads to...")',
    success_metric: 'Page conversion rate (%)',
    sample_size: '2000 visitors (1000 per variant)',
    duration_days: 14,
    action_steps: [
      'Rewrite your headline to emphasize what they are losing',
      'Use words like: "Stop", "Losing", "Missing", "Wasting"',
      'Keep the rest of page identical',
      'Run A/B test with even traffic split',
      'Measure conversion and time-on-page for each',
    ],
    why: 'Loss aversion is 2x stronger than gain motivation in decision-making.',
    allowed_channels: ['website'],
  },

  // ==============================
  // SOCIAL MEDIA EXPERIMENTS
  // ==============================
  {
    id: 'linkedin_hook_test',
    principle: 'pattern_interrupt',
    title: 'Controversial Hook vs Safe Hook Test',
    hypothesis:
      'If we open with a contrarian take, engagement will increase by 50%',
    control: 'Standard post opening (educational/helpful)',
    variant: 'Opening line challenges common industry belief',
    success_metric: 'Engagement rate (likes + comments / impressions)',
    sample_size: '5 posts each variant',
    duration_days: 30,
    action_steps: [
      'List 5 "common wisdoms" in your industry that you disagree with',
      'Write posts that open with "Unpopular opinion:" or "Everyone says X. They are wrong."',
      'Alternate between contrarian and safe posts',
      'Track engagement rate on each',
      'Double down on what works',
    ],
    why: 'Contrarian takes create cognitive dissonance that demands engagement.',
    allowed_channels: ['linkedin', 'twitter'],
  },
  {
    id: 'linkedin_carousel_test',
    principle: 'commitment',
    title: 'Carousel vs Text Post Test',
    hypothesis:
      'If we use carousel format instead of text-only, saves will increase by 3x',
    control: 'Text-only post with same content',
    variant: 'Carousel document with same content split into slides',
    success_metric: 'Save rate (saves / impressions)',
    sample_size: '10 posts (5 each format)',
    duration_days: 30,
    action_steps: [
      'Take your best-performing text post',
      'Convert it into a 7-10 slide carousel',
      'Slide 1: Hook question or bold statement',
      'Slides 2-8: One key point per slide',
      'Last slide: CTA to follow/save',
    ],
    why: 'Carousels increase dwell time and trigger completion bias.',
    allowed_channels: ['linkedin', 'instagram'],
  },
  {
    id: 'twitter_thread_test',
    principle: 'commitment',
    title: 'Thread vs Single Tweet Test',
    hypothesis:
      'If we post threads instead of singles, follower growth will increase by 40%',
    control: 'Single tweets throughout the week',
    variant: '2-3 long threads per week instead',
    success_metric: 'Follower growth rate (new followers / week)',
    sample_size: '4 weeks of posting',
    duration_days: 28,
    action_steps: [
      'Identify 3 topics you can expand into 10+ tweet threads',
      'Structure: Hook tweet → Value tweets → Summary → CTA to follow',
      'Post threads at peak engagement times (8-9am your audience timezone)',
      'Compare follower growth vs previous 4 weeks',
      'Track which thread topics perform best',
    ],
    why: 'Threads reward completion with accumulated value, building trust.',
    allowed_channels: ['twitter'],
  },

  // ==============================
  // AD EXPERIMENTS
  // ==============================
  {
    id: 'ad_ugly_creative',
    principle: 'pattern_interrupt',
    title: 'Ugly vs Polished Ad Creative Test',
    hypothesis: 'If we use lo-fi/ugly creative, CTR will increase by 30%',
    control: 'Professionally designed ad creative',
    variant: 'Screenshot-style or selfie-style "ugly" creative',
    success_metric: 'Click-through rate (CTR %)',
    sample_size: '$500 ad spend per variant',
    duration_days: 14,
    action_steps: [
      'Create a variant using iPhone screenshot style',
      'No professional design - make it look like a friend texted it',
      'Use same copy and targeting for both',
      'Split budget 50/50',
      'Compare CTR and CPA after $500 each',
    ],
    why: 'Native-looking content bypasses "ad blindness" in feeds.',
    allowed_channels: ['facebook', 'instagram', 'tiktok'],
  },
  {
    id: 'ad_video_vs_static',
    principle: 'pattern_interrupt',
    title: 'Video vs Static Image Ad Test',
    hypothesis:
      'If we use short video instead of static image, CPA will decrease by 20%',
    control: 'Static image ad with copy',
    variant: '15-30 second video ad with same message',
    success_metric: 'Cost per acquisition (CPA)',
    sample_size: '$1000 ad spend per variant',
    duration_days: 14,
    action_steps: [
      'Record a simple 15-second talking head video',
      'Same message as your static ad',
      'No fancy editing - authenticity over production',
      'Test against your best-performing static ad',
      'Compare CPA and total conversions',
    ],
    why: 'Video captures attention longer and builds trust faster.',
    allowed_channels: ['facebook', 'instagram', 'youtube', 'tiktok'],
  },

  // ==============================
  // PRICING/OFFER EXPERIMENTS
  // ==============================
  {
    id: 'pricing_anchor',
    principle: 'pricing_psych',
    title: 'Price Anchoring Test',
    hypothesis:
      'If we show higher "value" price before actual price, conversion will increase by 20%',
    control: 'Show price only ($99/mo)',
    variant: 'Show "Value: $499/mo" crossed out above "$99/mo"',
    success_metric: 'Checkout conversion rate (%)',
    sample_size: '500 visitors to pricing page',
    duration_days: 14,
    action_steps: [
      'Calculate the true value of your offering (time saved * hourly rate)',
      'Display that "value" prominently above actual price',
      'Use visual crossing out or "Compare at" language',
      'A/B test pricing page',
      'Track conversion rate and average order value',
    ],
    why: 'Anchoring sets expectations that make actual price feel like a deal.',
    allowed_channels: ['website'],
  },
  {
    id: 'pricing_decoy',
    principle: 'pricing_psych',
    title: 'Decoy Pricing Tier Test',
    hypothesis:
      'If we add a decoy middle tier, pro tier purchases will increase by 30%',
    control: 'Two tiers: Basic ($29) and Pro ($99)',
    variant: 'Three tiers: Basic ($29), Plus ($89), Pro ($99)',
    success_metric: 'Pro tier selection rate (%)',
    sample_size: '300 pricing page visitors',
    duration_days: 21,
    action_steps: [
      'Design a middle tier that is clearly worse value than Pro',
      'Price it close to Pro to make Pro look like better value',
      'Include ~70% of Pro features in middle tier',
      'A/B test the pricing table',
      'Track which tier gets selected in each variant',
    ],
    why: 'Decoy effect makes adjacent options look more attractive.',
    allowed_channels: ['website'],
  },

  // ==============================
  // REFERRAL EXPERIMENTS
  // ==============================
  {
    id: 'referral_double_sided',
    principle: 'social_proof',
    title: 'Double-Sided Referral Reward Test',
    hypothesis:
      'If both referrer and referee get rewards, referral rate will increase by 50%',
    control: 'Single-sided reward (referrer only gets benefit)',
    variant: 'Both parties get equal reward',
    success_metric: 'Referral conversion rate (%)',
    sample_size: '200 existing customers',
    duration_days: 30,
    action_steps: [
      'Design a reward valuable to both parties (discount, extra features)',
      'Email existing customers about the new program',
      'Make sharing frictionless (one-click share links)',
      'Track: shares, signups, conversions for each variant',
      'Calculate cost per acquired customer via referral',
    ],
    why: 'Double-sided rewards remove guilt from asking friends to sign up.',
    allowed_channels: ['email', 'website'],
  },
  {
    id: 'referral_waitlist',
    principle: 'loss_aversion',
    title: 'Viral Waitlist Position Test',
    hypothesis:
      'If we show waitlist position with share-to-jump, signups will increase by 3x',
    control: 'Standard waitlist (just collect email)',
    variant: 'Show position in line + "Share to jump ahead"',
    success_metric: 'Signups and shares per visitor',
    sample_size: '500 waitlist visitors',
    duration_days: 30,
    action_steps: [
      'Add position number to confirmation page (#4,821 in line)',
      'Add share buttons: "Move up 100 spots for each friend who joins"',
      'Track viral coefficient (signups per share)',
      'Compare total signups vs control period',
      'Measure quality of referred users after launch',
    ],
    why: 'Position anxiety + achievable goal creates sharing urgency.',
    allowed_channels: ['website'],
  },
];

export const CONSTRAINTS: ConstraintTemplate[] = [
  // Safe
  { id: 'short_length', description: 'Under 100 words', risk_level: 'safe' },
  { id: 'clear_cta', description: 'Single clear CTA', risk_level: 'safe' },
  {
    id: 'professional_tone',
    description: 'Professional tone',
    risk_level: 'safe',
  },
  { id: 'data_backed', description: 'Include a statistic', risk_level: 'safe' },

  // Spicy
  { id: 'no_links', description: 'No hyperlinks allowed', risk_level: 'spicy' },
  {
    id: 'contrarian_hook',
    description: 'Contrarian opener',
    risk_level: 'spicy',
  },
  {
    id: 'visual_pattern_interrupt',
    description: 'Visual pattern interrupt',
    risk_level: 'spicy',
  },
  {
    id: 'emoji_subject',
    description: 'Single emoji subject line',
    risk_level: 'spicy',
  },
  {
    id: 'question_only',
    description: 'Subject is just a question',
    risk_level: 'spicy',
  },
  {
    id: 'lowercase_subject',
    description: 'All lowercase subject',
    risk_level: 'spicy',
  },

  // Unreasonable
  {
    id: 'anti_selling',
    description: 'Anti-selling framing',
    risk_level: 'unreasonable',
  },
  {
    id: 'confession',
    description: 'Embarrassing confession',
    risk_level: 'unreasonable',
  },
  {
    id: 'typo_human',
    description: 'Deliberate typo/lowercase',
    risk_level: 'unreasonable',
  },
  {
    id: 'aggressive_filter',
    description: 'Aggressively filter out prospects',
    risk_level: 'unreasonable',
  },
  {
    id: 'ugly_design',
    description: 'Deliberately ugly design',
    risk_level: 'unreasonable',
  },
  {
    id: 'no_branding',
    description: 'Zero branding/logo',
    risk_level: 'unreasonable',
  },
];

export const CHANNEL_DEFAULTS: Record<
  ChannelType,
  { effort: '10m' | '30m' | '2h'; time_to_signal: '24h' | '48h' | '7d' }
> = {
  email: { effort: '30m', time_to_signal: '24h' },
  linkedin: { effort: '30m', time_to_signal: '24h' },
  twitter: { effort: '10m', time_to_signal: '24h' },
  instagram: { effort: '30m', time_to_signal: '48h' },
  tiktok: { effort: '30m', time_to_signal: '48h' },
  youtube: { effort: '2h', time_to_signal: '7d' },
  facebook: { effort: '30m', time_to_signal: '48h' },
  google_ads: { effort: '2h', time_to_signal: '7d' },
  website: { effort: '2h', time_to_signal: '7d' },
  blog: { effort: '2h', time_to_signal: '7d' },
  podcast: { effort: '2h', time_to_signal: '7d' },
  other: { effort: '30m', time_to_signal: '48h' },
};

// Autocomplete suggestions for "Other" channel
export const CHANNEL_SUGGESTIONS: string[] = [
  'WhatsApp',
  'Slack',
  'Discord',
  'Telegram',
  'SMS',
  'Push Notifications',
  'Reddit',
  'Quora',
  'Medium',
  'Substack',
  'Newsletter',
  'Product Hunt',
  'Hacker News',
  'Indie Hackers',
  'Dev.to',
  'Pinterest',
  'Snapchat',
  'Clubhouse',
  'Twitch',
  'Spotify Ads',
  'Apple Podcasts',
  'Webinar',
  'Conference',
  'Meetup',
  'Direct Mail',
  'Billboard',
  'Radio',
  'Print Magazine',
  'Newspaper',
  'TV',
  'Cinema',
  'Influencer Partnership',
  'Affiliate',
  'Partnership',
  'Co-marketing',
  'Guest Post',
  'Press Release',
  'Review Sites',
  'G2',
  'Capterra',
  'Trustpilot',
  'App Store',
  'Play Store',
  'Chrome Web Store',
  'Marketplace',
  'Yelp',
  'Google Business',
  'LinkedIn Ads',
  'Twitter Ads',
  'Programmatic',
  'Native Ads',
  'Sponsored Content',
  'Trade Show',
];
