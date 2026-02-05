interface TerrierIconProps {
  className?: string;
}

export function TerrierIcon({ className = "w-8 h-8" }: TerrierIconProps) {
  return (
    <svg 
      viewBox="0 0 100 100" 
      className={className}
      fill="currentColor"
    >
      {/* Stylized BU Terrier head silhouette */}
      <path d="M50 10 L30 25 L25 20 L20 30 L15 28 L18 40 L10 50 L15 55 L12 65 L20 62 L25 75 L35 80 L40 90 L50 88 L60 90 L65 80 L75 75 L80 62 L88 65 L85 55 L90 50 L82 40 L85 28 L80 30 L75 20 L70 25 L50 10Z" />
      {/* Ear accent */}
      <path d="M25 20 L30 35 L20 30Z" opacity="0.8" />
      <path d="M75 20 L70 35 L80 30Z" opacity="0.8" />
      {/* Eye spots */}
      <circle cx="38" cy="48" r="5" fill="var(--bg-primary, #0f0f0f)" />
      <circle cx="62" cy="48" r="5" fill="var(--bg-primary, #0f0f0f)" />
      {/* Nose */}
      <ellipse cx="50" cy="62" rx="8" ry="6" fill="var(--bg-primary, #0f0f0f)" />
    </svg>
  );
}
