'use client';

import React from 'react';
import * as PhosphorIcons from '@phosphor-icons/react';

export interface IconProps {
  icon?: any;
  size?: number;
  className?: string;
  color?: string;
  weight?: 'thin' | 'light' | 'regular' | 'bold' | 'fill' | 'duotone';
}

export const AppIcon: React.FC<IconProps> = ({ icon, size = 16, className, color, weight = 'regular' }) => {
  if (!icon) return null;

  // Use any to bypass TypeScript's strict checking for dynamic icon access
  const IconComponent = (PhosphorIcons as any)[icon];
  if (!IconComponent || typeof IconComponent !== 'function') return null;

  return React.createElement(IconComponent, {
    size,
    className,
    color,
    weight
  });
};

export const Icons = {
  // Navigation
  Home: 'House',
  Campaigns: 'Target',
  Moves: 'Bolt',
  Settings: 'Gear',
  Target: 'Target',

  // Analytics
  Analytics: 'ChartLine',
  Schedule: 'Calendar',
  Team: 'Users',
  Goal: 'Trophy',
  Brain: 'Brain',
  Chart: 'ChartLine',
  Activity: 'Activity',
  View: 'Eye',
  Security: 'Shield',

  // Content
  Document: 'FileText',
  Image: 'Image',
  Video: 'Video',
  Audio: 'SpeakerHigh',
  Nature: 'Tree',

  // Communication
  Message: 'ChatText',
  Bell: 'Bell',
  Email: 'Envelope',
  Phone: 'Phone',

  // Actions
  Add: 'Plus',
  Remove: 'Minus',
  Success: 'Check',
  Close: 'X',
  ArrowRight: 'ArrowRight',
  ArrowLeft: 'ArrowLeft',
  ArrowUp: 'ArrowUp',
  ArrowDown: 'ArrowDown',

  // File operations
  Folder: 'Folder',
  File: 'File',
  Download: 'Download',
  Upload: 'UploadSimple',
  Cloud: 'Cloud',

  // Social
  Favorite: 'Heart',
  Share: 'ShareNetwork',
  Star: 'Star',
  Bookmark: 'Bookmark',

  // Business
  Money: 'CurrencyDollar',
  Cart: 'ShoppingCart',
  Payment: 'CreditCard',
  Receipt: 'Receipt',

  // Development
  Code: 'Code',
  Terminal: 'Terminal',
  Database: 'Database',
  Server: 'Server',

  // Security
  Lock: 'Lock',
  Key: 'Key',
  Fingerprint: 'Fingerprint',

  // Time
  Time: 'Clock',
  Timer: 'Timer',
  Calendar: 'Calendar',

  // Location
  Map: 'MapPin',
  Pin: 'MapPin',
  Navigation: 'Compass',

  // Weather
  Sun: 'Sun',
  Rain: 'CloudRain',
  Wind: 'Wind',
  Tree: 'Tree',

  // UI elements
  More: 'DotsThree',
  Search: 'MagnifyingGlass',
  Filter: 'Funnel',
  Menu: 'List',
  Delete: 'Trash',
  Edit: 'Pencil',
  Copy: 'Copy',
  Refresh: 'ArrowClockwise',
  Info: 'Info',
  Warning: 'Warning',
  Error: 'XCircle',

  // Additional mappings for existing code
  Clock: 'Clock',
  BarChart2: 'ChartBar',
  Sparkles: 'Sparkle',
  BrainCircuit: 'Brain',
  Rocket: 'Rocket',
  CheckCircle2: 'CheckCircle',
  X: 'X',
};

// Individual icon components for backward compatibility
export const ChevronDownIcon = ({ size = 16, ...props }: any) => (
  <AppIcon icon="CaretDown" size={size} {...props} />
);

export const MicIcon = ({ size = 16, ...props }: any) => (
  <AppIcon icon="Microphone" size={size} {...props} />
);

export const MessageIcon = ({ size = 16, ...props }: any) => (
  <AppIcon icon="ChatText" size={size} {...props} />
);

export const TargetIcon = ({ size = 16, ...props }: any) => (
  <AppIcon icon="Target" size={size} {...props} />
);

export const SparklesIcon = ({ size = 16, ...props }: any) => (
  <AppIcon icon="Sparkle" size={size} {...props} />
);

export const ArrowRightIcon = ({ size = 16, ...props }: any) => (
  <AppIcon icon="ArrowRight" size={size} {...props} />
);

export const FoundationIcon = ({ size = 16, ...props }: any) => (
  <AppIcon icon="House" size={size} {...props} />
);

export const CohortsIcon = ({ size = 16, ...props }: any) => (
  <AppIcon icon="UsersThree" size={size} {...props} />
);

export const CampaignsIcon = ({ size = 16, ...props }: any) => (
  <AppIcon icon="Target" size={size} {...props} />
);

export const MuseIcon = ({ size = 16, ...props }: any) => (
  <AppIcon icon="Sparkle" size={size} {...props} />
);

export const AlertCircleIcon = ({ size = 16, ...props }: any) => (
  <AppIcon icon="WarningCircle" size={size} {...props} />
);

export const CheckCircleIcon = ({ size = 16, ...props }: any) => (
  <AppIcon icon="CheckCircle" size={size} {...props} />
);

export const UserIcon = ({ size = 16, ...props }: any) => (
  <AppIcon icon="User" size={size} {...props} />
);

export const WorkspaceIcon = ({ size = 16, ...props }: any) => (
  <AppIcon icon="Buildings" size={size} {...props} />
);

export const AppearanceIcon = ({ size = 16, ...props }: any) => (
  <AppIcon icon="Palette" size={size} {...props} />
);

export const BellIcon = ({ size = 16, ...props }: any) => (
  <AppIcon icon="Bell" size={size} {...props} />
);

export const SunIcon = ({ size = 16, ...props }: any) => (
  <AppIcon icon="Sun" size={size} {...props} />
);

export const MoonIcon = ({ size = 16, ...props }: any) => (
  <AppIcon icon="Moon" size={size} {...props} />
);

export const SystemIcon = ({ size = 16, ...props }: any) => (
  <AppIcon icon="Monitor" size={size} {...props} />
);

export const TrashIcon = ({ size = 16, ...props }: any) => (
  <AppIcon icon="Trash" size={size} {...props} />
);

export const DashboardIcon = ({ size = 16, ...props }: any) => (
  <AppIcon icon="Layout" size={size} {...props} />
);

export const MovesIcon = ({ size = 16, ...props }: any) => (
  <AppIcon icon="Bolt" size={size} {...props} />
);

export const MatrixIcon = ({ size = 16, ...props }: any) => (
  <AppIcon icon="GridFour" size={size} {...props} />
);

export const BlackboxIcon = ({ size = 16, ...props }: any) => (
  <AppIcon icon="Cube" size={size} {...props} />
);

export const FilterIcon = ({ size = 16, ...props }: any) => (
  <AppIcon icon="Funnel" size={size} {...props} />
);

export const ZapIcon = ({ size = 16, ...props }: any) => (
  <AppIcon icon="Bolt" size={size} {...props} />
);

export default AppIcon;
