/**
 * Number and Date formatters formatted to Indian financial conventions.
 */

const inrCurrencyFormatter = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

const inrCompactFormatter = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  maximumFractionDigits: 0,
});

const inrDecimalFormatter = new Intl.NumberFormat("en-IN", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

/**
 * Formats a number into Indian Rupee currency string: e.g. ₹ 1,30,615.10
 */
export function formatINR(amount: number, compact = false): string {
  if (isNaN(amount)) return "₹ 0.00";
  return compact ? inrCompactFormatter.format(amount) : inrCurrencyFormatter.format(amount);
}

/**
 * Formats a raw number with Indian comma separators: e.g. 1,30,615.10
 */
export function formatDecimal(amount: number): string {
  if (isNaN(amount)) return "0.00";
  return inrDecimalFormatter.format(amount);
}

/**
 * Formats ISO timestamp string to local human-readable time: e.g. "11 Oct 2026, 08:15 PM"
 */
export function formatDateTime(isoString?: string | null): string {
  if (!isoString) return "N/A";
  try {
    const date = new Date(isoString);
    if (isNaN(date.getTime())) return isoString;
    return new Intl.DateTimeFormat("en-IN", {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      hour12: true,
    }).format(date);
  } catch {
    return isoString;
  }
}

/**
 * Formats relative time elapsed from now: e.g. "Just now", "2m ago", "1h ago"
 */
export function formatRelativeTime(isoString?: string | null): string {
  if (!isoString) return "Recently";
  try {
    const date = new Date(isoString);
    const now = new Date();
    const diffSecs = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (diffSecs < 10) return "Just now";
    if (diffSecs < 60) return `${diffSecs}s ago`;
    const diffMins = Math.floor(diffSecs / 60);
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    return formatDateTime(isoString);
  } catch {
    return "Recently";
  }
}
