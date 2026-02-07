import { useState, useMemo } from 'react';
import { ChevronDown } from 'lucide-react';
import type { ScheduleEvent } from '../../types';

interface ScheduleCalendarProps {
  events: ScheduleEvent[];
  terms: string[];
  selectedTerm: string;
  onTermChange: (term: string) => void;
}

const DAYS = ['Mo', 'Tu', 'We', 'Th', 'Fr'];
const DAY_MAP: Record<string, string> = {
  'Monday': 'Mo',
  'Tuesday': 'Tu',
  'Wednesday': 'We',
  'Thursday': 'Th',
  'Friday': 'Fr',
};

const START_HOUR = 7;
const END_HOUR = 22;
const HOUR_HEIGHT = 40;
const TOTAL_HOURS = END_HOUR - START_HOUR;

function minutesToPosition(minutes: number): number {
  const hoursSinceStart = (minutes - START_HOUR * 60) / 60;
  return hoursSinceStart * HOUR_HEIGHT;
}

/** Two-tone block: dark background + lighter border/text. */
function blockColors(hex: string): { bg: string; border: string; text: string } {
  const h = hex.replace(/^#/, '');
  const r = parseInt(h.slice(0, 2), 16) / 255;
  const g = parseInt(h.slice(2, 4), 16) / 255;
  const b = parseInt(h.slice(4, 6), 16) / 255;
  const max = Math.max(r, g, b), min = Math.min(r, g, b);
  let s = 0, l = (max + min) / 2;
  if (max !== min) {
    const d = max - min;
    s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
  }
  let hue = 0;
  if (max !== min) {
    const d = max - min;
    if (max === r) hue = ((g - b) / d + (g < b ? 6 : 0)) / 6;
    else if (max === g) hue = ((b - r) / d + 2) / 6;
    else hue = ((r - g) / d + 4) / 6;
  }
  const toHex = (n: number) => Math.round(Math.min(255, Math.max(0, n))).toString(16).padStart(2, '0');
  const hueToRgb = (p: number, q: number, t: number): number => {
    if (t < 0) t += 1; if (t > 1) t -= 1;
    if (t < 1/6) return p + (q - p) * 6 * t;
    if (t < 1/2) return q;
    if (t < 2/3) return p + (q - p) * (2/3 - t) * 6;
    return p;
  };
  const hslToRgb = (hh: number, ss: number, ll: number) => {
    let rr: number, gg: number, bb: number;
    if (ss === 0) rr = gg = bb = ll;
    else {
      const q = ll < 0.5 ? ll * (1 + ss) : ll + ss - ll * ss;
      const p = 2 * ll - q;
      rr = hueToRgb(p, q, hh + 1/3);
      gg = hueToRgb(p, q, hh);
      bb = hueToRgb(p, q, hh - 1/3);
    }
    return `#${toHex(rr*255)}${toHex(gg*255)}${toHex(bb*255)}`;
  };
  const bgL = Math.max(0.15, Math.min(0.35, l * 0.5));
  const borderL = Math.min(0.55, Math.max(0.4, bgL + 0.15));
  const textL = Math.min(0.92, borderL + 0.4);
  return {
    bg: hslToRgb(hue, s, bgL),
    border: hslToRgb(hue, s, borderL),
    text: hslToRgb(hue, s, textL),
  };
}

function formatLocation(location: string): string {
  if (!location || location.trim() === '') return '—';
  const trimmed = location.trim();
  if (trimmed.toUpperCase() === 'TBA') return '(TBA)';
  const match = trimmed.match(/\s([A-Z]{2,4})\s+([A-Z0-9]+)\s*$/i);
  if (match) return `(${match[1]} ${match[2]})`;
  return `(${trimmed})`;
}

function assignColumnsForDay(dayEvents: ScheduleEvent[]): { event: ScheduleEvent; column: number; totalColumns: number }[] {
  const sorted = [...dayEvents].sort((a, b) => a.start_minutes - b.start_minutes || a.end_minutes - b.end_minutes);
  const columns: number[] = [];
  const result: { event: ScheduleEvent; column: number; totalColumns: number }[] = [];
  for (const event of sorted) {
    let placed = false;
    for (let i = 0; i < columns.length; i++) {
      if (event.start_minutes >= columns[i]) {
        columns[i] = event.end_minutes;
        result.push({ event, column: i, totalColumns: 0 });
        placed = true;
        break;
      }
    }
    if (!placed) {
      result.push({ event, column: columns.length, totalColumns: 0 });
      columns.push(event.end_minutes);
    }
  }
  const totalCols = columns.length || 1;
  result.forEach((r) => { r.totalColumns = totalCols; });
  return result;
}

export function ScheduleCalendar({
  events,
  terms,
  selectedTerm,
  onTermChange,
}: ScheduleCalendarProps) {
  const [termDropdownOpen, setTermDropdownOpen] = useState(false);

  const eventsByDayWithColumns = useMemo(() => {
    const byDay: Record<string, ScheduleEvent[]> = {};
    for (const day of DAYS) byDay[day] = [];
    for (const event of events) {
      const dayCode = DAY_MAP[event.day];
      if (dayCode && byDay[dayCode]) byDay[dayCode].push(event);
    }
    const withColumns: Record<string, { event: ScheduleEvent; column: number; totalColumns: number }[]> = {};
    for (const day of DAYS) withColumns[day] = assignColumnsForDay(byDay[day]);
    return withColumns;
  }, [events]);

  const hours = Array.from({ length: TOTAL_HOURS }, (_, i) => START_HOUR + i);

  return (
    <div className="flex flex-col">
      <div className="relative mb-2 overflow-visible">
        <button
          type="button"
          onClick={() => setTermDropdownOpen(!termDropdownOpen)}
          className="flex items-center justify-between w-full px-3 py-2 text-bu-scarlet rounded-t-lg bg-[var(--bg-primary)]"
        >
          <span className="text-sm font-medium">{selectedTerm || 'Select Term'}</span>
          <ChevronDown className={`w-4 h-4 transition-transform shrink-0 ${termDropdownOpen ? 'rotate-180' : ''}`} />
        </button>
        {termDropdownOpen && (
          <div className="absolute top-full left-0 right-0 mt-0 bg-[var(--bg-primary)] rounded-b-lg shadow-lg z-50 overflow-hidden">
            {terms.length === 0 ? (
              <div className="px-3 py-2 text-sm text-[var(--text-muted)]">No terms</div>
            ) : (
              terms.map((term) => (
                <button
                  key={term}
                  type="button"
                  onClick={() => { onTermChange(term); setTermDropdownOpen(false); }}
                  className={`block w-full text-left px-3 py-2 text-sm hover:bg-[var(--bg-secondary)] ${selectedTerm === term ? 'text-bu-scarlet font-medium' : 'text-[var(--text-primary)]'}`}
                >
                  {term}
                </button>
              ))
            )}
          </div>
        )}
      </div>

      <div className="border border-[var(--border-color)] rounded-b-lg overflow-x-auto overflow-y-hidden">
        <div className="flex border-b border-[var(--border-color)] bg-[var(--bg-primary)] min-w-[320px]">
          <div className="flex-shrink-0 w-10 sm:w-12 border-r border-[var(--border-color)]" />
          {DAYS.map((day, i) => (
            <div
              key={day}
              className={`flex-1 min-w-0 h-6 flex items-center justify-center text-xs font-medium text-bu-scarlet ${i < DAYS.length - 1 ? 'border-r border-[var(--border-color)]' : ''}`}
            >
              {day}
            </div>
          ))}
        </div>

        <div className="flex min-w-[320px]">
          <div className="flex-shrink-0 w-10 sm:w-12 border-r border-[var(--border-color)]">
            {hours.map((hour) => (
              <div
                key={hour}
                  className="text-[10px] text-[var(--text-muted)] text-right pr-1 border-b border-[var(--border-color)]"
                style={{ height: HOUR_HEIGHT }}
              >
                {hour > 12 ? hour - 12 : hour} {hour >= 12 ? 'PM' : 'AM'}
              </div>
            ))}
          </div>

          {DAYS.map((day, dayIndex) => (
            <div
              key={day}
              className={`flex-1 min-w-0 relative ${dayIndex < DAYS.length - 1 ? 'border-r border-[var(--border-color)]' : ''}`}
              style={{ height: TOTAL_HOURS * HOUR_HEIGHT }}
            >
              {hours.map((hour, i) => (
                <div
                  key={hour}
                  className="absolute left-0 right-0 border-b border-[var(--border-color)]"
                  style={{ top: (i + 1) * HOUR_HEIGHT - 1 }}
                />
              ))}

              {eventsByDayWithColumns[day].map(({ event, column, totalColumns }, idx) => {
                const top = minutesToPosition(event.start_minutes);
                const rawHeight = ((event.end_minutes - event.start_minutes) / 60) * HOUR_HEIGHT;
                const blockHeight = Math.max(rawHeight, 44);
                const width = totalColumns > 1 ? `${100 / totalColumns}%` : '100%';
                const left = totalColumns > 1 ? `${(column / totalColumns) * 100}%` : '0';
                const isSmallBlock = blockHeight < 60 || totalColumns > 1;
                const colors = blockColors(event.color || '#3B82F6');

                return (
                  <div
                    key={`${event.course_id}-${idx}`}
                    className="absolute rounded-lg overflow-hidden flex flex-col justify-start border break-words"
                    style={{
                      top,
                      height: blockHeight,
                      width,
                      left,
                      backgroundColor: colors.bg,
                      borderColor: colors.border,
                      color: colors.text,
                      padding: isSmallBlock ? '2px 4px' : '6px 8px',
                    }}
                  >
                    <div className="font-bold leading-tight break-words text-[8px]">{event.course_code}</div>
                    <div className="opacity-90 leading-tight break-words text-[8px]">{event.start_time} – {event.end_time}</div>
                    <div className="opacity-90 leading-tight break-words text-[8px]">{formatLocation(event.location)}</div>
                  </div>
                );
              })}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
