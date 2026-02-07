import { createContext, useContext, type ReactNode } from 'react';
import { useLocalSchedule } from '../hooks/useLocalSchedule';
import type { ScheduleResponse, ScheduleConflict } from '../types';

export interface ScheduleContextValue {
  schedule: ScheduleResponse;
  isLoading: boolean;
  addCourse: (courseId: string) => Promise<{ success: boolean; conflicts: ScheduleConflict[] }>;
  removeCourse: (courseId: string) => Promise<boolean>;
  clear: () => Promise<boolean>;
  isInSchedule: (courseId: string) => boolean;
  isAdding: boolean;
  isRemoving: boolean;
  handleExport: () => Promise<void>;
}

const ScheduleContext = createContext<ScheduleContextValue | null>(null);

export function ScheduleProvider({ children }: { children: ReactNode }) {
  const value = useLocalSchedule();
  return (
    <ScheduleContext.Provider value={value}>
      {children}
    </ScheduleContext.Provider>
  );
}

export function useSchedule(): ScheduleContextValue {
  const ctx = useContext(ScheduleContext);
  if (!ctx) {
    throw new Error('useSchedule must be used within ScheduleProvider');
  }
  return ctx;
}
