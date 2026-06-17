import { useQueryClient } from '@tanstack/react-query';
import { useCallback } from 'react';
import { apiClient } from '../api/client';
import { useAuthStore } from '../store/authStore';

/**
 * Oracle Predictive Intelligence Engine 🛸
 * Anticipates user behavior and prefetches required context to ensure zero-latency routing.
 */
export const useOracle = () => {
  const queryClient = useQueryClient();
  const isAuthenticated = useAuthStore(state => state.isAuthenticated);

  // Safely fetch data. Degrades gracefully if unauthorized or error occurs.
  const safePrefetch = useCallback(async (queryKey: any[], url: string) => {
    if (!isAuthenticated) return;

    // Only prefetch if we don't already have fresh data
    const existing = queryClient.getQueryData(queryKey);
    if (existing) return;

    try {
      await queryClient.prefetchQuery({
        queryKey,
        queryFn: async () => {
          const { data } = await apiClient.get(url);
          return data;
        },
        staleTime: 60000 // Cache for 1 minute to avoid spamming
      });
      console.log(`[Oracle 🛸] Prefetched: ${queryKey[0]}`);
    } catch (e) {
      // Degrade gracefully - normal flow will handle errors later
      console.debug(`[Oracle 🛸] Prefetch failed for ${queryKey[0]}, degrading gracefully.`);
    }
  }, [queryClient, isAuthenticated]);

  /**
   * Intent-Based Route Prefetching
   * Triggered when a user hovers or moves toward a navigation link.
   */
  const prefetchRouteContext = useCallback((path: string) => {
    switch (path) {
      case '/':
        safePrefetch(['dashboard-stats'], '/districts/stats');
        break;
      case '/map':
        safePrefetch(['choropleth-data', false, null], '/districts');
        break;
      case '/alerts':
        safePrefetch(['tactical-alerts', false, null], '/alerts');
        break;
      case '/simulations':
        safePrefetch(['sim-scenarios'], '/scenarios/');
        break;
    }
  }, [safePrefetch]);

  /**
   * Behavioral Next-Action Prediction
   * Triggered AFTER a significant user action completes.
   */

  // Predict: After a HIGH risk diagnosis, the user will immediately want to see the broader
  // strategic map or tactical alerts to contextualize the local threat.
  const predictPostHighRiskDiagnosis = useCallback(() => {
    console.log("[Oracle 🛸] High risk clinical diagnosis detected. Predicting map/alert context required.");
    safePrefetch(['choropleth-data', false, null], '/districts');
    safePrefetch(['tactical-alerts', false, null], '/alerts');
  }, [safePrefetch]);

  // Predict: After acknowledging a tactical alert, the user will likely want to simulate
  // scenarios to understand mitigation strategies.
  const predictPostAlertAcknowledge = useCallback(() => {
    console.log("[Oracle 🛸] Tactical alert acknowledged. Predicting scenario simulation required.");
    safePrefetch(['sim-scenarios'], '/scenarios/');
  }, [safePrefetch]);

  return {
    prefetchRouteContext,
    predictPostHighRiskDiagnosis,
    predictPostAlertAcknowledge
  };
};
