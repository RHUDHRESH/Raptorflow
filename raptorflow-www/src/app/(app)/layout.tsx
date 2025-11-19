// Authenticated app layout - dashboard, onboarding, etc.
export default function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-rf-bg">
      {children}
    </div>
  );
}

