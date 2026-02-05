import { useQuery } from '@tanstack/react-query';
import { searchCourses, getCourse } from '../api/client';

interface UseCoursesParams {
  q?: string;
  subject?: string[];
  term?: string[];
  hub?: string[];
  status?: string[];
  limit?: number;
  offset?: number;
  grouped?: boolean;
}

export function useCourses(params: UseCoursesParams) {
  return useQuery({
    queryKey: ['courses', params],
    queryFn: () => searchCourses(params),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

export function useCourse(courseId: string | null) {
  return useQuery({
    queryKey: ['course', courseId],
    queryFn: () => getCourse(courseId!),
    enabled: !!courseId,
    staleTime: 1000 * 60 * 5,
  });
}
