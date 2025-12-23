import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { CompetitorRadar } from './CompetitorRadar';
import React from 'react';

describe('CompetitorRadar', () => {
    const mockData = [
        {
            subject: 'Feature A',
            A: 120,
            B: 110,
            fullMark: 150
        },
        {
            subject: 'Feature B',
            A: 98,
            B: 130,
            fullMark: 150
        },
    ];

    it('renders the competitor radar chart', () => {
        render(<CompetitorRadar data={mockData} />);
        expect(screen.getByText(/Competitor Comparison/i)).toBeDefined();
    });

    it('displays labels for the radar pillars', () => {
        render(<CompetitorRadar data={mockData} />);
        expect(screen.getByText(/Feature A/i)).toBeDefined();
        expect(screen.getByText(/Feature B/i)).toBeDefined();
    });
});
