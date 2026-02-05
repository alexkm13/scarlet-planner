import { Dropdown, DropdownItem } from '../ui/Dropdown';

interface StatusDropdownProps {
  selected: string[];
  onChange: (value: string[]) => void;
}

const STATUSES = ['Open', 'Closed'];

export function StatusDropdown({ selected, onChange }: StatusDropdownProps) {
  const toggleStatus = (status: string) => {
    if (selected.includes(status)) {
      onChange(selected.filter(s => s !== status));
    } else {
      onChange([...selected, status]);
    }
  };

  const displayValue = selected.length === 1 
    ? selected[0] 
    : selected.length > 1 
      ? 'All'
      : 'All';

  return (
    <Dropdown label="Status" value={selected} displayValue={displayValue}>
      <div className="py-1">
        {selected.length > 0 && (
          <button
            onClick={() => onChange([])}
            className="w-full text-left px-4 py-2 text-sm text-bu-scarlet hover:bg-[var(--bg-secondary)]"
          >
            Clear
          </button>
        )}
        {STATUSES.map(status => (
          <DropdownItem
            key={status}
            selected={selected.includes(status)}
            onClick={() => toggleStatus(status)}
          >
            {status}
          </DropdownItem>
        ))}
      </div>
    </Dropdown>
  );
}
