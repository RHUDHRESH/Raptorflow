"use client";

import { useState } from "react";
import { X, Sparkles, Loader2, Target, Users, Brain } from "lucide-react";
import { BlueprintCard } from "@/components/ui/BlueprintCard";
import { BlueprintButton, SecondaryButton } from "@/components/ui/BlueprintButton";
import { RICP } from "@/types/foundation";
import { apiClient } from "@/lib/api/client";

interface DeriveCohortModalProps {
    isOpen: boolean;
    onClose: () => void;
    onDerived: (ricp: RICP) => void;
}

export function DeriveCohortModal({ isOpen, onClose, onDerived }: DeriveCohortModalProps) {
    const [cohortName, setCohortName] = useState("");
    const [isDeriving, setIsDeriving] = useState(false);
    const [error, setError] = useState<string | null>(null);

    if (!isOpen) return null;

    const handleDerive = async () => {
        if (!cohortName.trim()) return;

        setIsDeriving(true);
        setError(null);

        try {
            const response = await apiClient.deriveTrinity(cohortName);
            
            // Handle both direct object and wrapped data object
            const ricp: RICP = response.data || response;
            
            if (!ricp || !ricp.name) {
                throw new Error("Invalid response from derivation engine");
            }

            onDerived(ricp);
            onClose();
        } catch (err: any) {
            console.error(err);
            setError(err.message || "An unexpected error occurred during trinity derivation");
        } finally {
            setIsDeriving(false);
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <div className="fixed inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose} />
            
            <div className="relative w-full max-w-lg bg-[var(--paper)] rounded-[var(--radius)] border border-[var(--structure)] shadow-2xl overflow-hidden animate-in zoom-in-95 duration-200">
                <div className="p-6 border-b border-[var(--structure)] flex justify-between items-center">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-[var(--blueprint-light)] flex items-center justify-center">
                            <Sparkles className="text-[var(--blueprint)]" size={20} />
                        </div>
                        <div>
                            <h2 className="font-serif text-xl text-[var(--ink)]">Derive New Cohort</h2>
                            <p className="text-xs text-[var(--ink-muted)] font-technical uppercase">SYS.TRINITY_GENERATOR</p>
                        </div>
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-[var(--surface)] rounded-lg transition-colors">
                        <X size={20} className="text-[var(--ink-muted)]" />
                    </button>
                </div>

                <div className="p-8 space-y-6">
                    <div className="space-y-2">
                        <label className="text-xs font-bold text-[var(--ink-muted)] uppercase tracking-wider">Cohort Name</label>
                        <input
                            type="text"
                            value={cohortName}
                            onChange={(e) => setCohortName(e.target.value)}
                            placeholder="e.g. Bootstrapped SaaS Founders"
                            className="w-full p-4 bg-[var(--surface)] border border-[var(--structure)] rounded-xl focus:border-[var(--blueprint)] outline-none transition-all text-lg"
                            autoFocus
                        />
                        <p className="text-sm text-[var(--ink-secondary)]">
                            Enter a descriptive name. RaptorFlow will derive the demographic structure (ICP) and the psychological persona automatically.
                        </p>
                    </div>

                    {error && (
                        <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-red-600 text-sm">
                            {error}
                        </div>
                    )}

                    <div className="grid grid-cols-3 gap-4 pt-4">
                        <StepItem icon={Users} label="Cohort" />
                        <StepItem icon={Target} label="ICP" />
                        <StepItem icon={Brain} label="Persona" />
                    </div>
                </div>

                <div className="p-6 bg-[var(--surface)] border-t border-[var(--structure)] flex justify-end gap-3">
                    <SecondaryButton onClick={onClose} disabled={isDeriving}>
                        Cancel
                    </SecondaryButton>
                    <BlueprintButton 
                        onClick={handleDerive} 
                        disabled={!cohortName.trim() || isDeriving}
                        className="min-w-[140px]"
                    >
                        {isDeriving ? (
                            <>
                                <Loader2 className="mr-2 animate-spin" size={18} />
                                Deriving...
                            </>
                        ) : (
                            <>
                                <Sparkles className="mr-2" size={18} />
                                Derive Trinity
                            </>
                        )}
                    </BlueprintButton>
                </div>
            </div>
        </div>
    );
}

function StepItem({ icon: Icon, label }: { icon: any, label: string }) {
    return (
        <div className="flex flex-col items-center gap-2 p-3 bg-[var(--paper)] rounded-xl border border-[var(--structure-subtle)]">
            <Icon size={20} className="text-[var(--ink-muted)]" />
            <span className="text-[10px] font-bold text-[var(--ink-muted)] uppercase tracking-widest">{label}</span>
        </div>
    );
}
