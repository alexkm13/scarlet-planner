import { cn } from '../../lib/utils';
import { useHubUnits } from '../../hooks/useHubUnits';

interface HubChipsProps {
  selected: string[];
  onChange: (value: string[]) => void;
}

export function HubChips({ selected, onChange }: HubChipsProps) {
  const { data } = useHubUnits();
  const hubUnits = data?.hub_units ?? [];

  const toggleHub = (hub: string) => {
    if (selected.includes(hub)) {
      onChange(selected.filter(h => h !== hub));
    } else {
      onChange([...selected, hub]);
    }
  };

  if (hubUnits.length === 0) {
    return null;
  }

  return (
    <div className="flex flex-wrap gap-2">
      <span className="text-sm text-[var(--text-muted)] py-1">Hub:</span>
      <div className="flex flex-wrap gap-2 overflow-x-auto pb-1">
        {hubUnits.map(hub => {
          const isSelected = selected.includes(hub);
          return (
            <button
              key={hub}
              onClick={() => toggleHub(hub)}
              className={cn(
                'px-3 py-1 rounded-full text-sm whitespace-nowrap transition-colors',
                isSelected
                  ? 'bg-bu-scarlet text-white'
                  : 'bg-[var(--bg-secondary)] text-[var(--text-secondary)] border border-[var(--border-color)] hover:border-bu-scarlet hover:text-bu-scarlet'
              )}
            >
              {hub}
            </button>
          );
        })}
      </div>
      {selected.length > 0 && (
        <button
          onClick={() => onChange([])}
          className="text-sm text-bu-scarlet hover:underline py-1"
        >
          Clear
        </button>
      )}
    </div>
  );
}
