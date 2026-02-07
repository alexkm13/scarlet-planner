/**
 * Schedule Builder - Client-side schedule logic with conflict detection.
 * Port of Python schedule_builder.py for localStorage-based per-user schedules.
 */

import type { Course } from '../types';
import type { ScheduleEvent, ScheduleConflict } from '../types';

export const DAY_ORDER = [
  'Monday',
  'Tuesday',
  'Wednesday',
  'Thursday',
  'Friday',
  'Saturday',
  'Sunday',
];

export const COLORS = [
  '#CC0000', // BU Scarlet
  '#3B82F6', // Blue
  '#10B981', // Green
  '#8B5CF6', // Purple
  '#F59E0B', // Amber
  '#EC4899', // Pink
  '#06B6D4', // Cyan
  '#84CC16', // Lime
  '#F97316', // Orange
  '#6366F1', // Indigo
];

/** Convert time string to minutes since midnight. */
export function parseTimeToMinutes(timeStr: string): number {
  if (!timeStr || typeof timeStr !== 'string') return 0;
  const s = timeStr.trim().toUpperCase();

  let isPm = s.includes('PM');
  let isAm = s.includes('AM');
  const cleaned = s.replace(/AM|PM/g, '').trim();

  if (cleaned.includes(':')) {
    const parts = cleaned.split(':');
    let h = parseInt(parts[0], 10) || 0;
    const m = parseInt(parts[1]?.split(/\s/)[0] ?? '0', 10) || 0;

    if (isPm && h !== 12) h += 12;
    else if (isAm && h === 12) h = 0;

    return h * 60 + m;
  }

  if (/^\d+$/.test(cleaned)) {
    if (cleaned.length === 4) {
      return parseInt(cleaned.slice(0, 2), 10) * 60 + parseInt(cleaned.slice(2), 10);
    }
    return parseInt(cleaned, 10) * 60;
  }

  return 0;
}

/** Parse day string into full day names (e.g. 'MWF' -> ['Monday','Wednesday','Friday']). */
export function parseDaysToFullNames(daysStr: string): string[] {
  if (!daysStr || daysStr.toUpperCase() === 'TBA') return [];

  const codes: string[] = [];
  let upper = daysStr.toUpperCase();

  const twoLetter = ['TU', 'TH', 'SA', 'SU', 'MO', 'WE', 'FR'];
  for (const code of twoLetter) {
    if (upper.includes(code)) {
      codes.push(code);
      upper = upper.replace(code, '');
    }
  }

  for (const char of upper) {
    if (char === 'M' && !codes.includes('MO')) codes.push('M');
    else if (char === 'W' && !codes.includes('WE')) codes.push('W');
    else if (char === 'F' && !codes.includes('FR')) codes.push('F');
  }

  const nameMap: Record<string, string> = {
    MO: 'Monday',
    TU: 'Tuesday',
    WE: 'Wednesday',
    TH: 'Thursday',
    FR: 'Friday',
    SA: 'Saturday',
    SU: 'Sunday',
    M: 'Monday',
    W: 'Wednesday',
    F: 'Friday',
  };

  return codes.map((c) => nameMap[c] ?? c).filter(Boolean);
}

interface InternalEvent {
  course_id: string;
  course_code: string;
  course_title: string;
  section: string;
  section_type: string;
  professor: string;
  day: string;
  start_minutes: number;
  end_minutes: number;
  start_time: string;
  end_time: string;
  location: string;
  color: string;
  column: number;
  total_columns: number;
}

function eventOverlaps(a: InternalEvent, b: InternalEvent): boolean {
  if (a.day !== b.day) return false;
  return a.start_minutes < b.end_minutes && b.start_minutes < a.end_minutes;
}

function courseToEvents(course: Course, color: string): InternalEvent[] {
  const events: InternalEvent[] = [];

  for (const meeting of course.schedule || []) {
    if (!meeting.days || meeting.days.toUpperCase() === 'TBA') continue;

    const days = parseDaysToFullNames(meeting.days);
    const start = meeting.start_time ? parseTimeToMinutes(meeting.start_time) : 0;
    const end = meeting.end_time ? parseTimeToMinutes(meeting.end_time) : 0;

    if (start === 0 && end === 0) continue;

    for (const day of days) {
      events.push({
        course_id: course.id,
        course_code: course.code,
        course_title: course.title,
        section: course.section,
        section_type: course.section_type,
        professor: course.professor,
        day,
        start_minutes: start,
        end_minutes: end,
        start_time: meeting.start_time,
        end_time: meeting.end_time,
        location: meeting.location ?? '',
        color,
        column: 0,
        total_columns: 1,
      });
    }
  }

  return events;
}

function assignColumns(events: InternalEvent[]): InternalEvent[] {
  const sorted = [...events].sort(
    (a, b) => a.start_minutes - b.start_minutes || a.end_minutes - b.end_minutes
  );
  const columns: number[] = [];

  for (const event of sorted) {
    let placed = false;
    for (let i = 0; i < columns.length; i++) {
      if (event.start_minutes >= columns[i]) {
        event.column = i;
        columns[i] = event.end_minutes;
        placed = true;
        break;
      }
    }
    if (!placed) {
      event.column = columns.length;
      columns.push(event.end_minutes);
    }
  }

  const totalCols = columns.length || 1;
  for (const event of sorted) {
    event.total_columns = totalCols;
  }

  return sorted;
}

/** Build events with column layout from a list of courses. */
export function coursesToEvents(courses: Course[]): ScheduleEvent[] {
  const courseColors: Record<string, string> = {};
  courses.forEach((c, i) => {
    courseColors[c.id] = COLORS[i % COLORS.length];
  });

  const allEvents: InternalEvent[] = [];
  for (const course of courses) {
    const color = courseColors[course.id] ?? COLORS[0];
    allEvents.push(...courseToEvents(course, color));
  }

  const byDay: Record<string, InternalEvent[]> = {};
  for (const event of allEvents) {
    if (!byDay[event.day]) byDay[event.day] = [];
    byDay[event.day].push(event);
  }

  const result: ScheduleEvent[] = [];
  for (const day of DAY_ORDER) {
    if (byDay[day]) {
      const dayEvents = assignColumns(byDay[day]);
      for (const e of dayEvents) {
        result.push({
          course_id: e.course_id,
          course_code: e.course_code,
          course_title: e.course_title,
          section: e.section,
          section_type: e.section_type,
          professor: e.professor,
          day: e.day,
          start_minutes: e.start_minutes,
          end_minutes: e.end_minutes,
          start_time: e.start_time,
          end_time: e.end_time,
          location: e.location,
          color: e.color,
          column: e.column,
          total_columns: e.total_columns,
        });
      }
    }
  }

  return result;
}

/** Detect all conflicts between courses. */
export function detectConflicts(courses: Course[]): ScheduleConflict[] {
  const conflicts: ScheduleConflict[] = [];
  const tempColor = COLORS[0];

  for (let i = 0; i < courses.length; i++) {
    const events1 = courseToEvents(courses[i], tempColor);
    for (let j = i + 1; j < courses.length; j++) {
      const events2 = courseToEvents(courses[j], tempColor);
      for (const e1 of events1) {
        for (const e2 of events2) {
          if (eventOverlaps(e1, e2)) {
            const overlapStart = Math.max(e1.start_minutes, e2.start_minutes);
            const overlapEnd = Math.min(e1.end_minutes, e2.end_minutes);
            conflicts.push({
              course1_id: e1.course_id,
              course1_code: e1.course_code,
              course2_id: e2.course_id,
              course2_code: e2.course_code,
              day: e1.day,
              overlap_minutes: overlapEnd - overlapStart,
            });
          }
        }
      }
    }
  }

  return conflicts;
}

/** Build full ScheduleResponse from courses. */
export function buildScheduleResponse(courses: Course[]) {
  const events = coursesToEvents(courses);
  const conflicts = detectConflicts(courses);
  const total_credits = courses.reduce((sum, c) => sum + (c.credits ?? 0), 0);

  return {
    courses: courses.map((c) => ({
      id: c.id,
      code: c.code,
      title: c.title,
      section: c.section,
      credits: c.credits,
      professor: c.professor,
      term: c.term,
    })),
    events,
    conflicts,
    total_credits,
    course_count: courses.length,
    has_conflicts: conflicts.length > 0,
  };
}
