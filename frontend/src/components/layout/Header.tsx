import { ThemeToggle } from './ThemeToggle';

interface HeaderProps {
  searchValue?: string;
  onSearchChange?: (value: string) => void;
}

export function Header({ searchValue, onSearchChange }: HeaderProps) {
  return (
    <header className="sticky top-0 z-50 bg-[var(--bg-primary)] border-b border-[var(--border-color)]">
      <div className="max-w-7xl mx-auto px-3 py-2 sm:px-4 sm:py-3">
        <div className="flex items-center gap-2 sm:gap-4">
          {/* App mark */}
          <img
            src={`${import.meta.env.BASE_URL}bu-logo.png`}
            alt=""
            className="h-10 w-auto flex-shrink-0 sm:h-12"
          />
          
          {/* Search input */}
          <div className="flex-1 min-w-0 relative">
            <input
              type="text"
              value={searchValue ?? ''}
              onChange={(e) => onSearchChange?.(e.target.value)}
              placeholder="Search courses..."
              className="w-full py-2.5 px-3 text-base sm:py-3 sm:px-4 sm:text-xl bg-transparent text-[var(--text-primary)] placeholder:text-[var(--text-muted)] focus:outline-none min-h-[44px] sm:min-h-0"
            />
          </div>
          
          {/* Theme toggle */}
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}
