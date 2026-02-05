import { ThemeToggle } from './ThemeToggle';

interface HeaderProps {
  searchValue?: string;
  onSearchChange?: (value: string) => void;
}

export function Header({ searchValue, onSearchChange }: HeaderProps) {
  return (
    <header className="sticky top-0 z-50 bg-[var(--bg-primary)] border-b border-[var(--border-color)]">
      <div className="max-w-7xl mx-auto px-4 py-3">
        <div className="flex items-center gap-4">
          {/* BU Terrier logo */}
          <img 
            src="/bu-terrier.png" 
            alt="BU Terrier" 
            className="h-12 w-auto flex-shrink-0"
          />
          
          {/* Search input */}
          <div className="flex-1 relative">
            <input
              type="text"
              value={searchValue ?? ''}
              onChange={(e) => onSearchChange?.(e.target.value)}
              placeholder="Search courses..."
              className="w-full py-3 px-4 bg-transparent text-[var(--text-primary)] text-xl placeholder:text-[var(--text-muted)] focus:outline-none"
            />
          </div>
          
          {/* Theme toggle */}
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}
