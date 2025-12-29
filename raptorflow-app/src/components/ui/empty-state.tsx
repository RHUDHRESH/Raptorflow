'use client';

/**
 * Abstract Empty State Artworks
 * Philosophy: "Calm, minimal geometric art that whispers 'something will be here'"
 */

export function EmptyStateArtwork({
  type = 'default',
}: {
  type?: 'campaigns' | 'notifications' | 'default';
}) {
  if (type === 'campaigns') {
    return (
      <svg
        viewBox="0 0 200 200"
        className="w-48 h-48 text-muted-foreground/20"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Abstract geometric target/campaign visual */}
        <circle
          cx="100"
          cy="100"
          r="80"
          stroke="currentColor"
          strokeWidth="0.5"
        />
        <circle
          cx="100"
          cy="100"
          r="60"
          stroke="currentColor"
          strokeWidth="0.5"
        />
        <circle
          cx="100"
          cy="100"
          r="40"
          stroke="currentColor"
          strokeWidth="0.5"
        />
        <circle
          cx="100"
          cy="100"
          r="20"
          stroke="currentColor"
          strokeWidth="1"
        />
        <line
          x1="100"
          y1="20"
          x2="100"
          y2="180"
          stroke="currentColor"
          strokeWidth="0.5"
          strokeDasharray="4 4"
        />
        <line
          x1="20"
          y1="100"
          x2="180"
          y2="100"
          stroke="currentColor"
          strokeWidth="0.5"
          strokeDasharray="4 4"
        />
      </svg>
    );
  }

  if (type === 'notifications') {
    return (
      <svg
        viewBox="0 0 200 200"
        className="w-48 h-48 text-muted-foreground/20"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Abstract sleeping bell */}
        <path
          d="M100 40 L140 90 L140 120 Q140 140 120 150 L80 150 Q60 140 60 120 L60 90 Z"
          stroke="currentColor"
          strokeWidth="1"
          fill="none"
        />
        <circle cx="100" cy="160" r="8" stroke="currentColor" strokeWidth="1" />
        {/* ZZZ */}
        <path
          d="M150 50 L165 50 L150 65 L165 65"
          stroke="currentColor"
          strokeWidth="0.75"
        />
        <path
          d="M160 35 L172 35 L160 47 L172 47"
          stroke="currentColor"
          strokeWidth="0.5"
        />
      </svg>
    );
  }

  // Default abstract geometric
  return (
    <svg
      viewBox="0 0 200 200"
      className="w-48 h-48 text-muted-foreground/20"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Abstract flow lines */}
      <path
        d="M20 100 Q50 60 100 100 T180 100"
        stroke="currentColor"
        strokeWidth="0.5"
      />
      <path
        d="M20 120 Q50 80 100 120 T180 120"
        stroke="currentColor"
        strokeWidth="0.75"
      />
      <path
        d="M20 140 Q50 100 100 140 T180 140"
        stroke="currentColor"
        strokeWidth="1"
      />
      <circle cx="100" cy="100" r="4" fill="currentColor" />
    </svg>
  );
}

export function EmptyState({
  title,
  description,
  action,
  type = 'default',
}: {
  title: string;
  description: string;
  action?: React.ReactNode;
  type?: 'campaigns' | 'notifications' | 'default';
}) {
  return (
    <div className="flex flex-col items-center justify-center py-24 px-8 text-center">
      <EmptyStateArtwork type={type} />
      <h3 className="mt-8 font-display text-2xl font-medium text-foreground">
        {title}
      </h3>
      <p className="mt-2 max-w-sm text-muted-foreground">{description}</p>
      {action && <div className="mt-6">{action}</div>}
    </div>
  );
}
