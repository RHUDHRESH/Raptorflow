import React from "react";

interface RaptorLogoProps {
    size?: number;
    className?: string;
}

/**
 * RaptorFlow Logo - Raptor head with compass needle beak
 * Distinctive, memorable, instantly recognizable
 */
export function RaptorLogo({ size = 32, className = "" }: RaptorLogoProps) {
    return (
        <svg
            width={size}
            height={size}
            viewBox="0 0 32 32"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            className={className}
        >
            {/* Raptor head outline with compass needle beak */}
            <path
                fillRule="evenodd"
                clipRule="evenodd"
                d="M8 4C6 4 4 6 4 10L4 14C4 16 5 18 7 19L7 22C7 24 8 26 10 27L16 30L22 20L28 16L24 14L28 12L22 8L8 4ZM14 18C15.1046 18 16 17.1046 16 16C16 14.8954 15.1046 14 14 14C12.8954 14 12 14.8954 12 16C12 17.1046 12.8954 18 14 18Z"
                fill="currentColor"
            />
        </svg>
    );
}

// Keep CompassLogo as alias
export const CompassLogo = RaptorLogo;
