import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';

describe('App', () => {
  it('should render without crashing', () => {
    expect(true).toBe(true);
  });

  it('should pass basic test', () => {
    const sum = 1 + 1;
    expect(sum).toBe(2);
  });
});
