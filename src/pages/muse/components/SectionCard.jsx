import { cn } from "../../../utils/cn";

export const SectionCard = ({ title, subtitle, children, actions, className }) => (
    <div className={cn("group flex flex-col gap-4 rounded-3xl border border-black/5 bg-white p-5 shadow-[0_2px_8px_rgba(0,0,0,0.04)] transition-all hover:shadow-[0_4px_12px_rgba(0,0,0,0.06)]", className)}>
        {(title || actions) && (
            <div className="flex items-center justify-between gap-3">
                <div>
                    {title && <h3 className="text-[11px] font-bold uppercase tracking-[0.2em] text-neutral-400">{title}</h3>}
                    {subtitle && <p className="mt-0.5 text-sm font-semibold text-neutral-900">{subtitle}</p>}
                </div>
                {actions}
            </div>
        )}
        <div className="relative">
            {children}
        </div>
    </div>
);
