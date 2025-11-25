export const WEEK_OPTIONS = ["This week (24–30 Nov)", "Next week (1–7 Dec)", "Custom"];
export const BRANDS = ["Altivox – Main", "Altivox – SMB", "Sandbox"];
export const MODEL_ROUTES = ["Auto", "Cheap", "Premium"];

export const MOVES = [
    {
        id: "m1",
        name: "Weekend Booking Engine",
        cohorts: ["Weekend Foodies", "High-intent Dine-in"],
        channels: ["IG", "WA", "LI"],
        progress: "3/5 ready",
    },
    {
        id: "m2",
        name: "Office Lunch Upsell",
        cohorts: ["Office Lunch Crowd"],
        channels: ["IG", "WA"],
        progress: "2/4 ready",
    },
];

export const COHORTS = [
    { name: "Weekend Foodies", note: "Reels + scarcity working" },
    { name: "Office Lunch Crowd", note: "Stories > Posts" },
    { name: "High-intent Dine-in", note: "Proof + scarcity" },
];

export const VOICE = ["Blunt", "No cringe", "Data-backed", "Founder-first"];

export const ASSETS = [
    {
        id: "a1",
        title: 'IG Carousel – "Stop Discounting Your Time"',
        channel: "IG",
        type: "Carousel",
        status: "Draft",
        move: "Weekend Booking Engine",
        cohorts: ["Weekend Foodies"],
        tags: ["Hook: Story", "Angle: Founder mistake", "Objective: Book calls"],
    },
    {
        id: "a2",
        title: 'LI Post – "Founder Pricing Math"',
        channel: "LI",
        type: "Post",
        status: "In review",
        move: "Office Lunch Upsell",
        cohorts: ["Office Lunch Crowd"],
        tags: ["Hook: Spiky", "Angle: Proof", "Objective: Book demos"],
    },
    {
        id: "a3",
        title: 'Email – "Stop the Discounts"',
        channel: "Email",
        type: "Email",
        status: "Ready",
        move: "Weekend Booking Engine",
        cohorts: ["Weekend Foodies"],
        tags: ["Hook: Proof", "Objective: Rebook", "CTA: Book call"],
    },
];

export const INSIGHTS = [
    "Reels with face close-up: 3.1x saves vs food-only",
    "Story-led hooks > contrarian for “Weekend Foodies”",
    "WA broadcasts Fri–Sun drive 70% of bookings",
];

export const IDEA_STACK = [
    {
        id: "h1",
        text: `"Your discount isn’t generosity. It’s self-sabotage."`,
        tags: ["Hook: Spiky", "Cohort: Indie SaaS"],
    },
    {
        id: "h2",
        text: `"Stop trying to win on price. Win on being irreplaceable."`,
        tags: ["Hook: Pricing", "Cohort: DTC"],
    },
];

export const STATUS_COLORS = {
    Draft: "bg-neutral-100 text-neutral-800 border-neutral-200",
    "In review": "bg-amber-50 text-amber-700 border-amber-100 ring-1 ring-amber-200/50",
    Ready: "bg-emerald-50 text-emerald-700 border-emerald-100 ring-1 ring-emerald-200/50",
    Published: "bg-blue-50 text-blue-700 border-blue-100 ring-1 ring-blue-200/50",
};
