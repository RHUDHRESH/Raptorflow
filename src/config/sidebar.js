import {
    LayoutDashboard,
    Target,
    Users,
    HelpCircle,
    Sparkles,
    Settings,
    User,
    BookOpen,
    Activity,
    Calendar,
    Megaphone,
} from 'lucide-react';
import { routes } from '../lib/routes';

/**
 * Sidebar Configuration
 * 
 * Single source of truth for sidebar navigation structure.
 * Organized into logical sections with proper route references.
 */

export const sidebarSections = [
    {
        id: 'navigation',
        label: 'Navigation',
        items: [
            { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard, to: routes.dashboard },
            { id: 'positioning', label: 'Positioning', icon: Target, to: routes.positioning },
            { id: 'moves', label: 'Moves', icon: BookOpen, to: routes.moves },
            { id: 'campaigns', label: 'Campaigns', icon: Megaphone, to: routes.campaigns },
            { id: 'muse', label: 'Muse', icon: Sparkles, to: routes.muse },
            { id: 'matrix', label: 'Matrix', icon: Activity, to: routes.matrix },
            { id: 'daily_pulse', label: 'Daily Pulse', icon: Calendar, to: routes.today },
            { id: 'strategy', label: 'Strategy', icon: Target, to: routes.strategy },
            { id: 'cohorts', label: 'Cohorts', icon: Users, to: routes.cohorts }, // Currently /cohorts-moves
        ],
    },
    {
        id: 'system',
        label: 'System',
        items: [
            { id: 'settings', label: 'Settings', icon: Settings, to: routes.settings },
            { id: 'account', label: 'Account', icon: User, to: routes.account },
            { id: 'support', label: 'Support', icon: HelpCircle, to: routes.support },
        ],
    },
];
