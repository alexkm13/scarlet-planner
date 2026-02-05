import { useQuery } from '@tanstack/react-query';
import { getTerms } from '../api/client';

export function useTerms() {
  return useQuery({
    queryKey: ['terms'],
    queryFn: getTerms,
    staleTime: 1000 * 60 * 60, // 1 hour
  });
}
