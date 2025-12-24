'use client';

import { useState, useEffect, useCallback } from 'react';

export type InferenceStatus = 'idle' | 'generating' | 'complete' | 'error' | 'awaiting_approval';

interface StatusResponse {
    status: string;
    orchestrator_status?: string;
    messages: string[];
}

export function useInferenceStatus(campaignId: string | null) {
    const [status, setStatus] = useState<InferenceStatus>('idle');
    const [messages, setMessages] = useState<string[]>([]);
    const [error, setError] = useState<string | null>(null);

    const checkStatus = useCallback(async () => {
        if (!campaignId) return;

        try {
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
            const response = await fetch(`${apiUrl}/api/v1/campaigns/generate-arc/${campaignId}/status`);

            if (!response.ok) {
                if (response.status === 404) {
                    // Not found might mean it hasn't started yet or doesn't exist
                    return;
                }
                throw new Error('Failed to fetch status');
            }

            const data: StatusResponse = await response.json();
            setMessages(data.messages);

            if (data.status === 'planning') {
                setStatus('generating');
            } else if (data.status === 'awaiting_approval') {
                setStatus('awaiting_approval');
            } else if (data.status === 'monitoring' || data.status === 'complete') {
                setStatus('complete');
            } else if (data.status === 'error') {
                setStatus('error');
            }
        } catch (err) {
            console.error('Error polling status:', err);
            setError(err instanceof Error ? err.message : 'An unknown error occurred');
        }
    }, [campaignId]);

    useEffect(() => {
        if (!campaignId || status === 'complete' || status === 'error') return;

        const interval = setInterval(checkStatus, 3000); // Poll every 3 seconds
        checkStatus(); // Initial check

        return () => clearInterval(interval);
    }, [campaignId, status, checkStatus]);

    return { status, messages, error, refresh: checkStatus };
}
