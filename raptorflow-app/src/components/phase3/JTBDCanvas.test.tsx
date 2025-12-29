import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { JTBDCanvas } from './JTBDCanvas';

vi.mock('next/font/google', () => ({
  Playfair_Display: () => ({
    className: 'mock-playfair',
  }),
}));

describe('JTBDCanvas component', () => {
  it('renders all job inputs', () => {
    render(
      <JTBDCanvas functional="" emotional="" social="" onChange={() => {}} />
    );

    expect(screen.getByLabelText(/Functional Job/i)).toBeTruthy();
    expect(screen.getByLabelText(/Emotional Job/i)).toBeTruthy();
    expect(screen.getByLabelText(/Social Job/i)).toBeTruthy();
  });

  it('calls onChange when typing', () => {
    const handleChange = vi.fn();
    render(
      <JTBDCanvas
        functional=""
        emotional=""
        social=""
        onChange={handleChange}
      />
    );

    const input = screen.getByLabelText(/Functional Job/i);
    fireEvent.change(input, { target: { value: 'New Task' } });

    expect(handleChange).toHaveBeenCalledWith('functional', 'New Task');
  });
});
