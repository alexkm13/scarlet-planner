export interface Meeting {
  days: string;
  start_time: string;
  end_time: string;
  location: string;
}

export interface ProfessorRating {
  name: string;
  rating: number | null;
  num_ratings: number;
  difficulty: number | null;
  would_take_again: number | null;
  rmp_url: string | null;
}

export interface RelatedSection {
  id: string;
  section: string;
  section_type: string;
  professor: string;
  schedule: Meeting[];
  status: string;
  enrollment_cap: number;
  enrollment_total: number;
  professor_rating: ProfessorRating | null;
}

export interface Course {
  id: string;
  code: string;
  title: string;
  description: string;
  section: string;
  professor: string;
  term: string;
  credits: number;
  hub_units: string[];
  department: string;
  college: string;
  schedule: Meeting[];
  status: string;
  enrollment_cap: number;
  enrollment_total: number;
  section_type: string;
  class_nbr: number;
  professor_rating: ProfessorRating | null;
  related_sections?: RelatedSection[];
}

export interface CourseResponse {
  courses: Course[];
  total: number;
  /** Query time in seconds (preferred). */
  query_time_sec?: number;
  /** @deprecated Use query_time_sec. Query time in milliseconds (legacy). */
  query_time_ms?: number;
}

export interface SubjectsResponse {
  subjects: string[];
}

export interface TermsResponse {
  terms: string[];
}

export interface HubUnitsResponse {
  hub_units: string[];
}

export interface Filters {
  q: string;
  subject: string[];
  term: string[];
  hub: string[];
  status: string[];
  days: string[];
}

export type SortOption = 'relevance' | 'rating' | 'code';

// Schedule Builder Types
export interface ScheduleEvent {
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

export interface ScheduleCourse {
  id: string;
  code: string;
  title: string;
  section: string;
  credits: number;
  professor: string;
  term: string;
}

export interface ScheduleConflict {
  course1_id: string;
  course1_code: string;
  course2_id: string;
  course2_code: string;
  day: string;
  overlap_minutes: number;
}

export interface ScheduleResponse {
  courses: ScheduleCourse[];
  events: ScheduleEvent[];
  conflicts: ScheduleConflict[];
  total_credits: number;
  course_count: number;
  has_conflicts: boolean;
}

export interface AddCourseResponse {
  success: boolean;
  schedule: ScheduleResponse;
  new_conflicts: ScheduleConflict[];
}
