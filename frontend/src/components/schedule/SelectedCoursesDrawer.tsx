import { useState, useMemo, useEffect } from 'react';
import { Calendar, Download, Trash2, X } from 'lucide-react';
import { useSchedule } from '../../contexts/ScheduleContext';
import { ScheduleCalendar } from './ScheduleCalendar';

interface SelectedCoursesDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  onExport: () => void;
}

export function SelectedCoursesDrawer({ isOpen, onClose, onExport }: SelectedCoursesDrawerProps) {
  const { schedule, removeCourse } = useSchedule();
  const [showCalendar, setShowCalendar] = useState(false);

  const hasCourses = schedule.courses.length > 0;

  const terms = useMemo(() => {
    const termSet = new Set(schedule.courses.map((c) => c.term));
    return Array.from(termSet).sort();
  }, [schedule.courses]);

  const [selectedTerm, setSelectedTerm] = useState<string>('');

  const filteredEvents = useMemo(() => {
    if (!selectedTerm) return schedule.events;
    const termKey = selectedTerm.replace(' ', '');
    return schedule.events.filter((e) => e.course_id.includes(termKey));
  }, [schedule.events, selectedTerm]);

  useEffect(() => {
    if (terms.length > 0 && !terms.includes(selectedTerm)) {
      setSelectedTerm(terms[0]);
    }
  }, [terms, selectedTerm]);

  return (
    <>
      {/* Mobile: backdrop (only when open) */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 md:hidden animate-[fadeIn_150ms_ease-out]"
          onClick={onClose}
          aria-hidden
        />
      )}
      {/* Drawer panel: full-screen on mobile, side panel on desktop */}
      <div
        className={`
          fixed md:relative inset-y-0 right-0 z-50 md:z-auto
          w-full max-w-[100vw] md:max-w-[420px] md:flex-shrink-0
          bg-[var(--bg-primary)] border-l border-[var(--border-color)]
          transition-[transform] duration-300 ease-in-out md:transition-[width] md:duration-300
          flex flex-col
          md:overflow-hidden
          ${isOpen ? 'translate-x-0 md:w-[420px]' : 'translate-x-full md:translate-x-0 md:w-0 md:border-0'}
        `}
      >
        <div className="w-full md:w-[420px] h-full flex flex-col min-w-0">
          <div className="flex flex-wrap items-center justify-between gap-3 p-4 flex-shrink-0 border-b border-[var(--border-color)] md:border-b-0">
            <h2 className="text-lg font-semibold text-[var(--text-primary)]">
              Selected Courses
            </h2>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={onClose}
                className="p-2 rounded-lg md:hidden border border-[var(--border-color)] hover:bg-[var(--bg-secondary)]"
                aria-label="Close"
              >
                <X className="w-5 h-5 text-[var(--text-muted)]" />
              </button>
              <button
              type="button"
              onClick={() => setShowCalendar(!showCalendar)}
              className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border text-xs transition-colors ${
                showCalendar
                  ? 'border-bu-scarlet bg-bu-scarlet/10 text-bu-scarlet'
                  : 'border-[var(--border-color)] text-[var(--text-primary)] hover:border-[var(--text-muted)]'
              }`}
            >
              <Calendar className="w-3.5 h-3.5" />
              {showCalendar ? 'Hide Schedule' : 'Show Schedule'}
            </button>
            <button
              type="button"
              onClick={onExport}
              className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border border-[var(--border-color)] text-xs text-[var(--text-muted)] hover:border-[var(--text-muted)] transition-colors"
            >
              <Download className="w-3.5 h-3.5" />
              Export
            </button>
            </div>
          </div>

        <div className="flex-1 min-h-0 overflow-y-auto px-4 pt-4 pb-4 md:pt-0">
          {showCalendar && hasCourses && (
            <div className="mb-4">
              <ScheduleCalendar
                events={filteredEvents}
                terms={terms}
                selectedTerm={selectedTerm}
                onTermChange={setSelectedTerm}
              />
            </div>
          )}

          {!hasCourses ? (
            <p className="text-center text-sm text-[var(--text-muted)] mt-12 px-4">
              No courses selected yet. Click the '+' icon next to a course to add it.
            </p>
          ) : (
            <div className="space-y-3">
              {schedule.courses.map((course) => (
                <div
                  key={course.id}
                  className="flex items-start justify-between p-4 rounded-xl border border-[var(--border-color)] bg-[var(--bg-secondary)]"
                >
                  <div className="flex-1 min-w-0">
                    <p className="text-xs text-[var(--text-muted)] uppercase tracking-wide">
                      {course.code}
                    </p>
                    <p className="text-base text-[var(--text-primary)] mt-1">
                      {course.title}
                    </p>
                    <p className="text-sm text-[var(--text-muted)] mt-1">
                      {course.term} · {course.credits} credits
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={() => removeCourse(course.id)}
                    className="p-2 text-[var(--text-muted)] hover:text-red-500 transition-colors"
                    title="Remove from schedule"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
    </>
  );
}
