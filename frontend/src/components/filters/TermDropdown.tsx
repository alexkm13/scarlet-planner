import { Dropdown, DropdownItem } from '../ui/Dropdown';
import { useTerms } from '../../hooks/useTerms';

interface TermDropdownProps {
  selected: string[];
  onChange: (value: string[]) => void;
}

export function TermDropdown({ selected, onChange }: TermDropdownProps) {
  const { data } = useTerms();
  const terms = data?.terms ?? [];

  const toggleTerm = (term: string) => {
    if (selected.includes(term)) {
      onChange(selected.filter(t => t !== term));
    } else {
      onChange([...selected, term]);
    }
  };

  const displayValue = selected.length === 1 
    ? selected[0] 
    : selected.length > 1 
      ? `${selected.length} terms`
      : 'All';

  return (
    <Dropdown label="Term" value={selected} displayValue={displayValue}>
      <div className="py-1">
        {selected.length > 0 && (
          <button
            onClick={() => onChange([])}
            className="w-full text-left px-4 py-2 text-sm text-bu-scarlet hover:bg-[var(--bg-secondary)]"
          >
            Clear all
          </button>
        )}
        {terms.map(term => (
          <DropdownItem
            key={term}
            selected={selected.includes(term)}
            onClick={() => toggleTerm(term)}
          >
            {term}
          </DropdownItem>
        ))}
      </div>
    </Dropdown>
  );
}
