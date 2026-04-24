import type { LucideIcon } from "lucide-react";

interface EmptyStateProps {
  icon: LucideIcon;
  title: string;
  description: string;
  action?: React.ReactNode;
}

export function EmptyState({ icon: Icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-center">
      <div
        className="rounded-2xl border border-white/[0.08] p-5 mb-5"
        style={{ background: "rgba(255,255,255,0.03)" }}
      >
        <Icon className="w-8 h-8 text-slate-500" strokeWidth={1.5} />
      </div>
      <p className="text-white/80 font-semibold text-base mb-1">{title}</p>
      <p className="text-slate-400 text-sm max-w-xs leading-relaxed">{description}</p>
      {action && <div className="mt-5">{action}</div>}
    </div>
  );
}
