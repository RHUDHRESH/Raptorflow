import { cn } from "../../../utils/cn";

export const SummaryCard = ({ label, value, helper, accent }) => (
    <div className="group relative overflow-hidden rounded-3xl border border-black/5 bg-white p-5 shadow-[0_2px_8px_rgba(0,0,0,0.04)] transition-all hover:shadow-[0_4px_12px_rgba(0,0,0,0.06)]">
        <div className="relative z-10">
            <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-neutral-400">{label}</p>
            <p className="mt-1 text-3xl font-semibold text-neutral-900 tracking-tight">{value}</p>
            {helper && <p className="mt-1 text-xs font-medium text-neutral-500">{helper}</p>}
            {accent && <span className="mt-3 inline-flex rounded-full bg-black px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider text-white">{accent}</span>}
        </div>
        <div className="absolute -right-6 -top-6 h-24 w-24 rounded-full bg-neutral-50 transition-transform group-hover:scale-110" />
    </div>
);
