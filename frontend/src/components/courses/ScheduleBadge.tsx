import { cn } from '../../lib/utils';
import type { Meeting } from '../../types';

interface ScheduleBadgeProps {
  schedule: Meeting[];
}

const DAY_ORDER = ['M', 'T', 'W', 'TH', 'F'];

function getDaysFromMeeting(days: string): string[] {
  const result: string[] = [];
  const upper = days.toUpperCase();
  
  // Format is like "MoWeFr", "TuTh", "Mo", etc.
  if (upper.includes('MO')) result.push('M');
  if (upper.includes('TU')) result.push('T');
  if (upper.includes('WE')) result.push('W');
  if (upper.includes('TH')) result.push('TH');
  if (upper.includes('FR')) result.push('F');
  
  return result;
}

export function ScheduleBadge({ schedule }: ScheduleBadgeProps) {
  if (schedule.length === 0) {
    return (
      <span className="text-[var(--text-muted)] text-sm italic">No schedule</span>
    );
  }

  const meeting = schedule[0];
  
  // Check for TBA schedule
  const isTBA = meeting.days.toUpperCase() === 'TBA' || 
                meeting.days === '' ||
                (meeting.start_time === '' && meeting.end_time === '');
  
  if (isTBA) {
    return (
      <span className="text-[var(--text-muted)] text-sm italic">No scheduled classes</span>
    );
  }

  const activeDays = getDaysFromMeeting(meeting.days);
  const timeRange = `${meeting.start_time} - ${meeting.end_time}`;

  return (
    <div className="flex flex-col gap-1">
      <div className="flex gap-1">
        {DAY_ORDER.map(day => {
          const isActive = activeDays.includes(day);
          const displayDay = day === 'TH' ? 'Th' : day;
          
          return (
            <span
              key={day}
              className={cn(
                'w-6 h-6 flex items-center justify-center rounded text-xs font-medium',
                isActive
                  ? 'bg-bu-scarlet text-white'
                  : 'bg-[var(--bg-tertiary)] text-[var(--text-muted)]'
              )}
            >
              {displayDay}
            </span>
          );
        })}
      </div>
      <span className="text-xs text-[var(--text-secondary)]">{timeRange}</span>
    </div>
  );
}
