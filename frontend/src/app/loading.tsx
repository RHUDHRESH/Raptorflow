export default function Loading() {
    return (
        <div className="w-full h-[calc(100vh-64px)] flex items-center justify-center bg-[var(--paper)]">
            <div className="flex flex-col items-center gap-4">
                <div className="relative w-12 h-12">
                    <div className="absolute inset-0 border-2 border-[var(--border)] rounded-full opactiy-20" />
                    <div className="absolute inset-0 border-2 border-t-[var(--blueprint)] border-r-transparent border-b-transparent border-l-transparent rounded-full animate-spin" />
                </div>
                <span className="font-technical text-xs text-[var(--muted)] tracking-widest animate-pulse">LOADING SYSTEM...</span>
            </div>
        </div>
    );
}
