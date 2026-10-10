import { useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import { useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../api/client';
import { useSimulation } from '../context/SimulationContext';

// Markov chain transition frequencies: { fromPath: { toPath: count } }
type Transitions = Record<string, Record<string, number>>;

export function useOracle() {
  const location = useLocation();
  const queryClient = useQueryClient();
  const prevPathRef = useRef<string | null>(null);
  const { isSimulating, activeSimId } = useSimulation();

  useEffect(() => {
    const currentPath = location.pathname;
    const prevPath = prevPathRef.current;

    if (prevPath && prevPath !== currentPath) {
      // Update transition history
      const stored = localStorage.getItem('oracle_nav_history');
      const transitions: Transitions = stored ? JSON.parse(stored) : {};

      if (!transitions[prevPath]) {
        transitions[prevPath] = {};
      }
      transitions[prevPath][currentPath] = (transitions[prevPath][currentPath] || 0) + 1;
      localStorage.setItem('oracle_nav_history', JSON.stringify(transitions));
    }
    prevPathRef.current = currentPath;

    // Predict next path based on history
    const stored = localStorage.getItem('oracle_nav_history');
    if (stored) {
      const transitions: Transitions = JSON.parse(stored);
      const possibleNext = transitions[currentPath];

      if (possibleNext) {
        let likelyNext = '';
        let maxCount = 0;
        for (const [path, count] of Object.entries(possibleNext)) {
          if (count > maxCount) {
            maxCount = count;
            likelyNext = path;
          }
        }

        if (likelyNext) {
          console.debug(`🛸 Oracle predicts next route: ${likelyNext} (confidence: ${maxCount})`);

          // Prefetch data based on prediction
          if (likelyNext === '/map') {
            queryClient.prefetchQuery({
              queryKey: ['choropleth-data', isSimulating, activeSimId],
              queryFn: async () => {
                const url = isSimulating
                  ? `/districts`
                  : `/districts`;
                const response = await apiClient.get(url);
                return response.data;
              }
            });
          } else if (likelyNext === '/alerts') {
            queryClient.prefetchQuery({
              queryKey: ['tactical-alerts', isSimulating, activeSimId],
              queryFn: async () => {
                const url = isSimulating
                  ? `/alerts?simulation_id=${activeSimId}`
                  : `/alerts`;
                const response = await apiClient.get(url);
                return response.data;
              }
            });
          } else if (likelyNext === '/') {
             queryClient.prefetchQuery({
              queryKey: ['dashboard-stats'],
              queryFn: async () => {
                const response = await apiClient.get('/districts/stats');
                return response.data;
              }
            });
          }
        }
      }
    }
  }, [location.pathname, queryClient, isSimulating, activeSimId]);
}
