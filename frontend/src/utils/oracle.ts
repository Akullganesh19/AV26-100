import { useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import { useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../api/client';

// Markov Chain transition counts: Record<CurrentRoute, Record<NextRoute, Count>>
type TransitionMatrix = Record<string, Record<string, number>>;

const STORAGE_KEY = 'oracle_route_transitions';
const CONFIDENCE_THRESHOLD = 0.4; // 40% confidence needed to prefetch

export const useOraclePrefetch = () => {
  const location = useLocation();
  const queryClient = useQueryClient();
  const lastPathRef = useRef<string | null>(null);

  useEffect(() => {
    const currentPath = location.pathname;

    // 1. Record the transition from the previous route to the current route
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      const matrix: TransitionMatrix = stored ? JSON.parse(stored) : {};

      if (lastPathRef.current && lastPathRef.current !== currentPath) {
        const from = lastPathRef.current;
        const to = currentPath;

        if (!matrix[from]) matrix[from] = {};
        matrix[from][to] = (matrix[from][to] || 0) + 1;

        localStorage.setItem(STORAGE_KEY, JSON.stringify(matrix));
      }

      lastPathRef.current = currentPath;


      // Cleanup: Limit size to prevent unbounded growth from dynamic routes
      const MAX_ROUTES = 50;
      const keys = Object.keys(matrix);
      if (keys.length > MAX_ROUTES) {
          // Remove the oldest/least used? For simplicity, we just delete the first key
          delete matrix[keys[0]];
      }


      if (matrix[currentPath]) {
        const transitions = matrix[currentPath];
        const totalTransitions = Object.values(transitions).reduce((sum, count) => sum + count, 0);

        let mostLikelyNext: string | null = null;
        let highestProbability = 0;

        for (const [nextRoute, count] of Object.entries(transitions)) {
          const probability = count / totalTransitions;
          if (probability > highestProbability) {
            highestProbability = probability;
            mostLikelyNext = nextRoute;
          }
        }

        // If we are confident enough, prefetch the data for the predicted next route
        if (mostLikelyNext && highestProbability >= CONFIDENCE_THRESHOLD) {
          console.log(`[Oracle] Predicting next route: ${mostLikelyNext} (${Math.round(highestProbability * 100)}% confidence). Prefetching data...`);
          prefetchDataForRoute(mostLikelyNext, queryClient);
        }
      }
    } catch (e) {
      console.warn('[Oracle] Failed to process prediction matrix', e);
    }
  }, [location.pathname, queryClient]);
};

// Route-specific prefetching logic
const prefetchDataForRoute = (route: string, queryClient: any) => {

  if (route === '/map') {
    // Prefetch choropleth data for Strategic Map
    queryClient.prefetchQuery({
      queryKey: ['choropleth-data', false, null], // Assuming not simulating by default
      queryFn: async () => {
        const response = await apiClient.get(`/districts`);
        return response.data;
      }
    });
  } else if (route === '/alerts') {
    // Prefetch tactical alerts
    queryClient.prefetchQuery({
      queryKey: ['tactical-alerts'],
      queryFn: async () => {
        const response = await apiClient.get(`/alerts`);
        return response.data;
      }
    });
  } else if (route === '/') {
     // Prefetch dashboard stats
     queryClient.prefetchQuery({
      queryKey: ['dashboard-stats'],
      queryFn: async () => {
        const response = await apiClient.get(`/districts/stats`);
        return response.data;
      }
    });
  } else if (route === '/simulations') {
     // Prefetch simulation scenarios
     queryClient.prefetchQuery({
      queryKey: ['sim-scenarios'],
      queryFn: async () => {
        const response = await apiClient.get(`/scenarios/`);
        return response.data;
      }
    });
  }
};
