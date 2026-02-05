import { useState, Fragment } from 'react';
import { ChevronRight } from 'lucide-react';
import { CourseRow } from './CourseRow';
import { SectionSubRow } from './SectionSubRow';
import { RatingBadge } from './RatingBadge';
import { ScheduleBadge } from './ScheduleBadge';
import { AddButton } from './AddButton';
import { Spinner } from '../ui/Spinner';
import type { Course } from '../../types';

interface CourseTableProps {
  courses: Course[];
  isLoading: boolean;
  onCourseClick: (course: Course) => void;
}

export function CourseTable({ courses, isLoading, onCourseClick }: CourseTableProps) {
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set());

  const toggleExpanded = (courseId: string) => {
    setExpandedIds(prev => {
      const next = new Set(prev);
      if (next.has(courseId)) {
        next.delete(courseId);
      } else {
        next.add(courseId);
      }
      return next;
    });
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Spinner />
      </div>
    );
  }

  if (courses.length === 0) {
    return (
      <div className="text-center py-12 text-[var(--text-muted)]">
        No courses found. Try adjusting your filters.
      </div>
    );
  }

  return (
    <>
      {/* Mobile: card list */}
      <div className="md:hidden space-y-3">
        {courses.map(course => (
          <div
            key={course.id}
            onClick={() => onCourseClick(course)}
            className="flex items-start gap-3 p-4 rounded-xl border border-[var(--border-color)] bg-[var(--bg-primary)] hover:bg-[var(--bg-secondary)] cursor-pointer transition-colors min-h-[44px]"
          >
            <div className="flex-1 min-w-0">
              <p className="text-xs text-[var(--text-muted)] uppercase tracking-wide">{course.code}</p>
              <p className="text-sm font-medium text-[var(--text-primary)] mt-0.5 line-clamp-2">{course.title}</p>
              <p className="text-xs text-[var(--text-muted)] mt-1">{course.professor} · {course.term}</p>
              <div className="flex flex-wrap items-center gap-2 mt-2">
                <ScheduleBadge schedule={course.schedule} />
                <RatingBadge rating={course.professor_rating} />
              </div>
            </div>
            <div className="flex flex-col items-end gap-1 flex-shrink-0">
              <AddButton courseId={course.id} />
              <ChevronRight className="w-5 h-5 text-[var(--text-muted)]" />
            </div>
          </div>
        ))}
      </div>

      {/* Desktop: table */}
      <div className="hidden md:block overflow-x-auto rounded-lg border border-[var(--border-color)]">
        <table className="w-full">
          <thead>
            <tr className="text-left text-xs text-[var(--text-muted)] border-b border-[var(--border-color)]">
              <th className="py-2 px-4 font-normal">Course</th>
              <th className="py-2 px-4 font-normal">Instructors</th>
              <th className="py-2 px-4 font-normal">Term</th>
              <th className="py-2 px-4 font-normal">Schedule</th>
              <th className="py-2 px-4 font-normal">Rating</th>
              <th className="py-2 px-4 font-normal w-10"></th>
            </tr>
          </thead>
          <tbody>
            {courses.map(course => {
              const isExpanded = expandedIds.has(course.id);
              const hasRelated = course.related_sections && course.related_sections.length > 0;

              return (
                <Fragment key={course.id}>
                  <CourseRow
                    course={course}
                    onClick={() => onCourseClick(course)}
                    isExpanded={isExpanded}
                    onToggleExpand={hasRelated ? () => toggleExpanded(course.id) : undefined}
                  />
                  {isExpanded && course.related_sections?.map(section => (
                    <SectionSubRow
                      key={section.id}
                      section={section}
                    />
                  ))}
                </Fragment>
              );
            })}
          </tbody>
        </table>
      </div>
    </>
  );
}
