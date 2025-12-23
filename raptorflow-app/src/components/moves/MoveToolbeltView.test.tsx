import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { MoveToolbeltView } from './MoveToolbeltView';
import React from 'react';

describe('MoveToolbeltView', () => {
    it('renders tool icons and names', () => {
        const mockTools = ['Search', 'Copy'];
        render(<MoveToolbeltView tools={mockTools} />);

        expect(screen.getByText(/Search/i)).toBeDefined();
        expect(screen.getByText(/Copy/i)).toBeDefined();
    });

    it('renders verification status', () => {
        const mockTools = ['Search'];
        render(<MoveToolbeltView tools={mockTools} />);
        expect(screen.getByText(/Verified/i)).toBeDefined();
    });

    it('renders nothing when no tools provided', () => {
        const { container } = render(<MoveToolbeltView />);
        expect(container.firstChild).toBeNull();
    });
});
