'use client';

import { useState, useEffect, useCallback } from 'react';
import { Move, CouncilResponse } from '@/lib/campaigns-types';
import { getMove } from '@/lib/campaigns';
import { getMoveRationale, updateMove, updateMoveTasks } from '@/lib/api';
import { toast } from 'sonner';

export function useMove(moveId: string) {
    const [move, setMove] = useState<Move | null>(null);
    const [rationale, setRationale] = useState<CouncilResponse | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [isRefreshing, setIsRefreshing] = useState(false);
    const [error, setError] = useState<Error | null>(null);

    const fetchData = useCallback(async (isRefresh = false) => {
        if (isRefresh) setIsRefreshing(true);
        else setIsLoading(true);

        try {
            const [moveData, rationaleData] = await Promise.all([
                getMove(moveId),
                getMoveRationale(moveId),
            ]);

            if (!moveData) throw new Error('Move not found');

            setMove(moveData);
            setRationale(rationaleData);
            setError(null);
        } catch (err) {
            setError(err instanceof Error ? err : new Error('Failed to fetch move data'));
            console.error('useMove error:', err);
        } finally {
            setIsLoading(false);
            setIsRefreshing(false);
        }
    }, [moveId]);

    useEffect(() => {
        if (moveId) fetchData();
    }, [moveId, fetchData]);

    const refresh = () => fetchData(true);

    const updateFields = async (updates: Partial<Move>) => {
        if (!move) return;

        // Optimistic update
        const previousMove = { ...move };
        setMove({ ...move, ...updates });

        try {
            await updateMove(move.id, updates);
            toast.success('Move updated');
        } catch (err) {
            setMove(previousMove);
            toast.error('Failed to update move');
        }
    };

    const toggleTask = async (taskId: string) => {
        if (!move) return;

        const updatedChecklist = move.checklist.map(item =>
            item.id === taskId ? { ...item, completed: !item.completed } : item
        );

        // Optimistic update
        const previousMove = { ...move };
        setMove({ ...move, checklist: updatedChecklist });

        try {
            await updateMoveTasks(move.id, updatedChecklist);
        } catch (err) {
            setMove(previousMove);
            toast.error('Failed to update task');
        }
    };

    return {
        move,
        rationale,
        isLoading,
        isRefreshing,
        error,
        refresh,
        updateFields,
        toggleTask,
    };
}
