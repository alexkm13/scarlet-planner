import { ChevronRight, ChevronDown } from 'lucide-react';
import { RatingBadge } from './RatingBadge';
import { ScheduleBadge } from './ScheduleBadge';
import { AddButton } from './AddButton';
import { cn } from '../../lib/utils';
import type { Course } from '../../types';

interface CourseRowProps {
  course: Course;
  onClick: () => void;
  isExpanded?: boolean;
  onToggleExpand?: () => void;
}

function getSectionsBadgeText(sections: Course['related_sections']): string {
  if (!sections || sections.length === 0) return '';
  
  const counts: Record<string, number> = {};
  for (const section of sections) {
    const type = section.section_type.toLowerCase();
    counts[type] = (counts[type] || 0) + 1;
  }
  
  const parts: string[] = [];
  if (counts['discussion']) {
    parts.push(`${counts['discussion']} discussion${counts['discussion'] > 1 ? 's' : ''}`);
  }
  if (counts['laboratory']) {
    parts.push(`${counts['laboratory']} lab${counts['laboratory'] > 1 ? 's' : ''}`);
  }
  // Handle any other types
  for (const [type, count] of Object.entries(counts)) {
    if (type !== 'discussion' && type !== 'laboratory') {
      parts.push(`${count} ${type}`);
    }
  }
  
  return parts.join(', ');
}

export function CourseRow({ course, onClick, isExpanded = false, onToggleExpand }: CourseRowProps) {
  const hasRelatedSections = course.related_sections && course.related_sections.length > 0;
  const sectionsBadge = getSectionsBadgeText(course.related_sections);

  const handleExpandClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onToggleExpand?.();
  };

  return (
    <tr
      onClick={onClick}
      className={cn(
        "border-b border-[var(--border-color)] hover:bg-[var(--bg-secondary)] cursor-pointer transition-colors",
        isExpanded && "bg-[var(--bg-secondary)]/30"
      )}
    >
      {/* Course */}
      <td className="py-2 px-4">
        <div className="flex items-start gap-2">
          {/* Expand chevron - fixed width container for alignment */}
          <div className="w-4 h-4 flex-shrink-0 flex items-center justify-center mt-0.5">
            {hasRelatedSections && (
              <button
                onClick={handleExpandClick}
                className="p-0.5 rounded hover:bg-[var(--bg-tertiary)] transition-colors"
              >
                {isExpanded ? (
                  <ChevronDown className="w-3 h-3 text-[var(--text-muted)]" />
                ) : (
                  <ChevronRight className="w-3 h-3 text-[var(--text-muted)]" />
                )}
              </button>
            )}
          </div>
          
          <div className="flex flex-col">
            <span className="text-[11px] text-[var(--text-muted)] uppercase tracking-wide">
              {course.code}
            </span>
            <span className="text-sm text-[var(--text-primary)]">
              {course.title}
            </span>
            {sectionsBadge && (
              <span className="text-[10px] text-bu-scarlet mt-0.5">
                {sectionsBadge}
              </span>
            )}
          </div>
        </div>
      </td>

      {/* Professor */}
      <td className="py-2 px-4 text-sm text-[var(--text-secondary)]">
        {course.professor}
      </td>

      {/* Term */}
      <td className="py-2 px-4 text-sm text-[var(--text-secondary)]">
        {course.term}
      </td>

      {/* Schedule */}
      <td className="py-2 px-4">
        <ScheduleBadge schedule={course.schedule} />
      </td>

      {/* Rating */}
      <td className="py-2 px-4">
        <RatingBadge rating={course.professor_rating} />
      </td>

      {/* Add button */}
      <td className="py-2 px-4">
        <AddButton courseId={course.id} />
      </td>
    </tr>
  );
}
