import { useCallback, useEffect, useState } from 'react';
import { getCourse, getCoursesBatch, exportSchedule } from '../api/client';
import { buildScheduleResponse, detectConflicts } from '../lib/schedule';
import type { Course, ScheduleResponse, ScheduleConflict } from '../types';

const STORAGE_KEY = 'bu-course-schedule';

function loadCourseIds(): string[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function saveCourseIds(ids: string[]): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(ids));
}

const EMPTY_SCHEDULE: ScheduleResponse = {
  courses: [],
  events: [],
  conflicts: [],
  total_credits: 0,
  course_count: 0,
  has_conflicts: false,
};

export function useLocalSchedule() {
  const [courseIds, setCourseIds] = useState<string[]>(() => loadCourseIds());
  const [courses, setCourses] = useState<Course[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isAdding, setIsAdding] = useState(false);
  const [isRemoving, setIsRemoving] = useState(false);

  // Persist when courseIds change
  useEffect(() => {
    saveCourseIds(courseIds);
  }, [courseIds]);

  // Fetch course data when courseIds change
  useEffect(() => {
    if (courseIds.length === 0) {
      setCourses([]);
      setIsLoading(false);
      return;
    }

    let cancelled = false;
    setIsLoading(true);

    getCoursesBatch(courseIds)
      .then((fetched) => {
        if (cancelled) return;
        // Preserve order from courseIds, filter out any that weren't found (stale IDs)
        const ordered: Course[] = [];
        for (const id of courseIds) {
          const c = fetched.find((x) => x.id === id);
          if (c) ordered.push(c);
        }
        // If we dropped any, update persisted IDs
        if (ordered.length < courseIds.length) {
          const newIds = ordered.map((c) => c.id);
          setCourseIds(newIds);
        }
        setCourses(ordered);
      })
      .catch(() => {
        if (!cancelled) setCourses([]);
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [courseIds]);

  const schedule = courses.length > 0 ? buildScheduleResponse(courses) : EMPTY_SCHEDULE;

  const addCourse = useCallback(
    async (courseId: string): Promise<{ success: boolean; conflicts: ScheduleConflict[] }> => {
      if (courseIds.includes(courseId)) {
        return { success: true, conflicts: [] };
      }
      setIsAdding(true);
      try {
        const course = await getCourse(courseId);
        const newIds = [...courseIds, courseId];
        setCourseIds(newIds);

        // New conflicts = conflicts involving the new course
        const allCourses = [...courses, course];
        const allConflicts = detectConflicts(allCourses);
        const newConflicts = allConflicts.filter(
          (c) => c.course1_id === courseId || c.course2_id === courseId
        );

        return { success: true, conflicts: newConflicts };
      } catch {
        return { success: false, conflicts: [] };
      } finally {
        setIsAdding(false);
      }
    },
    [courseIds, courses]
  );

  const removeCourse = useCallback(async (courseId: string): Promise<boolean> => {
    if (!courseIds.includes(courseId)) return true;
    setIsRemoving(true);
    try {
      setCourseIds((prev) => prev.filter((id) => id !== courseId));
      return true;
    } finally {
      setIsRemoving(false);
    }
  }, [courseIds]);

  const clear = useCallback(async (): Promise<boolean> => {
    setCourseIds([]);
    return true;
  }, []);

  const isInSchedule = useCallback(
    (courseId: string): boolean => courseIds.includes(courseId),
    [courseIds]
  );

  const handleExport = useCallback(async () => {
    const ids = schedule.courses.map((c) => c.id);
    if (ids.length === 0) return;
    const { ics, filename } = await exportSchedule(ids);
    const blob = new Blob([ics], { type: 'text/calendar;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  }, [schedule.courses]);

  return {
    schedule,
    isLoading,
    addCourse,
    removeCourse,
    clear,
    isInSchedule,
    isAdding,
    isRemoving,
    handleExport,
  };
}
