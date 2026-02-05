/**
 * Get the color class for a rating value.
 */
export function getRatingColor(rating: number | null): string {
  if (rating === null) return 'text-gray-500';
  if (rating >= 4.5) return 'text-rating-excellent';
  if (rating >= 3.5) return 'text-rating-good';
  if (rating >= 2.5) return 'text-rating-average';
  return 'text-rating-poor';
}

/**
 * Get the background color class for a rating badge (solid colors).
 */
export function getRatingBgColor(rating: number | null): string {
  if (rating === null) return 'bg-gray-600';
  if (rating >= 4.5) return 'bg-rating-excellent';
  if (rating >= 3.5) return 'bg-rating-good';
  if (rating >= 2.5) return 'bg-rating-average';
  return 'bg-rating-poor';
}

/**
 * Combine class names, filtering out falsy values.
 */
export function cn(...classes: (string | undefined | null | false)[]): string {
  return classes.filter(Boolean).join(' ');
}

/**
 * Parse days string (e.g., "MWF", "TuTh") into individual day codes.
 */
export function parseDays(days: string): string[] {
  const result: string[] = [];
  const upper = days.toUpperCase();
  
  // Check two-letter codes first
  for (const twoLetter of ['TU', 'TH', 'SA', 'SU']) {
    if (upper.includes(twoLetter)) {
      result.push(twoLetter);
    }
  }
  
  // Single letter codes (after removing two-letter matches)
  let remaining = upper;
  for (const twoLetter of ['TU', 'TH', 'SA', 'SU']) {
    remaining = remaining.replace(twoLetter, '');
  }
  
  for (const char of remaining) {
    if ('MWF'.includes(char)) {
      result.push(char);
    }
  }
  
  return result;
}

/**
 * Format time for display (e.g., "10:10 AM" -> "10:10")
 */
export function formatTime(time: string): string {
  return time.replace(/ (AM|PM)$/i, '').trim();
}

/**
 * Debounce a function.
 */
export function debounce<T extends (...args: unknown[]) => unknown>(
  fn: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: ReturnType<typeof setTimeout>;
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn(...args), delay);
  };
}
