'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

/**
 * Sidebar — Following COMPONENTS.md spec exactly
 * 
 * Width: 220px
 * Background: var(--color-surface)
 * Border-right: 1px solid var(--color-border-subtle)
 * Max 10 items
 */

const navItems = [
    { name: 'Dashboard', href: '/' },
    { name: 'Foundation', href: '/foundation' },
    { name: 'Cohorts', href: '/cohorts' },
    { name: 'Moves', href: '/moves' },
    { name: 'Campaigns', href: '/campaigns' },
    { name: 'Muse', href: '/muse' },
    { name: 'Matrix', href: '/matrix' },
    { name: 'Blackbox', href: '/blackbox' },
];

const bottomItems = [
    { name: 'Settings', href: '/settings' },
];

export function Sidebar() {
    const pathname = usePathname();

    return (
        <aside style={{
            width: 'var(--sidebar-width)',
            height: '100vh',
            position: 'fixed',
            left: 0,
            top: 0,
            background: 'var(--color-surface)',
            borderRight: '1px solid var(--color-border-subtle)',
            display: 'flex',
            flexDirection: 'column',
            padding: '20px 12px',
            zIndex: 50,
        }}>
            {/* Logo */}
            <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: '0 12px',
                marginBottom: '32px'
            }}>
                <div style={{
                    width: '32px',
                    height: '32px',
                    borderRadius: 'var(--radius-md)',
                    background: 'var(--color-ink)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#FFFFFF',
                    fontSize: '14px',
                    fontWeight: 'var(--font-semibold)',
                }}>
                    RF
                </div>
                <span style={{
                    fontWeight: 'var(--font-semibold)',
                    fontSize: '18px',
                    letterSpacing: '-0.01em'
                }}>
                    RaptorFlow
                </span>
            </div>

            {/* Navigation */}
            <nav style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                <ul style={{ listStyle: 'none', margin: 0, padding: 0 }}>
                    {navItems.map((item) => (
                        <li key={item.href}>
                            <Link
                                href={item.href}
                                style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    height: '40px',
                                    padding: '0 12px',
                                    borderRadius: 'var(--radius-md)',
                                    fontSize: 'var(--text-sm)',
                                    fontWeight: 'var(--font-medium)',
                                    color: pathname === item.href ? '#FFFFFF' : 'var(--color-muted)',
                                    background: pathname === item.href ? 'var(--color-ink)' : 'transparent',
                                    textDecoration: 'none',
                                    transition: 'all var(--duration-normal) var(--easing)',
                                }}
                                onMouseEnter={(e) => {
                                    if (pathname !== item.href) {
                                        e.currentTarget.style.background = 'var(--color-border-subtle)';
                                        e.currentTarget.style.color = 'var(--color-ink)';
                                    }
                                }}
                                onMouseLeave={(e) => {
                                    if (pathname !== item.href) {
                                        e.currentTarget.style.background = 'transparent';
                                        e.currentTarget.style.color = 'var(--color-muted)';
                                    }
                                }}
                            >
                                {item.name}
                            </Link>
                        </li>
                    ))}
                </ul>

                {/* Bottom items */}
                <div style={{ marginTop: 'auto' }}>
                    <div style={{
                        height: '1px',
                        background: 'var(--color-border-subtle)',
                        margin: '16px 12px'
                    }} />
                    <ul style={{ listStyle: 'none', margin: 0, padding: 0 }}>
                        {bottomItems.map((item) => (
                            <li key={item.href}>
                                <Link
                                    href={item.href}
                                    style={{
                                        display: 'flex',
                                        alignItems: 'center',
                                        height: '40px',
                                        padding: '0 12px',
                                        borderRadius: 'var(--radius-md)',
                                        fontSize: 'var(--text-sm)',
                                        fontWeight: 'var(--font-medium)',
                                        color: pathname === item.href ? '#FFFFFF' : 'var(--color-muted)',
                                        background: pathname === item.href ? 'var(--color-ink)' : 'transparent',
                                        textDecoration: 'none',
                                        transition: 'all var(--duration-normal) var(--easing)',
                                    }}
                                    onMouseEnter={(e) => {
                                        if (pathname !== item.href) {
                                            e.currentTarget.style.background = 'var(--color-border-subtle)';
                                            e.currentTarget.style.color = 'var(--color-ink)';
                                        }
                                    }}
                                    onMouseLeave={(e) => {
                                        if (pathname !== item.href) {
                                            e.currentTarget.style.background = 'transparent';
                                            e.currentTarget.style.color = 'var(--color-muted)';
                                        }
                                    }}
                                >
                                    {item.name}
                                </Link>
                            </li>
                        ))}
                    </ul>
                </div>
            </nav>
        </aside>
    );
}
