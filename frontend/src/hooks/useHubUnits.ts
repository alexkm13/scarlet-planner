import { useQuery } from '@tanstack/react-query';
import { getHubUnits } from '../api/client';

export function useHubUnits() {
  return useQuery({
    queryKey: ['hubUnits'],
    queryFn: getHubUnits,
    staleTime: 1000 * 60 * 60, // 1 hour
  });
}
