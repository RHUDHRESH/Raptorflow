/**
 * Footer navigation configuration
 * Central config for all footer links used across the landing page
 */

export interface FooterLinkItem {
    name: string
    href: string
    external?: boolean
}

export interface SocialLinkItem {
    icon: 'twitter' | 'linkedin' | 'github'
    href: string
    label: string
    color: string
}

export const FOOTER_LINKS = {
    product: [
        { name: 'Features', href: '/#features' },
        { name: 'Pricing', href: '/pricing' },
        { name: 'Manifesto', href: '/manifesto' },
        { name: 'Changelog', href: '/changelog' },
        { name: 'Status', href: '/status', external: true },
    ] as FooterLinkItem[],

    company: [
        { name: 'About', href: '/about' },
        { name: 'Blog', href: '/blog' },
        { name: 'Careers', href: '/careers' },
        { name: 'Contact', href: '/contact' },
    ] as FooterLinkItem[],

    legal: [
        { name: 'Privacy', href: '/privacy' },
        { name: 'Terms', href: '/terms' },
        { name: 'Refunds', href: '/refunds' },
        { name: 'Cookies', href: '/cookies' },
    ] as FooterLinkItem[],
}

export const SOCIAL_LINKS: SocialLinkItem[] = [
    {
        icon: 'twitter',
        href: 'https://x.com/raptorflow',
        label: 'X / Twitter',
        color: 'from-sky-500 to-blue-600'
    },
    {
        icon: 'linkedin',
        href: 'https://linkedin.com/company/raptorflow',
        label: 'LinkedIn',
        color: 'from-blue-600 to-blue-800'
    },
    {
        icon: 'github',
        href: 'https://github.com/raptorflow',
        label: 'GitHub',
        color: 'from-gray-700 to-gray-900'
    },
]

export const BRAND_INFO = {
    name: 'RaptorFlow',
    tagline: 'Marketing OS for founders',
    description: 'The AI-first marketing operating system. Build campaigns, generate content, and ship daily—all in one place.',
    email: 'hello@raptorflow.com',
    country: 'India',
}
