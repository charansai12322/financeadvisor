import React from "react";

interface OdysseusMarkProps {
  className?: string;
  size?: number;
}

/**
 * Geometric, minimal wayfinding compass mark for Odysseus — Your AI Financial Navigator.
 * Avoids mythic illustrations or AI clichés; adheres to Obsidian Ledger design aesthetics.
 */
export function OdysseusMark({ className = "w-4 h-4", size = 20 }: OdysseusMarkProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.75"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-label="Odysseus Navigator Mark"
    >
      {/* Outer subtle celestial guide circle */}
      <circle cx="12" cy="12" r="9.5" strokeWidth="1.25" className="opacity-30" />
      
      {/* Cardinal orientation ticks */}
      <line x1="12" y1="2.5" x2="12" y2="4.5" strokeWidth="1.5" />
      <line x1="12" y1="19.5" x2="12" y2="21.5" strokeWidth="1.5" />
      <line x1="2.5" y1="12" x2="4.5" y2="12" strokeWidth="1.5" />
      <line x1="19.5" y1="12" x2="21.5" y2="12" strokeWidth="1.5" />

      {/* Dynamic geometric navigation diamond / needle */}
      <polygon
        points="12,5.5 15,12 12,18.5 9,12"
        fill="currentColor"
        fillOpacity="0.18"
        strokeWidth="1.5"
      />
      <polygon
        points="5.5,12 12,9.5 18.5,12 12,14.5"
        fill="currentColor"
        fillOpacity="0.08"
        strokeWidth="1.25"
      />

      {/* Central focal anchor */}
      <circle cx="12" cy="12" r="1.5" fill="currentColor" />
    </svg>
  );
}
