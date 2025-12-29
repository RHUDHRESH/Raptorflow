import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'About — RaptorFlow',
  description:
    'We exist to kill confusion. RaptorFlow is the marketing operating system that turns chaos into campaigns. Read our manifesto.',
  openGraph: {
    title: 'About — RaptorFlow',
    description:
      'We exist to kill confusion. Because the confused mind defaults to "no."',
    type: 'website',
  },
};

export default function AboutLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
