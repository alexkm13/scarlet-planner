import { useEffect } from 'react';
import { X } from 'lucide-react';

interface ModalProps {
  title: string;
  onClose: () => void;
  children: React.ReactNode;
}

export function Modal({ title, onClose, children }: ModalProps) {
  // Close on escape key
  useEffect(() => {
    function handleEscape(event: KeyboardEvent) {
      if (event.key === 'Escape') {
        onClose();
      }
    }

    document.addEventListener('keydown', handleEscape);
    document.body.style.overflow = 'hidden';
    
    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = '';
    };
  }, [onClose]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 animate-[fadeIn_150ms_ease-out]">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50 animate-[fadeIn_150ms_ease-out]"
        onClick={onClose}
      />

      {/* Modal content */}
      <div className="relative w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-xl bg-[var(--bg-primary)] border border-[var(--border-color)] shadow-2xl animate-[slideUp_200ms_ease-out] mx-0 sm:mx-0">
        {/* Header */}
        <div className="sticky top-0 flex items-center justify-between px-4 sm:px-6 py-3 sm:py-4 border-b border-[var(--border-color)] bg-[var(--bg-primary)]">
          <h2 className="text-base sm:text-lg font-semibold text-[var(--text-primary)] truncate pr-2">{title}</h2>
          <button
            onClick={onClose}
            className="p-2 sm:p-1 rounded-lg hover:bg-[var(--bg-secondary)] transition-colors min-h-[44px] min-w-[44px] sm:min-h-0 sm:min-w-0 flex items-center justify-center"
          >
            <X className="w-5 h-5 text-[var(--text-muted)]" />
          </button>
        </div>

        {/* Body */}
        <div className="p-4 sm:p-6">
          {children}
        </div>
      </div>
    </div>
  );
}
