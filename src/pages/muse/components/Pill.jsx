import { cn } from "../../../utils/cn";

export const Pill = ({ children, className }) => (
    <span className={cn("inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[11px] font-medium tracking-wide transition-colors", className)}>
        {children}
    </span>
);
