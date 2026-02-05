import { RatingBadge } from './RatingBadge';
import { ScheduleBadge } from './ScheduleBadge';
import { AddButton } from './AddButton';
import type { RelatedSection } from '../../types';

interface SectionSubRowProps {
  section: RelatedSection;
}

export function SectionSubRow({ section }: SectionSubRowProps) {
  return (
    <tr className="bg-[var(--bg-secondary)]/30 border-b border-[var(--border-color)]">
      {/* Indented section info */}
      <td className="py-1.5 px-4 pl-11">
        <div className="flex items-center gap-2">
          <span className="text-[11px] text-[var(--text-muted)] bg-[var(--bg-tertiary)] px-1.5 py-0.5 rounded">
            {section.section}
          </span>
          <span className="text-xs text-[var(--text-secondary)]">
            {section.section_type}
          </span>
        </div>
      </td>

      {/* Professor */}
      <td className="py-1.5 px-4 text-xs text-[var(--text-secondary)]">
        {section.professor}
      </td>

      {/* Empty term cell */}
      <td className="py-1.5 px-4"></td>

      {/* Schedule */}
      <td className="py-1.5 px-4">
        <ScheduleBadge schedule={section.schedule} />
      </td>

      {/* Rating */}
      <td className="py-1.5 px-4">
        <RatingBadge rating={section.professor_rating} />
      </td>

      {/* Add button */}
      <td className="py-1.5 px-4">
        <AddButton courseId={section.id} />
      </td>
    </tr>
  );
}
