/**
 * Privacy guards enforced client-side for the interactive Explore panel.
 * The pipeline already refuses to publish any group below this size
 * (docs/architecture.md §9.3, P3) — this is a second, independent check so a
 * filtered SUBSET of the already-safe row data still respects the same
 * floor before it is rendered.
 */
export const MIN_GROUP_SIZE = 10;
export const SMALL_SAMPLE_WARNING_THRESHOLD = 30;

export function isSuppressed(n: number): boolean {
  return n < MIN_GROUP_SIZE;
}

export function isSmallSample(n: number): boolean {
  return n >= MIN_GROUP_SIZE && n < SMALL_SAMPLE_WARNING_THRESHOLD;
}
