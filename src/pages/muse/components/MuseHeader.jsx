import { Sparkles, ChevronsUpDown, Palette } from "lucide-react";
import { cn } from "../../../utils/cn";

export const MuseHeader = ({ week, setWeek, brand, setBrand, modelRoute, title, subtitle }) => (
    <div className="sticky top-0 z-30 border-b border-black/5 bg-white/80 px-6 py-4 backdrop-blur-xl transition-all">
        <div className="mx-auto flex max-w-[1600px] items-center justify-between">
            <div>
                <div className="flex items-center gap-3">
                    <h1 className="text-xs font-bold uppercase tracking-[0.3em] text-neutral-400">Muse</h1>
                    {title && (
                        <>
                            <span className="h-4 w-px bg-neutral-200"></span>
                            <span className="text-xs font-medium text-neutral-500">{title}</span>
                        </>
                    )}
                </div>
                {subtitle && <p className="mt-1 text-sm font-semibold text-neutral-900">{subtitle}</p>}
            </div>
            <div className="flex items-center gap-3">
                <button className="group inline-flex items-center gap-2 rounded-full border border-black/5 bg-white px-4 py-2 text-xs font-semibold text-neutral-700 shadow-sm transition-all hover:border-black/10 hover:shadow-md active:scale-95">
                    <Sparkles size={14} className="text-purple-500" />
                    <span className="text-neutral-500">Model:</span>
                    <span className="text-neutral-900">{modelRoute}</span>
                </button>
                <div className="h-6 w-px bg-neutral-200"></div>
                <button className="group inline-flex items-center gap-2 rounded-full border border-black/5 bg-white px-4 py-2 text-xs font-semibold text-neutral-700 shadow-sm transition-all hover:border-black/10 hover:shadow-md active:scale-95">
                    <ChevronsUpDown size={14} className="text-neutral-400 group-hover:text-neutral-600" /> {week}
                </button>
                <button className="group inline-flex items-center gap-2 rounded-full border border-black/5 bg-white px-4 py-2 text-xs font-semibold text-neutral-700 shadow-sm transition-all hover:border-black/10 hover:shadow-md active:scale-95">
                    <Palette size={14} className="text-neutral-400 group-hover:text-neutral-600" /> {brand}
                </button>
            </div>
        </div>
    </div>
);
