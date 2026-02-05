import { Dropdown, DropdownItem } from '../ui/Dropdown';
import type { SortOption } from '../../types';

interface SortDropdownProps {
  value: SortOption;
  onChange: (value: SortOption) => void;
}

const SORT_OPTIONS: { id: SortOption; label: string }[] = [
  { id: 'relevance', label: 'Relevance' },
  { id: 'rating', label: 'Rating (High to Low)' },
  { id: 'code', label: 'Course Code' },
];

export function SortDropdown({ value, onChange }: SortDropdownProps) {
  const currentLabel = SORT_OPTIONS.find(o => o.id === value)?.label ?? 'Relevance';

  return (
    <Dropdown label="Sort by" value={value} displayValue={currentLabel}>
      <div className="py-1">
        {SORT_OPTIONS.map(option => (
          <DropdownItem
            key={option.id}
            selected={value === option.id}
            onClick={() => onChange(option.id)}
          >
            {option.label}
          </DropdownItem>
        ))}
      </div>
    </Dropdown>
  );
}
