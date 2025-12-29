import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'FAQ — RaptorFlow',
  description:
    'Frequently asked questions about RaptorFlow. Learn about features, pricing, billing, and support.',
  openGraph: {
    title: 'FAQ — RaptorFlow',
    description: 'Everything you need to know about RaptorFlow.',
    type: 'website',
  },
};

export default function FAQLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
