import { useState, Fragment } from 'react';
import { CourseRow } from './CourseRow';
import { SectionSubRow } from './SectionSubRow';
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
    <div className="overflow-x-auto rounded-lg border border-[var(--border-color)]">
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
  );
}
