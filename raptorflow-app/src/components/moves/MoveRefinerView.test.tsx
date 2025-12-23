import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { MoveRefinerView } from './MoveRefinerView';
import React from 'react';

describe('MoveRefinerView', () => {
    it('renders refinement data correctly', () => {
        const mockData = {
            estimated_effort: 'High',
            deadline: '2025-12-31',
            rationale: 'Strategic alignment test'
        };
                render(<MoveRefinerView data={mockData} />);

                expect(screen.getAllByText(/High/i).length).toBeGreaterThan(0);
                expect(screen.getByText(/2025-12-31/i)).toBeDefined();

        expect(screen.getByText(/Strategic alignment test/i)).toBeDefined();
    });

    it('renders empty state when no data provided', () => {
        render(<MoveRefinerView />);
        expect(screen.getByText(/Agentic refinement data is not available/i)).toBeDefined();
    });
});
