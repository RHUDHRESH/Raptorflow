import {
  Target,
  Shield,
  Zap,
  TrendingUp,
  Users,
  Brain,
  Rocket,
  BarChart3,
  Layers,
  FileText,
  Lock,
  Mail,
  Download,
  ClipboardList,
  AlertCircle
} from 'lucide-react';

export const HERO_CONTENT = {
  eyebrow: "The Art of Strategy",
  headline: "Marketing As Mastery.",
  subtitle: "Chaos is a choice. Order is a discipline. RaptorFlow transforms the noise of daily operations into a masterpiece of strategic clarity.",
  cta_primary: "Ignite System",
  cta_secondary: "Explore Demo",
  stats: [
    { label: 'Less Busywork', description: 'Focus on strategy, not endless tasks' },
    { label: 'Faster Execution', description: 'From idea to action in minutes' },
    { label: 'Total Clarity', description: 'Know exactly what to do next' }
  ]
};

export const CONSTRAINTS_CONTENT = {
  title: "Most Marketing Tools\nLet You Do Everything",
  subtitle: "Less choice. More done.",
  cards: [
    { number: "7", label: "Cohorts", sublabel: "Maximum active groups" },
    { number: "3", label: "Moves", sublabel: "Per week limit" },
    { number: "3", label: "Actions", sublabel: "Daily focus items" }
  ]
};

export const FEATURES_CONTENT = {
  title: "Everything You Need.\nNothing You Don't.",
  subtitle: "Stop guessing and start shipping marketing that makes sense",
  items: [
    {
      number: '01',
      title: 'Define',
      subtitle: 'Your Real Buyers',
      desc: 'Cohort builder that captures who they are, what they struggle with, and how you help. No more vague "target audiences."',
      icon: Target,
      features: ['ICP cohorts', 'Microproofs', 'Real language']
    },
    {
      number: '02',
      title: 'Plan',
      subtitle: 'Strategic Moves',
      desc: 'Campaign planner that turns ideas into finishable work. 1-3 moves per week, each with clear objectives and posture.',
      icon: Brain,
      features: ['Weekly moves', 'Daily actions', 'Brain dump tool']
    },
    {
      number: '03',
      title: 'Ship',
      subtitle: 'Track Progress',
      desc: 'See what\'s working without vanity metrics. Track posture mix, cadence streaks, and what actually drives growth.',
      icon: TrendingUp,
      features: ['Real analytics', 'Tone guardian', 'Team sync']
    }
  ]
};

export const SYSTEM_CONTENT = {
  title: "Everything You Need.\nNothing You Don't.",
  description: "A complete marketing command center designed for teams who want results, not busywork.",
  grid: [
    {
      icon: Target,
      title: 'Smart Cohorts',
      description: 'Define rare audiences with microproofs, objections, and language your buyers actually use.',
      metric: '3-7 cohorts',
      color: 'from-gray-900 to-black'
    },
    {
      icon: Brain,
      title: 'Strategic Moves',
      description: 'Plan operations with posture-aware pacing. Offensive when hot, defensive when protecting altitude.',
      metric: '1-3 weekly moves',
      color: 'from-black to-gray-800'
    },
    {
      icon: Zap,
      title: 'Daily Actions',
      description: 'Execute with focus. Time-boxed tasks that actually move the needle, not busywork.',
      metric: '3 actions/day',
      color: 'from-gray-800 to-gray-900'
    },
    {
      icon: Shield,
      title: 'Tone Guardian',
      description: 'AI sentinel that flags drift, fatigue, and cadence gaps without adding another inbox.',
      metric: '0 tone leaks',
      color: 'from-gray-900 to-black'
    },
    {
      icon: BarChart3,
      title: 'Real Analytics',
      description: 'Track what matters. Posture mix, cadence streaks, and alert count. No vanity metrics.',
      metric: 'Signal only',
      color: 'from-black to-gray-800'
    },
    {
      icon: Layers,
      title: 'Team Sync',
      description: 'Keep everyone aligned with clear ownership, binary status, and exportable recaps.',
      metric: 'One source',
      color: 'from-gray-800 to-gray-900'
    }
  ]
};

export const WEEKLY_RHYTHM_CONTENT = {
  title: "Seven Days of\nCalm Execution",
  description: "A proven weekly cadence that turns marketing chaos into a sustainable, finishable system.",
  steps: [
    { day: 'Monday', label: 'Brain Dump', desc: 'Offload the week in 10 minutes. System labels intent, risk, and effort automatically.', num: '01' },
    { day: 'Tuesday', label: 'Cohort Refresh', desc: 'Update microproofs, objections, and language from the week\'s calls and conversations.', num: '02' },
    { day: 'Wednesday', label: 'Lock Moves', desc: 'Choose 1-3 strategic moves. Each gets a finish line, owner, and posture assignment.', num: '03' },
    { day: 'Thursday', label: 'Daily Actions', desc: 'Bite-sized, time-boxed tasks. Ship, log, move on. No endless lists.', num: '04' },
    { day: 'Friday', label: 'Sentinel Review', desc: 'Resolve tone leaks, cadence gaps, and fatigue flags before they compound.', num: '05' },
    { day: 'Saturday', label: 'Weekly Recap', desc: 'One-page summary. Exportable. Board-ready. No slides needed.', num: '06' },
    { day: 'Sunday', label: 'Reset', desc: 'Carry only what matters into the next sprint. Archive the rest.', num: '07' }
  ]
};

export const DELIVERABLES_CONTENT = {
  title: "What Leaves\nThe Room",
  items: [
    {
      icon: FileText,
      title: 'Runway Brief',
      desc: 'Single page. Cohorts, objective, posture, and three moves. Made to send, not to present.',
      features: ['PDF export', 'Markdown copy', 'Print-ready']
    },
    {
      icon: ClipboardList,
      title: 'Cadence Log',
      desc: 'Daily actions with timestamps and outcomes. Receipts without the bloat.',
      features: ['Action history', 'Time tracking', 'Owner logs']
    },
    {
      icon: AlertCircle,
      title: 'Signals Board',
      desc: 'Tone leaks, fatigue, risks, and callouts. Only when action is required.',
      features: ['Alert summary', 'Risk flags', 'Trend analysis']
    }
  ]
};

export const TRUST_CONTENT = {
  title: "Your Data, Your Control",
  items: [
    {
      icon: Lock,
      title: 'Privacy First',
      desc: 'Your data stays yours. We store in Supabase. No public feeds, no surprise sharing.',
      animationType: 'lock'
    },
    {
      icon: Mail,
      title: 'Human Support',
      desc: 'Real people, not bots. Response inside business hours. support@raptorflow.in',
      animationType: 'mail'
    },
    {
      icon: Download,
      title: 'Export Everything',
      desc: 'PDF, Markdown, JSON. Your data is portable. Leave anytime with everything intact.',
      animationType: 'download'
    }
  ]
};

export const USE_CASES_CONTENT = {
  title: "Your Team,\nYour Way",
  subtitle: "Whether you're flying solo or leading a team, RaptorFlow adapts to your workflow",
  cases: [
    {
      title: 'Solo Founders',
      icon: Users,
      tagline: 'You wear all the hats. RaptorFlow gives you a marketing system that doesn\'t require a team.',
      benefits: [
        'Quick setup (< 1 hour)',
        'No learning curve',
        'Scales with you'
      ],
      cta: 'Start Free',
      link: '/register'
    },
    {
      title: 'Lean Marketing Teams',
      icon: Shield,
      tagline: 'Small team, big ambitions. Stay aligned without endless meetings and status updates.',
      benefits: [
        'Clear ownership',
        'Async-friendly',
        'No tool sprawl'
      ],
      cta: 'Start Free',
      link: '/register'
    },
    {
      title: 'Agencies',
      icon: Rocket,
      tagline: 'Manage multiple clients with consistent quality. Export briefs and recaps in seconds.',
      benefits: [
        'Client-ready exports',
        'Template library',
        'White-label ready'
      ],
      cta: 'Start Free',
      link: '/register'
    },
    {
      title: 'Product Teams',
      icon: Brain,
      tagline: 'Launch features with clarity. Define cohorts, plan moves, track what resonates.',
      benefits: [
        'Launch playbooks',
        'Feature adoption',
        'User feedback loops'
      ],
      cta: 'Start Free',
      link: '/register'
    }
  ]
};

export const PRICING_CONTENT = {
  title: "Simple, Honest Pricing",
  subtitle: "Choose your altitude. Scale as you grow.",
  footer: "Annual plans: 2 months free • Monthly billing • Cancel anytime"
};

export const FAQ_CONTENT = {
  title: "Straight Answers",
  items: [
    {
      q: 'Is this another content calendar?',
      a: 'No. We start with cohorts and postures, then map moves to daily actions. The calendar is an output, not the product.'
    },
    {
      q: 'How long to get value?',
      a: 'Most teams see clarity after the first sprint (one week). The intake takes under an hour, including cohorts.'
    },
    {
      q: 'Who is it for?',
      a: 'Solo founders, lean teams, and agencies who want fewer tasks with higher signal. If you hate guru theatrics, you will like this.'
    },
    {
      q: 'Do you lock me in?',
      a: 'No. Monthly billing. Export everything at any time. Your data is yours.'
    },
    {
      q: 'What makes RaptorFlow different?',
      a: 'We enforce constraints: 3-7 cohorts, 1-3 moves per week, 3 actions per day. Constraints create clarity. Most tools let you do everything, which means you finish nothing.'
    },
    {
      q: 'Can I use this with my existing tools?',
      a: 'Yes. RaptorFlow is your strategy layer. Export briefs to Notion, actions to Asana, or recaps to Slack. We play nice with others.'
    },
    {
      q: 'What about AI features?',
      a: 'AI helps with tone consistency (Sentinel), cohort suggestions, and move prioritization. But you stay in control. No auto-posting, no black boxes.'
    },
    {
      q: 'What\'s the difference between tiers?',
      a: 'Ascent is for one brand, Glide for multiple plays, Soar for agencies/multi-brand. Each tier unlocks more cohorts, moves, analytics depth, and team seats.'
    }
  ]
};
