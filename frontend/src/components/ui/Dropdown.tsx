import { useState, useRef, useEffect } from 'react';
import { ChevronDown } from 'lucide-react';
import { cn } from '../../lib/utils';

interface DropdownProps {
  label: string;
  value: string | string[];
  children: React.ReactNode;
  displayValue?: string;
}

export function Dropdown({ label, value, children, displayValue }: DropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  // Close on click outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (ref.current && !ref.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const hasValue = Array.isArray(value) ? value.length > 0 : !!value;
  const display = displayValue ?? (
    Array.isArray(value) 
      ? value.length > 0 ? `${value.length} selected` : 'All'
      : value || 'All'
  );

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          'flex items-center gap-2 px-3 py-2 rounded-lg border transition-colors text-sm whitespace-nowrap',
          hasValue
            ? 'border-bu-scarlet bg-bu-scarlet/10 text-bu-scarlet'
            : 'border-[var(--border-color)] bg-[var(--bg-secondary)] text-[var(--text-primary)]'
        )}
      >
        <span className="text-[var(--text-muted)]">{label}</span>
        <span>{display}</span>
        <ChevronDown className={cn('w-4 h-4 transition-transform', isOpen && 'rotate-180')} />
      </button>

      {isOpen && (
        <div className="absolute top-full left-0 mt-1 min-w-[200px] max-h-[300px] overflow-y-auto rounded-lg border border-[var(--border-color)] bg-[var(--bg-primary)] shadow-lg z-50">
          {children}
        </div>
      )}
    </div>
  );
}

interface DropdownItemProps {
  children: React.ReactNode;
  selected?: boolean;
  onClick: () => void;
}

export function DropdownItem({ children, selected, onClick }: DropdownItemProps) {
  return (
    <button
      onClick={onClick}
      className={cn(
        'w-full text-left px-4 py-2 text-sm hover:bg-[var(--bg-secondary)] transition-colors',
        selected && 'bg-bu-scarlet/10 text-bu-scarlet'
      )}
    >
      {children}
    </button>
  );
}
