import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { FoundationTimeline } from './FoundationTimeline';
import React from 'react';

describe('FoundationTimeline', () => {
    const mockEvents = [
        {
            id: '1',
            date: '2025-12-23T10:00:00Z',
            type: 'voice',
            description: 'Updated brand voice to "Calm & Premium"',
            author: 'System'
        },
        {
            id: '2',
            date: '2025-12-22T15:30:00Z',
            type: 'positioning',
            description: 'Refined target audience to include SMB SaaS founders',
            author: 'Founder'
        }
    ];

    it('renders the foundation timeline', () => {
        render(<FoundationTimeline events={mockEvents} />);
        expect(screen.getByText(/Brand History/i)).toBeDefined();
    });

    it('displays event descriptions correctly', () => {
        render(<FoundationTimeline events={mockEvents} />);
        expect(screen.getByText(/Updated brand voice to "Calm & Premium"/i)).toBeDefined();
        expect(screen.getByText(/Refined target audience to include SMB SaaS founders/i)).toBeDefined();
    });
});
