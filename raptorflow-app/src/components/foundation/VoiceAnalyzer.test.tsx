import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { VoiceAnalyzer } from './VoiceAnalyzer';
import React from 'react';

describe('VoiceAnalyzer', () => {
  it('renders the voice analyzer component', () => {
    render(<VoiceAnalyzer />);
    expect(screen.getByText(/Voice Alignment Analyzer/i)).toBeDefined();
  });

  it('contains an input field for sample text', () => {
    render(<VoiceAnalyzer />);
    expect(
      screen.getByPlaceholderText(/Paste sample copy here/i)
    ).toBeDefined();
  });
});
