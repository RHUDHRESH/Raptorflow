import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Pricing — RaptorFlow',
  description:
    'Simple, honest pricing for RaptorFlow. Three plans: Ascent (₹5,000/mo), Glide (₹7,000/mo), and Soar (₹10,000/mo). Start free with a 14-day trial.',
  openGraph: {
    title: 'Pricing — RaptorFlow',
    description:
      'Simple, honest pricing. No hidden fees. Start free with a 14-day trial.',
    type: 'website',
  },
};

export default function PricingLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
