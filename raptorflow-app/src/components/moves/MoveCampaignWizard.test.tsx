import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MoveCampaignWizard } from './MoveCampaignWizard';
import * as api from '@/lib/api';

// Create a mock function for the API
const mockGenerate = vi.fn();

// Mock the API module
vi.mock('@/lib/api', () => ({
  generateCouncilProposal: (...args: any[]) => mockGenerate(...args),
  createMoveFromProposal: vi.fn(),
  createCampaignFromProposal: vi.fn(),
}));

// Mock toast
vi.mock('sonner', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

describe('MoveCampaignWizard', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders type selection initially', () => {
    render(<MoveCampaignWizard />);
    expect(screen.getByText(/What are we building/i)).toBeDefined();
    expect(screen.getByText('Single Move')).toBeDefined();
  });

  it('navigates to input step for Move', async () => {
    render(<MoveCampaignWizard />);
    fireEvent.click(screen.getByText('Single Move'));

    const nextBtn = screen.getByText(/Next Step/i);
    fireEvent.click(nextBtn);

    await waitFor(() => {
      expect(screen.getByText('Define the Move')).toBeDefined();
    });
  });

  it('validates input before enabling submit', async () => {
    render(<MoveCampaignWizard />);
    // To Step 2
    fireEvent.click(screen.getByText('Single Move'));
    fireEvent.click(screen.getByText(/Next Step/i));
    await waitFor(() => screen.getByText('Define the Move'));

    const summonBtn = screen.getByText(/Summon Council/i);
    expect(summonBtn).toBeDisabled();

    // Valid input
    fireEvent.change(
      screen.getByPlaceholderText(/Generate 10 qualified leads/i),
      { target: { value: 'Get some leads' } }
    );
    fireEvent.change(screen.getByPlaceholderText(/targeting Series A/i), {
      target: { value: 'Startup founders' },
    });

    await waitFor(() => {
      expect(summonBtn).not.toBeDisabled();
    });
  });

  it('displays results after API call', async () => {
    const mockResponse = {
      type: 'move',
      strategicDecree: 'Test Decree',
      confidence: 90,
      risks: [],
      debateTranscript: [],
      rejectedPaths: [],
      moves: [
        {
          id: 'm1',
          title: 'Test Move',
          description: 'Desc',
          type: 'post',
          toolRequirements: [],
          confidenceScore: 90,
        },
      ],
    };
    mockGenerate.mockResolvedValue(mockResponse);

    render(<MoveCampaignWizard />);

    // Go to Step 2
    fireEvent.click(screen.getByText('Single Move'));
    fireEvent.click(screen.getByText(/Next Step/i));
    await waitFor(() => screen.getByText('Define the Move'));

    // Fill Input
    fireEvent.change(
      screen.getByPlaceholderText(/Generate 10 qualified leads/i),
      { target: { value: 'Get some leads' } }
    );
    fireEvent.change(screen.getByPlaceholderText(/targeting Series A/i), {
      target: { value: 'Startup founders' },
    });

    // Submit
    const summonBtn = screen.getByText(/Summon Council/i);
    fireEvent.click(summonBtn);

    // Verify Loading
    await waitFor(() => {
      expect(screen.getByText(/Council is deliberating/i)).toBeDefined();
    });

    // Verify Result
    await waitFor(() => {
      expect(screen.getByText(/Test Decree/i)).toBeDefined();
      expect(screen.getByText('Test Move')).toBeDefined();
    });
  });
});
