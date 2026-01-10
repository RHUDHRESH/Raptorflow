/* ══════════════════════════════════════════════════════════════════════════════
   EXTERNAL LINKS — Platform URL Mapping & Utilities
   Centralized configuration for all external platform links
   ══════════════════════════════════════════════════════════════════════════════ */

/**
 * Platform URL mapping for external services
 */
export const PLATFORM_URLS: Record<string, string> = {
    // Social Media
    "LinkedIn": "https://linkedin.com",
    "X (Twitter)": "https://x.com",
    "Twitter": "https://x.com",
    "Instagram": "https://instagram.com",
    "TikTok": "https://tiktok.com",
    "YouTube": "https://youtube.com",
    "Facebook": "https://facebook.com",
    "Reddit": "https://reddit.com",
    "Threads": "https://threads.net",
    "Pinterest": "https://pinterest.com",
    "Snapchat": "https://snapchat.com",

    // Professional
    "Medium": "https://medium.com",
    "Substack": "https://substack.com",
    "Discord": "https://discord.com",
    "Slack": "https://slack.com",

    // Communication
    "Email": "mailto:",
    "WhatsApp": "https://wa.me",
    "Telegram": "https://t.me",
};

/**
 * Deep link URLs for direct posting (where supported)
 */
export const PLATFORM_COMPOSE_URLS: Record<string, string> = {
    "LinkedIn": "https://www.linkedin.com/feed/?shareActive=true",
    "X (Twitter)": "https://x.com/compose/tweet",
    "Twitter": "https://x.com/compose/tweet",
    "Facebook": "https://www.facebook.com/sharer/sharer.php",
    "Reddit": "https://www.reddit.com/submit",
};

/**
 * Platform icons (Lucide icon names for consistency)
 */
export const PLATFORM_ICONS: Record<string, string> = {
    "LinkedIn": "Linkedin",
    "X (Twitter)": "Twitter",
    "Twitter": "Twitter",
    "Instagram": "Instagram",
    "TikTok": "Music2",
    "YouTube": "Youtube",
    "Facebook": "Facebook",
    "Reddit": "MessageCircle",
    "Email": "Mail",
    "Discord": "MessageSquare",
};

/**
 * Open a platform URL in a new tab
 */
export function openPlatform(platform: string): void {
    const url = PLATFORM_URLS[platform];
    if (url) {
        window.open(url, "_blank", "noopener,noreferrer");
    }
}

/**
 * Open a platform's compose/post URL with optional text
 */
export function openPlatformCompose(platform: string, text?: string): void {
    let url = PLATFORM_COMPOSE_URLS[platform] || PLATFORM_URLS[platform];

    if (url) {
        // Add text parameter for platforms that support it
        if (text) {
            const encodedText = encodeURIComponent(text);
            if (platform === "X (Twitter)" || platform === "Twitter") {
                url = `${url}?text=${encodedText}`;
            } else if (platform === "LinkedIn") {
                url = `${url}&text=${encodedText}`;
            } else if (platform === "Reddit") {
                url = `${url}?title=${encodedText}`;
            }
        }
        window.open(url, "_blank", "noopener,noreferrer");
    }
}

/**
 * Copy text to clipboard and optionally open platform
 */
export async function copyAndOpenPlatform(
    text: string,
    platform: string,
    openAfterCopy: boolean = true
): Promise<boolean> {
    try {
        await navigator.clipboard.writeText(text);
        if (openAfterCopy) {
            openPlatform(platform);
        }
        return true;
    } catch (error) {
        console.error("Failed to copy to clipboard:", error);
        return false;
    }
}

/**
 * Get the base URL for a platform
 */
export function getPlatformUrl(platform: string): string | undefined {
    return PLATFORM_URLS[platform];
}

/**
 * Check if a platform has a compose/post deep link
 */
export function hasComposeUrl(platform: string): boolean {
    return platform in PLATFORM_COMPOSE_URLS;
}
