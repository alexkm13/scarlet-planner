import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getSchedule, addToSchedule, removeFromSchedule, clearSchedule } from '../api/client';
import type { ScheduleResponse, ScheduleConflict } from '../types';

export function useSchedule() {
  const queryClient = useQueryClient();

  const { data: schedule, isLoading } = useQuery<ScheduleResponse>({
    queryKey: ['schedule'],
    queryFn: getSchedule,
    staleTime: Infinity, // Schedule only changes via mutations
  });

  const addMutation = useMutation({
    mutationFn: addToSchedule,
    onSuccess: (data) => {
      queryClient.setQueryData(['schedule'], data.schedule);
    },
  });

  const removeMutation = useMutation({
    mutationFn: removeFromSchedule,
    onSuccess: (data) => {
      queryClient.setQueryData(['schedule'], data.schedule);
    },
  });

  const clearMutation = useMutation({
    mutationFn: clearSchedule,
    onSuccess: (data) => {
      queryClient.setQueryData(['schedule'], data.schedule);
    },
  });

  const addCourse = async (courseId: string): Promise<{ success: boolean; conflicts: ScheduleConflict[] }> => {
    try {
      const result = await addMutation.mutateAsync(courseId);
      return { success: result.success, conflicts: result.new_conflicts };
    } catch {
      return { success: false, conflicts: [] };
    }
  };

  const removeCourse = async (courseId: string): Promise<boolean> => {
    try {
      const result = await removeMutation.mutateAsync(courseId);
      return result.success;
    } catch {
      return false;
    }
  };

  const clear = async (): Promise<boolean> => {
    try {
      await clearMutation.mutateAsync();
      return true;
    } catch {
      return false;
    }
  };

  const isInSchedule = (courseId: string): boolean => {
    return schedule?.courses.some(c => c.id === courseId) ?? false;
  };

  return {
    schedule: schedule ?? {
      courses: [],
      events: [],
      conflicts: [],
      total_credits: 0,
      course_count: 0,
      has_conflicts: false,
    },
    isLoading,
    addCourse,
    removeCourse,
    clear,
    isInSchedule,
    isAdding: addMutation.isPending,
    isRemoving: removeMutation.isPending,
  };
}
