import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { AlertCenter, SystemAlert } from './AlertCenter';
import React from 'react';

describe('AlertCenter', () => {
    const mockAlerts: SystemAlert[] = [
        {
            id: '1',
            severity: 'critical',
            message: 'Vertex AI Quota Exceeded',
            timestamp: '2025-12-23T10:00:00Z',
            component: 'Inference'
        },
        {
            id: '2',
            severity: 'warning',
            message: 'High latency detected in Supabase',
            timestamp: '2025-12-23T10:05:00Z',
            component: 'Database'
        }
    ];

    it('renders the alert center heading', () => {
        render(<AlertCenter alerts={mockAlerts} />);
        expect(screen.getByText(/System Alerts/i)).toBeDefined();
    });

    it('displays alert messages correctly', () => {
        render(<AlertCenter alerts={mockAlerts} />);
        expect(screen.getByText(/Vertex AI Quota Exceeded/i)).toBeDefined();
        expect(screen.getByText(/High latency detected in Supabase/i)).toBeDefined();
    });

    it('shows the component source for each alert', () => {
        render(<AlertCenter alerts={mockAlerts} />);
        expect(screen.getByText(/Inference/i)).toBeDefined();
        expect(screen.getByText(/Database/i)).toBeDefined();
    });
});
