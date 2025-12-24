import type { Metadata } from 'next';

// Feature-specific metadata
const featureMetadata: Record<string, { title: string; description: string }> = {
    foundation: {
        title: 'Foundation — RaptorFlow',
        description: 'Build your BrandKit, positioning, and messaging architecture in one place. The strategic foundation that makes every piece of marketing connect.',
    },
    cohorts: {
        title: 'Cohorts — RaptorFlow',
        description: 'Define Ideal Customer Profiles that go beyond demographics. Behavioral segmentation that actually predicts who will buy—and why.',
    },
    moves: {
        title: 'Moves — RaptorFlow',
        description: 'Weekly execution that actually ships. Bite-sized execution packets that turn your 90-day plan into daily action.',
    },
    campaigns: {
        title: 'Campaigns — RaptorFlow',
        description: '90-day strategic arcs that compound. Not random acts of content, but coordinated efforts with clear outcomes.',
    },
    muse: {
        title: 'Muse — RaptorFlow',
        description: 'AI content that sounds like you. Asset generation trained on your Foundation, your voice, your strategy.',
    },
    matrix: {
        title: 'Matrix — RaptorFlow',
        description: 'See everything. Control everything. Your command center with RAG status, progress tracking, and kill-switch.',
    },
    blackbox: {
        title: 'Blackbox — RaptorFlow',
        description: 'Prove what works. Automatic A/B testing and experiments. Stop guessing. Start knowing.',
    },
    radar: {
        title: 'Radar — RaptorFlow',
        description: 'Know what your competitors do not. Competitor intelligence that keeps you three moves ahead.',
    },
};

type Props = {
    params: Promise<{ feature: string }>;
};

export async function generateMetadata({ params }: Props): Promise<Metadata> {
    const { feature } = await params;
    const meta = featureMetadata[feature];

    if (!meta) {
        return {
            title: 'Feature — RaptorFlow',
            description: 'Explore RaptorFlow features.',
        };
    }

    return {
        title: meta.title,
        description: meta.description,
        openGraph: {
            title: meta.title,
            description: meta.description,
            type: 'website',
        },
    };
}

export default function FeatureLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return <>{children}</>;
}
