import { useQuery } from '@tanstack/react-query';
import { getSubjects } from '../api/client';

export function useSubjects() {
  return useQuery({
    queryKey: ['subjects'],
    queryFn: getSubjects,
    staleTime: 1000 * 60 * 60, // 1 hour - subjects rarely change
  });
}
