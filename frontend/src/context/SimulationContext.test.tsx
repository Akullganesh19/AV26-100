import React from 'react';
import { renderHook, act } from '@testing-library/react';
import { expect, test, describe } from 'vitest';
import { SimulationProvider, useSimulation } from './SimulationContext';

describe('SimulationContext', () => {
  test('throws error if used outside of provider', () => {
    expect(() => renderHook(() => useSimulation())).toThrow(
      'useSimulation must be used within a SimulationProvider'
    );
  });

  test('provides default state', () => {
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <SimulationProvider>{children}</SimulationProvider>
    );

    const { result } = renderHook(() => useSimulation(), { wrapper });

    expect(result.current.isSimulating).toBe(false);
    expect(result.current.activeSimId).toBeNull();
  });

  test('startSimulation updates state correctly', () => {
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <SimulationProvider>{children}</SimulationProvider>
    );

    const { result } = renderHook(() => useSimulation(), { wrapper });

    act(() => {
      result.current.startSimulation('sim-123');
    });

    expect(result.current.isSimulating).toBe(true);
    expect(result.current.activeSimId).toBe('sim-123');
  });

  test('stopSimulation updates state correctly', () => {
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <SimulationProvider>{children}</SimulationProvider>
    );

    const { result } = renderHook(() => useSimulation(), { wrapper });

    act(() => {
      result.current.startSimulation('sim-123');
    });

    expect(result.current.isSimulating).toBe(true);
    expect(result.current.activeSimId).toBe('sim-123');

    act(() => {
      result.current.stopSimulation();
    });

    expect(result.current.isSimulating).toBe(false);
    expect(result.current.activeSimId).toBeNull();
  });
});
