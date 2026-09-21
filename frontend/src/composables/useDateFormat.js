/**
 * Calendar date utilities.
 *
 * CALENDAR DATE ≠ INSTANT/TIMESTAMP
 *
 * Financial dates represent calendar DAYS (e.g., due_date "2026-09-20"),
 * not UTC instants. These helpers produce local-date strings without
 * timezone conversion artifacts.
 *
 * Do NOT use toISOString() for calendar dates — it converts to UTC,
 * which shifts the date backward in negative-UTC timezones (e.g., Colombia UTC-5)
 * between midnight and 5am local time.
 */

/**
 * Get today's date as a local YYYY-MM-DD string.
 * Safe for "is today?" comparisons against backend date strings.
 *
 * @returns {string} e.g., "2026-09-20"
 */
export function getLocalDateString(date = new Date()) {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

/**
 * Convert a YYYY-MM-DD string to a local Date at midnight.
 * Appending T00:00:00 forces local-time parsing instead of UTC.
 *
 * @param {string} dateStr - e.g., "2026-09-20"
 * @returns {Date}
 */
export function parseLocalDate(dateStr) {
  return new Date(dateStr + 'T00:00:00')
}

/**
 * Calculate days between a date string and today.
 * Positive = future, negative = past, 0 = today.
 *
 * @param {string} dateStr - e.g., "2026-09-20"
 * @returns {number}
 */
export function daysUntil(dateStr) {
  const target = parseLocalDate(dateStr)
  const now = new Date()
  now.setHours(0, 0, 0, 0)
  return Math.round((target - now) / 86400000)
}
