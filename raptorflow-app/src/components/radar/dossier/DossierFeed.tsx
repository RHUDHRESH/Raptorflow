'use client';

import React from 'react';
import { Dossier } from '../types';
import { DossierCard } from './DossierCard';
import { BookOpen } from 'lucide-react';

interface DossierFeedProps {
    dossiers: Dossier[];
}

export function DossierFeed({ dossiers }: DossierFeedProps) {
    if (dossiers.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center py-24 text-center border border-dashed border-border/60 rounded-xl bg-card/30">
                <BookOpen className="h-8 w-8 text-muted-foreground/30 mb-4" />
                <p className="text-muted-foreground font-medium">No dossiers available.</p>
                <p className="text-sm text-muted-foreground/60 mt-1">Dossiers are generated weekly.</p>
            </div>
        );
    }

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {dossiers.map((dossier) => (
                <DossierCard key={dossier.id} dossier={dossier} />
            ))}
        </div>
    );
}
