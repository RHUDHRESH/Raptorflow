'use client';

import React, { useState } from 'react';
import { AppLayout } from '@/components/layout/AppLayout';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useIcpStore } from '@/lib/icp-store';
import styles from './settings.module.css';
import {
    UserIcon,
    WorkspaceIcon,
    TargetIcon,
    AppearanceIcon,
    BellIcon,
    SunIcon,
    MoonIcon,
    SystemIcon,
    TrashIcon
} from '@/components/ui/Icons';
import { Switch } from '@/components/ui/switch';

import { UsageChart } from '@/components/settings/UsageChart';
import { BarChart3 } from 'lucide-react';

type SettingsSection =
    | 'profile'
    | 'workspace'
    | 'targeting'
    | 'appearance'
    | 'notifications'
    | 'usage';

const SECTIONS: { id: SettingsSection; label: string; icon: React.ReactNode }[] = [
    { id: 'profile', label: 'Profile', icon: <UserIcon /> },
    { id: 'workspace', label: 'Workspace', icon: <WorkspaceIcon /> },
    { id: 'targeting', label: 'Targeting', icon: <TargetIcon /> },
    { id: 'appearance', label: 'Appearance', icon: <AppearanceIcon /> },
    { id: 'notifications', label: 'Notifications', icon: <BellIcon /> },
    { id: 'usage', label: 'Usage', icon: <BarChart3 className="w-5 h-5" /> },
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
            case 'targeting':
                return <TargetingSection />;
            case 'appearance':
                return <AppearanceSection theme={theme} setTheme={setTheme} />;
            case 'notifications':
                return <NotificationsSection notifications={notifications} setNotifications={setNotifications} />;
            case 'usage':
                return <UsageSection />;
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

function UsageSection() {
    return (
        <div className={styles.section}>
            <div className={styles.sectionHeader}>
                <h2 className={styles.sectionTitle}>Usage & Billing</h2>
                <p className={styles.sectionDescription}>Track your token consumption and plan limits.</p>
            </div>

            <div className="space-y-6">
                <UsageChart />

                <div className={styles.card}>
                    <h3 className={styles.cardTitle}>Plan Details</h3>
                    <div className="flex items-center justify-between p-4 bg-muted/30 rounded-lg border border-border/50">
                        <div>
                            <p className="font-medium">Pro Plan</p>
                            <p className="text-sm text-muted-foreground">$29/month • Billed monthly</p>
                        </div>
                        <Button variant="outline" size="sm">Manage Subscription</Button>
                    </div>
                </div>
            </div>
        </div>
    );
}

// ============================================
// Section Components
// ============================================

function TargetingSection() {
    const router = useRouter();
    const icps = useIcpStore((state: any) => state.icps);
    const activeIcpId = useIcpStore((state: any) => state.activeIcpId);
    const setActiveIcp = useIcpStore((state: any) => state.setActiveIcp);
    const deleteIcp = useIcpStore((state: any) => state.deleteIcp);

    const handleDelete = (id: string, name: string) => {
        if (confirm(`Are you sure you want to delete "${name}"? This action cannot be undone.`)) {
            deleteIcp(id);
        }
    };

    return (
        <div className={styles.section}>
            <div className={styles.sectionHeader}>
                <h2 className={styles.sectionTitle}>Targeting (ICP)</h2>
                <p className={styles.sectionDescription}>Manage your Ideal Customer Profiles.</p>
            </div>

            <div className={styles.card}>
                <div className={styles.cardHeader}>
                    <h3 className={styles.cardTitle}>Active Profiles</h3>
                    <Button
                        variant="default"
                        size="sm"
                        onClick={() => router.push('/icp/new')}
                    >
                        Create New ICP
                    </Button>
                </div>

                <div className={styles.teamList}>
                    {icps.length === 0 && (
                        <div className={styles.emptyState}>
                            <span>No ICPs defined yet.</span>
                        </div>
                    )}

                    {icps.map((icp: any) => (
                        <div key={icp.id} className={styles.teamRow}>
                            <div className={`${styles.avatarSmall} bg-slate-100 text-slate-600`}>
                                {icp.name.substring(0, 2).toUpperCase()}
                            </div>
                            <div className={styles.teamInfo}>
                                <span className={styles.teamName}>{icp.name}</span>
                                <span className={styles.teamEmail}>Confidence: {(icp.confidenceScore * 100).toFixed(0)}%</span>
                            </div>
                            {activeIcpId === icp.id ? (
                                <span className={`${styles.roleBadge} bg-green-100 text-green-700`}>Active</span>
                            ) : (
                                <div className="flex items-center gap-3">
                                    <button
                                        onClick={() => setActiveIcp(icp.id)}
                                        className="text-xs text-slate-500 hover:text-slate-900 underline"
                                    >
                                        Set Active
                                    </button>
                                </div>
                            )}
                            <div className="flex items-center gap-2">
                                <Button
                                    variant="secondary"
                                    size="sm"
                                    onClick={() => router.push('/target')}
                                >
                                    View
                                </Button>
                                {activeIcpId !== icp.id && (
                                    <Button
                                        variant="ghost"
                                        size="icon"
                                        onClick={() => handleDelete(icp.id, icp.name)}
                                        className="h-8 w-8 text-slate-400 hover:text-red-600 hover:bg-red-50"
                                    >
                                        <TrashIcon />
                                    </Button>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            <div className={styles.card}>
                <h3 className={styles.cardTitle}>About Targeting</h3>
                <p className="text-sm text-slate-500 mb-4">
                    Your Active ICP determines how Muse writes content and how campaigns are structured.
                    Always keep your primary target up to date.
                </p>
            </div>
        </div>
    );
}

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
                    <Switch checked={false} onCheckedChange={() => { }} />
                </div>
                <div className={styles.optionRow}>
                    <div>
                        <span className={styles.optionLabel}>Reduced Motion</span>
                        <span className={styles.optionMeta}>Minimize animations</span>
                    </div>
                    <Switch checked={false} onCheckedChange={() => { }} />
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
                    <Switch checked={notifications.moveReminders} onCheckedChange={() => toggle('moveReminders')} />
                </div>
                <div className={styles.optionRow}>
                    <div>
                        <span className={styles.optionLabel}>Weekly Digest</span>
                        <span className={styles.optionMeta}>Weekly progress summary</span>
                    </div>
                    <Switch checked={notifications.weeklyDigest} onCheckedChange={() => toggle('weeklyDigest')} />
                </div>
                <div className={styles.optionRow}>
                    <div>
                        <span className={styles.optionLabel}>Campaign Alerts</span>
                        <span className={styles.optionMeta}>Alerts for campaigns needing attention</span>
                    </div>
                    <Switch checked={notifications.campaignAlerts} onCheckedChange={() => toggle('campaignAlerts')} />
                </div>
                <div className={styles.optionRow}>
                    <div>
                        <span className={styles.optionLabel}>Product Updates</span>
                        <span className={styles.optionMeta}>New features and improvements</span>
                    </div>
                    <Switch checked={notifications.productUpdates} onCheckedChange={() => toggle('productUpdates')} />
                </div>
            </div>
        </div>
    );
}
