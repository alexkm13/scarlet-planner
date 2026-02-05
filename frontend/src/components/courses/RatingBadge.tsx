import { Trophy } from 'lucide-react';
import { getRatingBgColor, cn } from '../../lib/utils';
import type { ProfessorRating } from '../../types';

interface RatingBadgeProps {
  rating: ProfessorRating | null;
}

export function RatingBadge({ rating }: RatingBadgeProps) {
  const value = rating?.rating ?? null;

  if (value === null) {
    return (
      <div className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-gray-600 text-white text-sm font-medium">
        <Trophy className="w-4 h-4" />
        <span>N/A</span>
      </div>
    );
  }

  return (
    <div className={cn(
      'inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-white text-sm font-medium',
      getRatingBgColor(value)
    )}>
      <Trophy className="w-4 h-4" />
      <span>{value.toFixed(2)}/5</span>
    </div>
  );
}
