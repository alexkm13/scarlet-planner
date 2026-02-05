import { ExternalLink, MapPin, Users, BookOpen, Clock } from 'lucide-react';
import { Modal } from '../ui/Modal';
import { RatingBadge } from './RatingBadge';
import { ScheduleBadge } from './ScheduleBadge';
import type { Course } from '../../types';

interface CourseModalProps {
  course: Course;
  onClose: () => void;
}

export function CourseModal({ course, onClose }: CourseModalProps) {
  return (
    <Modal title={course.code} onClose={onClose}>
      <div className="space-y-6">
        {/* Title and basic info */}
        <div>
          <h3 className="text-xl font-semibold text-[var(--text-primary)] mb-2">
            {course.title}
          </h3>
          <div className="flex flex-wrap items-center gap-4 text-sm text-[var(--text-secondary)]">
            <span className="flex items-center gap-1">
              <BookOpen className="w-4 h-4" />
              {course.credits} credits
            </span>
            <span>{course.term}</span>
            <span>{course.section_type}</span>
          </div>
        </div>

        {/* Description */}
        {course.description && (
          <div>
            <h4 className="text-sm font-medium text-[var(--text-muted)] mb-2">Description</h4>
            <p className="text-[var(--text-secondary)] text-sm leading-relaxed">
              {course.description}
            </p>
          </div>
        )}

        {/* Professor and Rating */}
        <div className="flex items-center justify-between p-4 rounded-lg bg-[var(--bg-secondary)]">
          <div>
            <h4 className="text-sm font-medium text-[var(--text-muted)] mb-1">Professor</h4>
            <p className="text-[var(--text-primary)] font-medium">{course.professor}</p>
          </div>
          <div className="flex items-center gap-3">
            <RatingBadge rating={course.professor_rating} />
            {course.professor_rating?.rmp_url && (
              <a
                href={course.professor_rating.rmp_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-bu-scarlet hover:underline flex items-center gap-1 text-sm"
              >
                RMP <ExternalLink className="w-3 h-3" />
              </a>
            )}
          </div>
        </div>

        {/* Schedule */}
        <div>
          <h4 className="text-sm font-medium text-[var(--text-muted)] mb-2 flex items-center gap-2">
            <Clock className="w-4 h-4" />
            Schedule
          </h4>
          <ScheduleBadge schedule={course.schedule} />
          {course.schedule[0]?.location && (
            <p className="mt-2 text-sm text-[var(--text-secondary)] flex items-center gap-1">
              <MapPin className="w-4 h-4" />
              {course.schedule[0].location}
            </p>
          )}
        </div>

        {/* Enrollment */}
        <div className="flex items-center gap-2">
          <Users className="w-4 h-4 text-[var(--text-muted)]" />
          <span className="text-sm text-[var(--text-secondary)]">
            {course.enrollment_total} / {course.enrollment_cap} enrolled
          </span>
          <span className={`text-xs px-2 py-0.5 rounded-full ${
            course.status === 'Open' 
              ? 'bg-green-500/20 text-green-500' 
              : 'bg-red-500/20 text-red-500'
          }`}>
            {course.status}
          </span>
        </div>

        {/* Hub Units */}
        {course.hub_units.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-[var(--text-muted)] mb-2">Hub Units</h4>
            <div className="flex flex-wrap gap-2">
              {course.hub_units.map(hub => (
                <span
                  key={hub}
                  className="px-3 py-1 rounded-full text-sm bg-bu-scarlet/10 text-bu-scarlet"
                >
                  {hub}
                </span>
              ))}
            </div>
          </div>
        )}

      </div>
    </Modal>
  );
}
