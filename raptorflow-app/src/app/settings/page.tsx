'use client';

import React, { useState } from 'react';
import { AppLayout } from '@/components/layout/AppLayout';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import styles from './settings.module.css';

type SettingsSection =
    | 'profile'
    | 'workspace'
    | 'team'
    | 'appearance'
    | 'notifications'
    | 'integrations'
    | 'developers'
    | 'billing';

const SECTIONS: { id: SettingsSection; label: string; icon: React.ReactNode }[] = [
    { id: 'profile', label: 'Profile', icon: <UserIcon /> },
    { id: 'workspace', label: 'Workspace', icon: <WorkspaceIcon /> },
    { id: 'team', label: 'Team', icon: <TeamIcon /> },
    { id: 'appearance', label: 'Appearance', icon: <AppearanceIcon /> },
    { id: 'notifications', label: 'Notifications', icon: <BellIcon /> },
    { id: 'integrations', label: 'Integrations', icon: <IntegrationsIcon /> },
    { id: 'developers', label: 'API & Developers', icon: <CodeIcon /> },
    { id: 'billing', label: 'Billing', icon: <BillingIcon /> },
];

export default function SettingsPage() {
    const [activeSection, setActiveSection] = useState<SettingsSection>('profile');
    const [theme, setTheme] = useState<'light' | 'dark' | 'system'>('system');
    const [notifications, setNotifications] = useState({
        moveReminders: true,
        weeklyDigest: true,
        campaignAlerts: true,
        productUpdates: false,
    });

    const renderSection = () => {
        switch (activeSection) {
            case 'profile':
                return <ProfileSection />;
            case 'workspace':
                return <WorkspaceSection />;
            case 'team':
                return <TeamSection />;
            case 'appearance':
                return <AppearanceSection theme={theme} setTheme={setTheme} />;
            case 'notifications':
                return <NotificationsSection notifications={notifications} setNotifications={setNotifications} />;
            case 'integrations':
                return <IntegrationsSection />;
            case 'developers':
                return <DevelopersSection />;
            case 'billing':
                return <BillingSection />;
            default:
                return null;
        }
    };

    return (
        <AppLayout>
            <div className={styles.container}>
                <header className={styles.header}>
                    <h1 className={styles.title}>Settings</h1>
                </header>

                <div className={styles.layout}>
                    <nav className={styles.nav}>
                        {SECTIONS.map((section) => (
                            <button
                                key={section.id}
                                className={`${styles.navItem} ${activeSection === section.id ? styles.active : ''}`}
                                onClick={() => setActiveSection(section.id)}
                            >
                                <span className={styles.navIcon}>{section.icon}</span>
                                <span className={styles.navLabel}>{section.label}</span>
                            </button>
                        ))}
                    </nav>

                    <main className={styles.content}>
                        {renderSection()}
                    </main>
                </div>
            </div>
        </AppLayout>
    );
}

// ============================================
// Section Components
// ============================================

function ProfileSection() {
    return (
        <div className={styles.section}>
            <div className={styles.sectionHeader}>
                <h2 className={styles.sectionTitle}>Profile</h2>
                <p className={styles.sectionDescription}>Your personal account details.</p>
            </div>

            {/* Avatar + Name Row */}
            <div className={styles.card}>
                <div className={styles.profileRow}>
                    <div className={styles.avatar}>JF</div>
                    <div className={styles.profileInfo}>
                        <span className={styles.profileName}>John Founder</span>
                        <span className={styles.profileEmail}>john@acme.com</span>
                    </div>
                    <Button variant="secondary" size="sm">Change Photo</Button>
                </div>
            </div>

            {/* Account Details */}
            <div className={styles.card}>
                <h3 className={styles.cardTitle}>Account</h3>
                <div className={styles.fieldGrid}>
                    <div className={styles.field}>
                        <label className={styles.label}>Full Name</label>
                        <input type="text" className={styles.input} defaultValue="John Founder" />
                    </div>
                    <div className={styles.field}>
                        <label className={styles.label}>Email</label>
                        <input type="email" className={styles.input} defaultValue="john@acme.com" />
                    </div>
                    <div className={styles.field}>
                        <label className={styles.label}>Role</label>
                        <input type="text" className={styles.input} defaultValue="Founder & CEO" />
                    </div>
                    <div className={styles.field}>
                        <label className={styles.label}>Timezone</label>
                        <select className={styles.input}>
                            <option>Asia/Kolkata (IST)</option>
                            <option>America/New_York (EST)</option>
                            <option>Europe/London (GMT)</option>
                        </select>
                    </div>
                </div>
                <div className={styles.cardActions}>
                    <Button variant="default" size="sm">Save Changes</Button>
                </div>
            </div>

            {/* Security */}
            <div className={styles.card}>
                <h3 className={styles.cardTitle}>Security</h3>
                <div className={styles.securityRow}>
                    <div>
                        <span className={styles.securityLabel}>Password</span>
                        <span className={styles.securityMeta}>Last changed 3 months ago</span>
                    </div>
                    <Button variant="secondary" size="sm">Change Password</Button>
                </div>
                <div className={styles.securityRow}>
                    <div>
                        <span className={styles.securityLabel}>Two-Factor Authentication</span>
                        <span className={styles.securityMeta}>Not enabled</span>
                    </div>
                    <Button variant="secondary" size="sm">Enable 2FA</Button>
                </div>
                <div className={styles.securityRow}>
                    <div>
                        <span className={styles.securityLabel}>Active Sessions</span>
                        <span className={styles.securityMeta}>2 devices</span>
                    </div>
                    <Button variant="ghost" size="sm">Manage</Button>
                </div>
            </div>
        </div>
    );
}

function WorkspaceSection() {
    return (
        <div className={styles.section}>
            <div className={styles.sectionHeader}>
                <h2 className={styles.sectionTitle}>Workspace</h2>
                <p className={styles.sectionDescription}>Manage your workspace settings and foundation.</p>
            </div>

            {/* Workspace Info */}
            <div className={styles.card}>
                <h3 className={styles.cardTitle}>Workspace Details</h3>
                <div className={styles.fieldGrid}>
                    <div className={styles.field}>
                        <label className={styles.label}>Workspace Name</label>
                        <input type="text" className={styles.input} defaultValue="Acme Corp" />
                    </div>
                    <div className={styles.field}>
                        <label className={styles.label}>Workspace URL</label>
                        <div className={styles.inputPrefix}>
                            <span>raptorflow.com/</span>
                            <input type="text" defaultValue="acme" />
                        </div>
                    </div>
                </div>
                <div className={styles.cardActions}>
                    <Button variant="default" size="sm">Update</Button>
                </div>
            </div>

            {/* Foundation Summary */}
            <div className={styles.card}>
                <div className={styles.cardHeader}>
                    <h3 className={styles.cardTitle}>Marketing Foundation</h3>
                    <span className={styles.badge}>Active</span>
                </div>
                <div className={styles.statsRow}>
                    <div className={styles.stat}>
                        <span className={styles.statValue}>SaaS B2B</span>
                        <span className={styles.statLabel}>Industry</span>
                    </div>
                    <div className={styles.stat}>
                        <span className={styles.statValue}>Early Stage</span>
                        <span className={styles.statLabel}>Stage</span>
                    </div>
                    <div className={styles.stat}>
                        <span className={styles.statValue}>Today</span>
                        <span className={styles.statLabel}>Last Updated</span>
                    </div>
                </div>
                <div className={styles.cardActions}>
                    <Link href="/foundation">
                        <Button variant="default" size="sm">Edit Foundation</Button>
                    </Link>
                </div>
            </div>

            {/* Danger Zone */}
            <div className={styles.dangerCard}>
                <h3 className={styles.cardTitle}>Danger Zone</h3>
                <div className={styles.dangerRow}>
                    <div>
                        <span className={styles.dangerLabel}>Transfer Ownership</span>
                        <span className={styles.dangerMeta}>Transfer this workspace to another user</span>
                    </div>
                    <Button variant="secondary" size="sm">Transfer</Button>
                </div>
                <div className={styles.dangerRow}>
                    <div>
                        <span className={styles.dangerLabel}>Delete Workspace</span>
                        <span className={styles.dangerMeta}>Permanently delete this workspace and all data</span>
                    </div>
                    <Button variant="destructive" size="sm">Delete</Button>
                </div>
            </div>
        </div>
    );
}

function TeamSection() {
    const teamMembers = [
        { name: 'John Founder', email: 'john@acme.com', role: 'Owner', avatar: 'JF' },
        { name: 'Sarah Marketing', email: 'sarah@acme.com', role: 'Admin', avatar: 'SM' },
        { name: 'Mike Developer', email: 'mike@acme.com', role: 'Member', avatar: 'MD' },
    ];

    return (
        <div className={styles.section}>
            <div className={styles.sectionHeader}>
                <h2 className={styles.sectionTitle}>Team</h2>
                <Button variant="default" size="sm">Invite Member</Button>
            </div>

            <div className={styles.card}>
                <div className={styles.teamList}>
                    {teamMembers.map((member, i) => (
                        <div key={i} className={styles.teamRow}>
                            <div className={styles.avatarSmall}>{member.avatar}</div>
                            <div className={styles.teamInfo}>
                                <span className={styles.teamName}>{member.name}</span>
                                <span className={styles.teamEmail}>{member.email}</span>
                            </div>
                            <span className={styles.roleBadge}>{member.role}</span>
                            <button className={styles.moreBtn}>•••</button>
                        </div>
                    ))}
                </div>
            </div>

            {/* Pending Invites */}
            <div className={styles.card}>
                <h3 className={styles.cardTitle}>Pending Invitations</h3>
                <div className={styles.emptyState}>
                    <span>No pending invitations</span>
                </div>
            </div>
        </div>
    );
}

function AppearanceSection({
    theme,
    setTheme
}: {
    theme: 'light' | 'dark' | 'system';
    setTheme: (t: 'light' | 'dark' | 'system') => void;
}) {
    return (
        <div className={styles.section}>
            <div className={styles.sectionHeader}>
                <h2 className={styles.sectionTitle}>Appearance</h2>
                <p className={styles.sectionDescription}>Customize your interface.</p>
            </div>

            <div className={styles.card}>
                <h3 className={styles.cardTitle}>Theme</h3>
                <div className={styles.themeGrid}>
                    {(['light', 'dark', 'system'] as const).map((option) => (
                        <button
                            key={option}
                            className={`${styles.themeCard} ${theme === option ? styles.selected : ''}`}
                            onClick={() => setTheme(option)}
                        >
                            <span className={styles.themeIcon}>
                                {option === 'light' && <SunIcon />}
                                {option === 'dark' && <MoonIcon />}
                                {option === 'system' && <SystemIcon />}
                            </span>
                            <span className={styles.themeLabel}>
                                {option.charAt(0).toUpperCase() + option.slice(1)}
                            </span>
                        </button>
                    ))}
                </div>
            </div>

            <div className={styles.card}>
                <h3 className={styles.cardTitle}>Display</h3>
                <div className={styles.optionRow}>
                    <div>
                        <span className={styles.optionLabel}>Compact Mode</span>
                        <span className={styles.optionMeta}>Reduce spacing for denser UI</span>
                    </div>
                    <Toggle checked={false} onChange={() => { }} />
                </div>
                <div className={styles.optionRow}>
                    <div>
                        <span className={styles.optionLabel}>Reduced Motion</span>
                        <span className={styles.optionMeta}>Minimize animations</span>
                    </div>
                    <Toggle checked={false} onChange={() => { }} />
                </div>
            </div>
        </div>
    );
}

function NotificationsSection({
    notifications,
    setNotifications
}: {
    notifications: {
        moveReminders: boolean;
        weeklyDigest: boolean;
        campaignAlerts: boolean;
        productUpdates: boolean;
    };
    setNotifications: React.Dispatch<React.SetStateAction<{
        moveReminders: boolean;
        weeklyDigest: boolean;
        campaignAlerts: boolean;
        productUpdates: boolean;
    }>>;
}) {
    const toggle = (key: keyof typeof notifications) => {
        setNotifications(prev => ({ ...prev, [key]: !prev[key] }));
    };

    return (
        <div className={styles.section}>
            <div className={styles.sectionHeader}>
                <h2 className={styles.sectionTitle}>Notifications</h2>
                <p className={styles.sectionDescription}>Control your notification preferences.</p>
            </div>

            <div className={styles.card}>
                <h3 className={styles.cardTitle}>Email</h3>
                <div className={styles.optionRow}>
                    <div>
                        <span className={styles.optionLabel}>Move Reminders</span>
                        <span className={styles.optionMeta}>Reminders for upcoming moves</span>
                    </div>
                    <Toggle checked={notifications.moveReminders} onChange={() => toggle('moveReminders')} />
                </div>
                <div className={styles.optionRow}>
                    <div>
                        <span className={styles.optionLabel}>Weekly Digest</span>
                        <span className={styles.optionMeta}>Weekly progress summary</span>
                    </div>
                    <Toggle checked={notifications.weeklyDigest} onChange={() => toggle('weeklyDigest')} />
                </div>
                <div className={styles.optionRow}>
                    <div>
                        <span className={styles.optionLabel}>Campaign Alerts</span>
                        <span className={styles.optionMeta}>Alerts for campaigns needing attention</span>
                    </div>
                    <Toggle checked={notifications.campaignAlerts} onChange={() => toggle('campaignAlerts')} />
                </div>
                <div className={styles.optionRow}>
                    <div>
                        <span className={styles.optionLabel}>Product Updates</span>
                        <span className={styles.optionMeta}>New features and improvements</span>
                    </div>
                    <Toggle checked={notifications.productUpdates} onChange={() => toggle('productUpdates')} />
                </div>
            </div>
        </div>
    );
}

function IntegrationsSection() {
    const integrations = [
        { name: 'LinkedIn', desc: 'Publish directly', connected: true, icon: 'Li' },
        { name: 'Twitter/X', desc: 'Schedule posts', connected: false, icon: 'X' },
        { name: 'Slack', desc: 'Get notifications', connected: true, icon: 'Sl' },
        { name: 'HubSpot', desc: 'Sync contacts', connected: false, icon: 'Hs' },
        { name: 'Google Analytics', desc: 'Track performance', connected: false, icon: 'GA' },
        { name: 'Zapier', desc: 'Connect 5000+ apps', connected: false, icon: 'Z' },
    ];

    return (
        <div className={styles.section}>
            <div className={styles.sectionHeader}>
                <h2 className={styles.sectionTitle}>Integrations</h2>
                <p className={styles.sectionDescription}>Connect your tools.</p>
            </div>

            <div className={styles.integrationsGrid}>
                {integrations.map((int, i) => (
                    <div key={i} className={styles.integrationCard}>
                        <div className={styles.integrationIcon}>{int.icon}</div>
                        <div className={styles.integrationInfo}>
                            <span className={styles.integrationName}>{int.name}</span>
                            <span className={styles.integrationDesc}>{int.desc}</span>
                        </div>
                        {int.connected ? (
                            <span className={styles.connectedBadge}>Connected</span>
                        ) : (
                            <Button variant="secondary" size="sm">Connect</Button>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
}

function DevelopersSection() {
    const [showKey, setShowKey] = useState(false);
    const apiKey = 'rf_live_sk_1a2b3c4d5e6f7g8h9i0j';

    return (
        <div className={styles.section}>
            <div className={styles.sectionHeader}>
                <h2 className={styles.sectionTitle}>API & Developers</h2>
                <p className={styles.sectionDescription}>Access RaptorFlow programmatically.</p>
            </div>

            {/* API Keys */}
            <div className={styles.card}>
                <div className={styles.cardHeader}>
                    <h3 className={styles.cardTitle}>API Keys</h3>
                    <Button variant="default" size="sm">Create Key</Button>
                </div>
                <div className={styles.apiKeyRow}>
                    <div className={styles.apiKeyInfo}>
                        <span className={styles.apiKeyName}>Production Key</span>
                        <code className={styles.apiKeyValue}>
                            {showKey ? apiKey : '••••••••••••••••••••'}
                        </code>
                    </div>
                    <button className={styles.showBtn} onClick={() => setShowKey(!showKey)}>
                        {showKey ? 'Hide' : 'Show'}
                    </button>
                    <button className={styles.copyBtn}>Copy</button>
                </div>
            </div>

            {/* Webhooks */}
            <div className={styles.card}>
                <div className={styles.cardHeader}>
                    <h3 className={styles.cardTitle}>Webhooks</h3>
                    <Button variant="secondary" size="sm">Add Endpoint</Button>
                </div>
                <div className={styles.emptyState}>
                    <span>No webhooks configured</span>
                </div>
            </div>

            {/* Usage */}
            <div className={styles.card}>
                <h3 className={styles.cardTitle}>API Usage</h3>
                <div className={styles.usageBar}>
                    <div className={styles.usageFill} style={{ width: '35%' }} />
                </div>
                <div className={styles.usageInfo}>
                    <span>3,500 / 10,000 requests this month</span>
                    <span className={styles.usageReset}>Resets in 8 days</span>
                </div>
            </div>
        </div>
    );
}

function BillingSection() {
    return (
        <div className={styles.section}>
            <div className={styles.sectionHeader}>
                <h2 className={styles.sectionTitle}>Billing</h2>
                <p className={styles.sectionDescription}>Manage your subscription.</p>
            </div>

            {/* Current Plan */}
            <div className={styles.planCard}>
                <div className={styles.planHeader}>
                    <div>
                        <span className={styles.planName}>Pro Plan</span>
                        <span className={styles.planPrice}>$49<span>/mo</span></span>
                    </div>
                    <span className={styles.badgePro}>Current</span>
                </div>
                <div className={styles.planFeatures}>
                    <span>✓ Unlimited moves & campaigns</span>
                    <span>✓ AI-powered content generation</span>
                    <span>✓ Team collaboration (up to 5)</span>
                    <span>✓ Priority support</span>
                </div>
                <div className={styles.cardActions}>
                    <Button variant="secondary" size="sm">Change Plan</Button>
                    <Button variant="ghost" size="sm">Cancel</Button>
                </div>
            </div>

            {/* Usage */}
            <div className={styles.card}>
                <h3 className={styles.cardTitle}>Usage This Period</h3>
                <div className={styles.usageGrid}>
                    <div className={styles.usageItem}>
                        <span className={styles.usageValue}>47</span>
                        <span className={styles.usageLabel}>Moves Created</span>
                    </div>
                    <div className={styles.usageItem}>
                        <span className={styles.usageValue}>12</span>
                        <span className={styles.usageLabel}>Campaigns</span>
                    </div>
                    <div className={styles.usageItem}>
                        <span className={styles.usageValue}>3.5K</span>
                        <span className={styles.usageLabel}>API Calls</span>
                    </div>
                    <div className={styles.usageItem}>
                        <span className={styles.usageValue}>3</span>
                        <span className={styles.usageLabel}>Team Members</span>
                    </div>
                </div>
            </div>

            {/* Payment */}
            <div className={styles.card}>
                <div className={styles.cardHeader}>
                    <h3 className={styles.cardTitle}>Payment Method</h3>
                    <Button variant="ghost" size="sm">Edit</Button>
                </div>
                <div className={styles.paymentRow}>
                    <span className={styles.cardBrand}>💳 Visa</span>
                    <span>•••• 4242</span>
                    <span className={styles.cardExpiry}>Exp 12/26</span>
                </div>
            </div>

            {/* Invoices */}
            <div className={styles.card}>
                <h3 className={styles.cardTitle}>Recent Invoices</h3>
                <div className={styles.invoiceList}>
                    {['Dec 2024', 'Nov 2024', 'Oct 2024'].map((month, i) => (
                        <div key={i} className={styles.invoiceRow}>
                            <span>{month}</span>
                            <span className={styles.invoiceAmount}>$49.00</span>
                            <button className={styles.downloadBtn}>Download</button>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}

// ============================================
// Reusable Toggle Component
// ============================================

function Toggle({ checked, onChange }: { checked: boolean; onChange: () => void }) {
    return (
        <button
            className={`${styles.toggle} ${checked ? styles.on : ''}`}
            onClick={onChange}
            role="switch"
            aria-checked={checked}
        >
            <span className={styles.toggleDot} />
        </button>
    );
}

// ============================================
// Icons
// ============================================

function UserIcon() {
    return (
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
            <circle cx="8" cy="4" r="2.5" />
            <path d="M3 14c0-2.76 2.24-5 5-5s5 2.24 5 5" />
        </svg>
    );
}

function WorkspaceIcon() {
    return (
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
            <rect x="2" y="2" width="12" height="12" rx="2" />
            <path d="M5 5H11M5 8H11M5 11H8" />
        </svg>
    );
}

function TeamIcon() {
    return (
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
            <circle cx="6" cy="5" r="2" />
            <circle cx="11" cy="5" r="2" />
            <path d="M2 13c0-2 1.5-3.5 4-3.5s4 1.5 4 3.5M10 13c0-2 1-3 3-3s3 1 3 3" />
        </svg>
    );
}

function AppearanceIcon() {
    return (
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
            <circle cx="8" cy="8" r="6" />
            <path d="M8 2v12" />
            <path d="M8 2c-3.31 0-6 2.69-6 6s2.69 6 6 6" fill="currentColor" opacity="0.3" />
        </svg>
    );
}

function BellIcon() {
    return (
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
            <path d="M6 12.5c0 1.1.9 2 2 2s2-.9 2-2M12 9V6c0-2.21-1.79-4-4-4S4 3.79 4 6v3l-1 2h10l-1-2z" />
        </svg>
    );
}

function IntegrationsIcon() {
    return (
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
            <rect x="2" y="2" width="4" height="4" rx="1" />
            <rect x="10" y="2" width="4" height="4" rx="1" />
            <rect x="2" y="10" width="4" height="4" rx="1" />
            <rect x="10" y="10" width="4" height="4" rx="1" />
        </svg>
    );
}

function CodeIcon() {
    return (
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
            <path d="M5 4L1 8l4 4M11 4l4 4-4 4M9 2L7 14" />
        </svg>
    );
}

function BillingIcon() {
    return (
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
            <rect x="2" y="3" width="12" height="10" rx="2" />
            <path d="M2 7h12" />
        </svg>
    );
}

function SunIcon() {
    return (
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" strokeWidth="1.5">
            <circle cx="9" cy="9" r="3" />
            <path d="M9 2v2M9 14v2M2 9h2M14 9h2M4.22 4.22l1.42 1.42M12.36 12.36l1.42 1.42M4.22 13.78l1.42-1.42M12.36 5.64l1.42-1.42" />
        </svg>
    );
}

function MoonIcon() {
    return (
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" strokeWidth="1.5">
            <path d="M15.54 9.07A6.99 6.99 0 018.93 2.46 7 7 0 1015.54 9.07z" />
        </svg>
    );
}

function SystemIcon() {
    return (
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" strokeWidth="1.5">
            <rect x="3" y="3" width="12" height="9" rx="1" />
            <path d="M6 15h6M9 12v3" />
        </svg>
    );
}
