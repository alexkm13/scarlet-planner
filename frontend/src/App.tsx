import { useState, useCallback, useEffect } from 'react';
import { Layers, List, PanelRightOpen, PanelRightClose } from 'lucide-react';
import { Header } from './components/layout/Header';
import { TermDropdown } from './components/filters/TermDropdown';
import { StatusDropdown } from './components/filters/StatusDropdown';
import { SubjectDropdown } from './components/filters/SubjectDropdown';
import { DayFilter } from './components/filters/DayFilter';
import { SortDropdown } from './components/filters/SortDropdown';
import { CourseTable } from './components/courses/CourseTable';
import { CourseModal } from './components/courses/CourseModal';
import { Pagination } from './components/ui/Pagination';
import { SelectedCoursesDrawer } from './components/schedule/SelectedCoursesDrawer';
import { useCourses } from './hooks/useCourses';
import { useSchedule } from './hooks/useSchedule';
import { exportSchedule } from './api/client';
import type { Course, SortOption, Filters, Meeting } from './types';

const ITEMS_PER_PAGE = 50;

// Helper to parse days string into array of day codes
// Format is like "MoWeFr", "TuTh", "Mo", etc.
function parseMeetingDays(days: string): string[] {
  const result: string[] = [];
  const upper = days.toUpperCase();
  
  if (upper.includes('MO')) result.push('M');
  if (upper.includes('TU')) result.push('T');
  if (upper.includes('WE')) result.push('W');
  if (upper.includes('TH')) result.push('TH');
  if (upper.includes('FR')) result.push('F');
  
  return result;
}

// Check if any schedule in a list matches the selected days
function schedulesMatchDays(schedules: Meeting[], selectedDays: string[]): boolean {
  return schedules.some(meeting => {
    const courseDays = parseMeetingDays(meeting.days);
    return selectedDays.some(day => courseDays.includes(day));
  });
}

function App() {
  const [filters, setFilters] = useState<Filters>({
    q: '',
    subject: [],
    term: [],
    hub: [], // Kept for type compatibility, but Hub is now searchable via query
    status: [],
    days: [],
  });
  const [searchInput, setSearchInput] = useState(''); // Local input value
  const [sort, setSort] = useState<SortOption>('relevance');
  const [page, setPage] = useState(1);
  const [grouped, setGrouped] = useState(true);
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const { schedule } = useSchedule();

  // Debounce search input
  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchInput !== filters.q) {
        setFilters(prev => ({ ...prev, q: searchInput }));
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [searchInput, filters.q]);

  // Reset page when filters change
  useEffect(() => {
    setPage(1);
  }, [filters, grouped]);

  const { data, isLoading, error } = useCourses({
    q: filters.q,
    subject: filters.subject.length > 0 ? filters.subject : undefined,
    term: filters.term.length > 0 ? filters.term : undefined,
    status: filters.status.length > 0 ? filters.status : undefined,
    limit: ITEMS_PER_PAGE,
    offset: (page - 1) * ITEMS_PER_PAGE,
    grouped,
  });

  // Client-side day filtering (API doesn't support this yet)
  // When grouped, also check related sections for day matches
  const filteredCourses = data?.courses.filter(course => {
    if (filters.days.length === 0) return true;
    
    // Check primary course schedule
    if (schedulesMatchDays(course.schedule, filters.days)) {
      return true;
    }
    
    // Also check related sections if grouped
    if (grouped && course.related_sections) {
      return course.related_sections.some(section => 
        schedulesMatchDays(section.schedule, filters.days)
      );
    }
    
    return false;
  }) ?? [];

  // Client-side sorting
  const sortedCourses = [...filteredCourses].sort((a, b) => {
    switch (sort) {
      case 'rating':
        const aRating = a.professor_rating?.rating ?? 0;
        const bRating = b.professor_rating?.rating ?? 0;
        return bRating - aRating;
      case 'code':
        return a.code.localeCompare(b.code);
      default:
        return 0;
    }
  });

  const updateFilter = useCallback(<K extends keyof Filters>(key: K, value: Filters[K]) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  }, []);

  const totalPages = Math.ceil((data?.total ?? 0) / ITEMS_PER_PAGE);

  const handleExport = async () => {
    const courseIds = schedule.courses.map((c) => c.id);
    if (courseIds.length === 0) return;
    try {
      const { ics, filename } = await exportSchedule(courseIds);
      const blob = new Blob([ics], { type: 'text/calendar;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      console.error('Export failed:', e);
    }
  };

  return (
    <div className="h-screen bg-[var(--bg-primary)] flex overflow-hidden">
      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Header 
          searchValue={searchInput}
          onSearchChange={setSearchInput}
        />
        
        <main className="flex-1 overflow-y-auto px-3 py-4 sm:px-4 sm:py-6">
          <div className="max-w-7xl mx-auto">
          {/* Filters row 1 */}
          <div className="grid grid-cols-1 sm:grid-cols-2 md:flex md:flex-wrap items-stretch gap-2 sm:gap-3 mb-4">
            <TermDropdown
              selected={filters.term}
              onChange={(value) => updateFilter('term', value)}
            />
            <SubjectDropdown
              selected={filters.subject}
              onChange={(value) => updateFilter('subject', value)}
            />
            <StatusDropdown
              selected={filters.status}
              onChange={(value) => updateFilter('status', value)}
            />
          </div>

          {/* Day filter and sort */}
          <div className="flex flex-wrap items-center justify-between gap-3 sm:gap-4 mb-4 sm:mb-6">
            <DayFilter
              selected={filters.days}
              onChange={(value) => updateFilter('days', value)}
            />
            <SortDropdown value={sort} onChange={setSort} />
          </div>

          {/* Results info and view toggle */}
          <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
            <p className="text-sm text-[var(--text-muted)]">
              {isLoading ? 'Loading...' : `${data?.total ?? 0} courses found`}
              {(() => {
                const ms = data?.query_time_ms;
                return ms != null ? <span className="ml-2">({Math.round(ms)}ms)</span> : null;
              })()}
            </p>

            <div className="flex items-center gap-2">
              {/* Group/Flatten toggle */}
              <button
                onClick={() => setGrouped(!grouped)}
                className="flex items-center gap-1.5 sm:gap-2 px-2.5 py-2 sm:px-3 sm:py-1.5 rounded-lg text-sm border border-[var(--border-color)] hover:border-bu-scarlet hover:text-bu-scarlet transition-colors min-h-[44px] sm:min-h-0"
                title={grouped ? "Show all sections (flat view)" : "Group sections under courses"}
              >
                <Layers className="w-4 h-4 flex-shrink-0" />
                <span className="hidden sm:inline">Grouped</span>
              </button>

              {/* Selected courses drawer toggle */}
              <button
                onClick={() => setDrawerOpen(!drawerOpen)}
                className="flex items-center gap-1.5 sm:gap-2 px-2.5 py-2 sm:px-3 sm:py-1.5 rounded-lg text-sm border border-[var(--border-color)] hover:border-bu-scarlet hover:text-bu-scarlet transition-colors min-h-[44px] sm:min-h-0"
                title={drawerOpen ? "Hide selected courses" : "Show selected courses"}
              >
                {drawerOpen ? (
                  <PanelRightClose className="w-4 h-4 flex-shrink-0" />
                ) : (
                  <PanelRightOpen className="w-4 h-4 flex-shrink-0" />
                )}
                <span className="hidden sm:inline">Selected</span>
                {schedule.course_count > 0 && (
                  <span className="bg-bu-scarlet text-white text-xs px-1.5 py-0.5 rounded-full">
                    {schedule.course_count}
                  </span>
                )}
              </button>
            </div>
          </div>

          {/* Error state */}
          {error && (
            <div className="p-4 mb-4 bg-red-500/10 border border-red-500/20 rounded-lg text-red-500">
              Error loading courses. Make sure the API server is running.
            </div>
          )}

          {/* Course table */}
          <CourseTable
            courses={sortedCourses}
            isLoading={isLoading}
            onCourseClick={setSelectedCourse}
          />

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="mt-6">
              <Pagination
                currentPage={page}
                totalPages={totalPages}
                onPageChange={setPage}
              />
            </div>
          )}

          {/* Footer */}
          <footer className="mt-12 pt-6 pb-8 border-t border-[var(--border-color)] text-center text-sm text-[var(--text-muted)] space-y-2">
            <p>
              <span className="font-medium text-[var(--text-primary)]">Scarlet Planner</span> v1 by Alex Kim
            </p>
            <p>
              Not affiliated with Boston University. Get in{' '}
              <a href="mailto:alexmk@bu.edu" className="text-bu-scarlet underline hover:underline focus:outline-none focus:underline align-baseline [vertical-align:-0.06em]">contact</a>.
            </p>
            <p>
              If this helped you save a few hours and find some better courses, tell a friend about it!
            </p>
          </footer>
          </div>
        </main>
      </div>

      {/* Right side drawer */}
      <SelectedCoursesDrawer
        isOpen={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        onExport={handleExport}
      />

      {/* Course detail modal */}
      {selectedCourse && (
        <CourseModal
          course={selectedCourse}
          onClose={() => setSelectedCourse(null)}
        />
      )}
    </div>
  );
}

export default App;
