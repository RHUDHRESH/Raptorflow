import { GroundworkLayout } from '@/components/groundwork/GroundworkLayout';

export default function GroundworkLayoutWrapper({
  children,
}: {
  children: React.ReactNode;
}) {
  return <GroundworkLayout>{children}</GroundworkLayout>;
}

