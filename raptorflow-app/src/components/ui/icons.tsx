import React from 'react';

export interface IconProps extends React.SVGProps<SVGSVGElement> {
    size?: number | string;
}

export function UserIcon({ size = 16, ...props }: IconProps) {
    return (
        <svg width={size} height={size} viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" {...props}>
            <circle cx="8" cy="4" r="2.5" />
            <path d="M3 14c0-2.76 2.24-5 5-5s5 2.24 5 5" />
        </svg>
    );
}

export function TargetIcon({ size = 16, ...props }: IconProps) {
    return (
        <svg width={size} height={size} viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" {...props}>
            <circle cx="8" cy="8" r="6" />
            <circle cx="8" cy="8" r="2" fill="currentColor" />
        </svg>
    );
}

export function WorkspaceIcon({ size = 16, ...props }: IconProps) {
    return (
        <svg width={size} height={size} viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" {...props}>
            <rect x="2" y="2" width="12" height="12" rx="2" />
            <path d="M5 5H11M5 8H11M5 11H8" />
        </svg>
    );
}

export function AppearanceIcon({ size = 16, ...props }: IconProps) {
    return (
        <svg width={size} height={size} viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" {...props}>
            <circle cx="8" cy="8" r="6" />
            <path d="M8 2v12" />
            <path d="M8 2c-3.31 0-6 2.69-6 6s2.69 6 6 6" fill="currentColor" opacity="0.3" />
        </svg>
    );
}

export function BellIcon({ size = 16, ...props }: IconProps) {
    return (
        <svg width={size} height={size} viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" {...props}>
            <path d="M6 12.5c0 1.1.9 2 2 2s2-.9 2-2M12 9V6c0-2.21-1.79-4-4-4S4 3.79 4 6v3l-1 2h10l-1-2z" />
        </svg>
    );
}

export function SunIcon({ size = 18, ...props }: IconProps) {
    return (
        <svg width={size} height={size} viewBox="0 0 18 18" fill="none" stroke="currentColor" strokeWidth="1.5" {...props}>
            <circle cx="9" cy="9" r="3" />
            <path d="M9 2v2M9 14v2M2 9h2M14 9h2M4.22 4.22l1.42 1.42M12.36 12.36l1.42 1.42M4.22 13.78l1.42-1.42M12.36 5.64l1.42-1.42" />
        </svg>
    );
}

export function MoonIcon({ size = 18, ...props }: IconProps) {
    return (
        <svg width={size} height={size} viewBox="0 0 18 18" fill="none" stroke="currentColor" strokeWidth="1.5" {...props}>
            <path d="M15.54 9.07A6.99 6.99 0 018.93 2.46 7 7 0 1015.54 9.07z" />
        </svg>
    );
}

export function SystemIcon({ size = 18, ...props }: IconProps) {
    return (
        <svg width={size} height={size} viewBox="0 0 18 18" fill="none" stroke="currentColor" strokeWidth="1.5" {...props}>
            <rect x="3" y="3" width="12" height="9" rx="1" />
            <path d="M6 15h6M9 12v3" />
        </svg>
    );
}

export function TrashIcon({ size = 16, ...props }: IconProps) {
    return (
        <svg width={size} height={size} viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" {...props}>
            <path d="M2.5 4.5h11" />
            <path d="M12.5 4.5V14c0 1.1-.9 2-2 2h-5c-1.1 0-2-.9-2-2V4.5M5.5 4.5V2.5c0-.55.45-1 1-1h3c.55 0 1 .45 1 1v2" />
        </svg>
    );
}

export function ChevronRightIcon({ size = 16, ...props }: IconProps) {
    return (
        <svg width={size} height={size} viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" {...props}>
            <path d="M6 3l5 5-5 5" />
        </svg>
    );
}

export function ChevronDownIcon({ size = 16, ...props }: IconProps) {
    return (
        <svg width={size} height={size} viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" {...props}>
            <path d="M3 6l5 5 5-5" />
        </svg>
    );
}

export function PlusIcon({ size = 16, ...props }: IconProps) {
    return (
        <svg width={size} height={size} viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" {...props}>
            <path d="M8 3v10M3 8h10" />
        </svg>
    );
}

export function CloseIcon({ size = 16, ...props }: IconProps) {
    return (
        <svg width={size} height={size} viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" {...props}>
            <path d="M12 4L4 12M4 4l8 8" />
        </svg>
    );
}

export function CheckIcon({ size = 16, ...props }: IconProps) {
    return (
        <svg width={size} height={size} viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" {...props}>
            <path d="M13.5 4.5L6.5 11.5L2.5 7.5" />
        </svg>
    );
}

export function SearchIcon({ size = 16, ...props }: IconProps) {
    return (
        <svg width={size} height={size} viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" {...props}>
            <circle cx="7" cy="7" r="5" />
            <path d="M11 11l3 3" />
        </svg>
    );
}

export function DashboardIcon({ size = 16, ...props }: IconProps) {
    return (
        <svg width={size} height={size} viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" {...props}>
            <rect x="2" y="2" width="5" height="5" rx="1" />
            <rect x="9" y="2" width="5" height="5" rx="1" />
            <rect x="2" y="9" width="5" height="5" rx="1" />
            <rect x="9" y="9" width="5" height="5" rx="1" />
        </svg>
    );
}

export function FoundationIcon({ size = 16, ...props }: IconProps) {
    return (
        <svg width={size} height={size} viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" {...props}>
            <path d="M2 14h12M4 14V6L8 3l4 3v8" />
            <path d="M6 14v-4h4v4" />
        </svg>
    );
}

export function CohortsIcon({ size = 16, ...props }: IconProps) {
    return (
        <svg width={size} height={size} viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" {...props}>
            <circle cx="5" cy="6" r="3" />
            <path d="M8 6a3 3 0 1 1 6 0" opacity="0.5" />
            <path d="M2.5 14c0-2 2-3.5 5-3.5" />
            <path d="M13.5 14c0-1.5-1.5-2.5-3-2.5" opacity="0.5" />
        </svg>
    );
}

export function MovesIcon({ size = 16, ...props }: IconProps) {
    return (
        <svg width={size} height={size} viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" {...props}>
            <path d="M3 8h10M10 5l3 3-3 3" />
            <circle cx="8" cy="8" r="7" strokeOpacity="0.3" />
        </svg>
    );
}

export function CampaignsIcon({ size = 16, ...props }: IconProps) {
    return (
        <svg width={size} height={size} viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" {...props}>
            <path d="M13 8l-4-4v3H3v2h6v3l4-4z" />
            <path d="M13 5v6" />
        </svg>
    );
}

export function MuseIcon({ size = 16, ...props }: IconProps) {
    return (
        <svg width={size} height={size} viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" {...props}>
            <path d="M9.5 3.5L12.5 6.5" />
            <path d="M13.5 5.5l-8 8-3 1 1-3 8-8a2.121 2.121 0 0 1 3 3z" />
        </svg>
    );
}

export function MatrixIcon({ size = 16, ...props }: IconProps) {
    return (
        <svg width={size} height={size} viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" {...props}>
            <rect x="2" y="2" width="12" height="12" rx="2" />
            <path d="M2 6h12M6 2v12M10 2v12" />
        </svg>
    );
}

export function BlackboxIcon({ size = 16, ...props }: IconProps) {
    return (
        <svg width={size} height={size} viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" {...props}>
            <path d="M2 5l6-3 6 3v6l-6 3-6-3V5z" />
            <path d="M8 8V2M2 5l6 3 6-3" />
        </svg>
    );
}

export function ArrowRightIcon({ size = 16, ...props }: IconProps) {
    return (
        <svg width={size} height={size} viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" {...props}>
            <path d="M2.5 8h11M9.5 4l4 4-4 4" />
        </svg>
    );
}

export function CheckCircleIcon({ size = 16, ...props }: IconProps) {
    return (
        <svg width={size} height={size} viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" {...props}>
            <circle cx="8" cy="8" r="6" />
            <path d="M11.5 6l-4.5 4.5-2-2" />
        </svg>
    );
}

export function AlertCircleIcon({ size = 16, ...props }: IconProps) {
    return (
        <svg width={size} height={size} viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" {...props}>
            <circle cx="8" cy="8" r="6" />
            <path d="M8 5v4M8 11h.01" />
        </svg>
    );
}

// ... previous icons ...

export function ZapIcon({ size = 16, ...props }: IconProps) {
    return (
        <svg width={size} height={size} viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" {...props}>
            <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" transform="scale(0.66) translate(1,1)" />
            {/* Simplified lightning */}
            <path d="M8.5 2L3 9.5h5L7.5 14l5.5-7.5h-5L8.5 2z" />
        </svg>
    );
}

export function FilterIcon({ size = 16, ...props }: IconProps) {
    return (
        <svg width={size} height={size} viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" {...props}>
            <path d="M2.5 4.5h11M4.5 9.5h7M7 14.5h2" />
        </svg>
    );
}

export function MicIcon({ size = 16, ...props }: IconProps) {
    return (
        <svg width={size} height={size} viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" {...props}>
            <path d="M8 12a3 3 0 0 0 3-3V5a3 3 0 0 0-6 0v4a3 3 0 0 0 3 3z" />
            <path d="M5 10v1a3 3 0 0 0 6 0v-1" />
            <path d="M8 13v2" />
        </svg>
    );
}

export function SparklesIcon({ size = 16, ...props }: IconProps) {
    return (
        <svg width={size} height={size} viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" {...props}>
            <path d="M8 2l1.5 4.5L14 8l-4.5 1.5L8 14l-1.5-4.5L2 8l4.5-1.5L8 2z" />
        </svg>
    );
}

export function FolderIcon({ size = 16, ...props }: IconProps) {
    return (
        <svg width={size} height={size} viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" {...props}>
            <path d="M2 4a1 1 0 0 1 1-1h3l2 2h5a1 1 0 0 1 1 1v7a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V4z" />
        </svg>
    );
}

export function MessageIcon({ size = 16, ...props }: IconProps) {
    return (
        <svg width={size} height={size} viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" {...props}>
            <path d="M14 11a1 1 0 0 1-1 1H4l-2 2V3a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v8z" />
        </svg>
    );
}
