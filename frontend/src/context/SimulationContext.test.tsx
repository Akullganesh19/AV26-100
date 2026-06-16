import { describe, it, expect, vi } from 'vitest';
import { renderHook } from '@testing-library/react';
import { useSimulation } from './SimulationContext';

describe('useSimulation', () => {
  it('throws an error if used outside of a SimulationProvider', () => {
    // Suppress console.error for this test to avoid noisy output,
    // since React will complain about the error boundary / unhandled exception
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    expect(() => renderHook(() => useSimulation())).toThrowError(
      'useSimulation must be used within a SimulationProvider'
    );

    consoleSpy.mockRestore();
  });
});
