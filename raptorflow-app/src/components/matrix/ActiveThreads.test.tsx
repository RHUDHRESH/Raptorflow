import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { ActiveThreads } from './ActiveThreads';
import React from 'react';

describe('ActiveThreads', () => {
    const mockThreads = [
        {
            id: 't1',
            agentName: 'Strategist-Alpha',
            task: '90-Day Arc Decomposition',
            status: 'thinking',
            startTime: '2025-12-23T10:30:00Z'
        },
        {
            id: 't2',
            agentName: 'Researcher-Beta',
            task: 'Competitor Pricing Scrape',
            status: 'executing',
            startTime: '2025-12-23T10:35:00Z'
        }
    ];

    it('renders the active agent pool heading', () => {
        render(<ActiveThreads threads={mockThreads} />);
        expect(screen.getByText(/Active Agent Pool/i)).toBeDefined();
    });

    it('displays agent names and tasks', () => {
        render(<ActiveThreads threads={mockThreads} />);
        expect(screen.getByText(/Strategist-Alpha/i)).toBeDefined();
        expect(screen.getByText(/Competitor Pricing Scrape/i)).toBeDefined();
    });

    it('shows current status for each agent', () => {
        render(<ActiveThreads threads={mockThreads} />);
        expect(screen.getByText(/thinking/i)).toBeDefined();
        expect(screen.getByText(/executing/i)).toBeDefined();
    });
});
