import { useState, useRef, useEffect } from 'react';
import { ChevronDown, Search } from 'lucide-react';
import { cn } from '../../lib/utils';
import { getDepartmentDisplay, getDepartmentName } from '../../lib/departments';
import { useSubjects } from '../../hooks/useSubjects';

interface SubjectDropdownProps {
  selected: string[];
  onChange: (value: string[]) => void;
}

export function SubjectDropdown({ selected, onChange }: SubjectDropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState('');
  const ref = useRef<HTMLDivElement>(null);
  const { data } = useSubjects();
  const allSubjects = data?.subjects ?? [];

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

  // Search matches both code and full name
  const matchesSearch = (code: string) => {
    const searchLower = search.toLowerCase();
    const fullName = getDepartmentName(code).toLowerCase();
    return code.toLowerCase().includes(searchLower) || fullName.includes(searchLower);
  };

  const unselected = allSubjects.filter(s => !selected.includes(s));
  
  const filteredSelected = selected.filter(matchesSearch);
  const filteredUnselected = unselected.filter(matchesSearch);

  const toggleSubject = (subject: string) => {
    if (selected.includes(subject)) {
      onChange(selected.filter(s => s !== subject));
    } else {
      onChange([...selected, subject]);
    }
  };

  const displayValue = selected.length === 0 
    ? 'All' 
    : selected.length === 1 
      ? getDepartmentName(selected[0])
      : `${selected.length} selected`;

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          'flex items-center gap-2 px-3 py-2 rounded-lg border transition-colors text-sm',
          selected.length > 0
            ? 'border-bu-scarlet bg-bu-scarlet/10 text-bu-scarlet'
            : 'border-[var(--border-color)] bg-[var(--bg-secondary)] text-[var(--text-primary)]'
        )}
      >
        <span className="text-[var(--text-muted)] mr-1">Subject</span>
        <span className="font-medium">{displayValue}</span>
        <ChevronDown className={cn('w-4 h-4 transition-transform', isOpen && 'rotate-180')} />
      </button>

      {isOpen && (
        <div className="absolute top-full left-0 mt-1 w-[300px] max-h-[400px] rounded-lg border border-[var(--border-color)] bg-[var(--bg-primary)] shadow-lg z-50 overflow-hidden">
          {/* Search */}
          <div className="p-2 border-b border-[var(--border-color)]">
            <div className="relative">
              <Search className="absolute left-2 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--text-muted)]" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search subjects..."
                className="w-full pl-8 pr-3 py-1.5 text-sm rounded border border-[var(--border-color)] bg-[var(--bg-secondary)] text-[var(--text-primary)] placeholder:text-[var(--text-muted)] focus:outline-none focus:border-bu-scarlet"
              />
            </div>
          </div>

          <div className="overflow-y-auto max-h-[340px]">
            {/* Selected section */}
            {filteredSelected.length > 0 && (
              <div>
                <div className="flex items-center justify-between px-4 py-2 bg-[var(--bg-secondary)]">
                  <span className="text-sm font-medium text-[var(--text-primary)]">Selected</span>
                  <button
                    onClick={() => onChange([])}
                    className="text-sm text-bu-scarlet hover:underline"
                  >
                    Clear all
                  </button>
                </div>
                {filteredSelected.map(subject => (
                  <button
                    key={subject}
                    onClick={() => toggleSubject(subject)}
                    className="w-full text-left px-4 py-2 text-sm text-[var(--text-primary)] hover:bg-[var(--bg-secondary)] bg-bu-scarlet/5"
                  >
                    {getDepartmentDisplay(subject)}
                  </button>
                ))}
              </div>
            )}

            {/* Unselected section */}
            {filteredUnselected.length > 0 && (
              <div>
                <div className="flex items-center justify-between px-4 py-2 bg-[var(--bg-secondary)]">
                  <span className="text-sm font-medium text-[var(--text-primary)]">Unselected</span>
                  <button
                    onClick={() => onChange([...selected, ...filteredUnselected])}
                    className="text-sm text-bu-scarlet hover:underline"
                  >
                    Select all
                  </button>
                </div>
                {filteredUnselected.map(subject => (
                  <button
                    key={subject}
                    onClick={() => toggleSubject(subject)}
                    className="w-full text-left px-4 py-2 text-sm text-[var(--text-primary)] hover:bg-[var(--bg-secondary)]"
                  >
                    {getDepartmentDisplay(subject)}
                  </button>
                ))}
              </div>
            )}

            {filteredSelected.length === 0 && filteredUnselected.length === 0 && (
              <div className="px-4 py-8 text-center text-sm text-[var(--text-muted)]">
                No subjects found
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
