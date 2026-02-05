import { cn } from '../../lib/utils';

interface DayFilterProps {
  selected: string[];
  onChange: (value: string[]) => void;
}

const DAYS = [
  { id: 'M', label: 'M' },
  { id: 'T', label: 'T' },
  { id: 'W', label: 'W' },
  { id: 'TH', label: 'Th' },
  { id: 'F', label: 'F' },
];

export function DayFilter({ selected, onChange }: DayFilterProps) {
  const toggleDay = (day: string) => {
    if (selected.includes(day)) {
      onChange(selected.filter(d => d !== day));
    } else {
      onChange([...selected, day]);
    }
  };

  return (
    <div className="flex items-center gap-2">
      <span className="text-sm text-[var(--text-muted)]">Days:</span>
      <div className="flex gap-1">
        {DAYS.map(day => {
          const isSelected = selected.includes(day.id);
          return (
            <button
              key={day.id}
              onClick={() => toggleDay(day.id)}
              className={cn(
                'w-9 h-9 rounded-lg font-medium text-sm transition-colors',
                isSelected
                  ? 'bg-bu-scarlet text-white'
                  : 'bg-[var(--bg-secondary)] text-[var(--text-secondary)] border border-[var(--border-color)] hover:border-bu-scarlet hover:text-bu-scarlet'
              )}
            >
              {day.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}
