import type { CourseResponse, SubjectsResponse, TermsResponse, HubUnitsResponse, Course, ScheduleResponse, AddCourseResponse } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL?.replace(/\/$/, '') || '';

function apiUrl(path: string): string {
  const base = API_BASE_URL || window.location.origin;
  const p = path.startsWith('/') ? path : `/${path}`;
  return `${base.replace(/\/$/, '')}${p}`;
}

interface SearchParams {
  q?: string;
  subject?: string[];
  term?: string[];
  hub?: string[];
  status?: string[];
  limit?: number;
  offset?: number;
  grouped?: boolean;
}

export async function searchCourses(params: SearchParams): Promise<CourseResponse> {
  const url = new URL(apiUrl('/api/courses'));
  
  if (params.q) url.searchParams.set('q', params.q);
  if (params.limit) url.searchParams.set('limit', params.limit.toString());
  if (params.offset) url.searchParams.set('offset', params.offset.toString());
  
  // Default to grouped=true
  url.searchParams.set('grouped', (params.grouped ?? true).toString());
  
  // Handle array params
  params.subject?.forEach(s => url.searchParams.append('subject', s));
  params.term?.forEach(t => url.searchParams.append('term', t));
  params.hub?.forEach(h => url.searchParams.append('hub', h));
  params.status?.forEach(s => url.searchParams.append('status', s));
  
  const response = await fetch(url.toString());
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return response.json();
}

export async function getCourse(courseId: string): Promise<Course> {
  const response = await fetch(apiUrl(`/api/courses/${encodeURIComponent(courseId)}`));
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return response.json();
}

export async function getSubjects(): Promise<SubjectsResponse> {
  const response = await fetch(apiUrl('/api/subjects'));
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return response.json();
}

export async function getTerms(): Promise<TermsResponse> {
  const response = await fetch(apiUrl('/api/terms'));
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return response.json();
}

export async function getHubUnits(): Promise<HubUnitsResponse> {
  const response = await fetch(apiUrl('/api/hub-units'));
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return response.json();
}

// Schedule Builder API

export async function getSchedule(): Promise<ScheduleResponse> {
  const response = await fetch(apiUrl('/api/schedule'));
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return response.json();
}

export async function addToSchedule(courseId: string): Promise<AddCourseResponse> {
  const response = await fetch(apiUrl('/api/schedule/add'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ course_id: courseId }),
  });
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return response.json();
}

export async function removeFromSchedule(courseId: string): Promise<{ success: boolean; schedule: ScheduleResponse }> {
  const response = await fetch(apiUrl(`/api/schedule/${encodeURIComponent(courseId)}`), {
    method: 'DELETE',
  });
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return response.json();
}

export async function clearSchedule(): Promise<{ success: boolean; schedule: ScheduleResponse }> {
  const response = await fetch(apiUrl('/api/schedule'), {
    method: 'DELETE',
  });
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return response.json();
}

export interface ScheduleExportResponse {
  ics: string;
  filename: string;
}

export async function exportSchedule(courseIds: string[]): Promise<ScheduleExportResponse> {
  const response = await fetch(apiUrl('/api/schedule/export'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(courseIds),
  });
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return response.json();
}
