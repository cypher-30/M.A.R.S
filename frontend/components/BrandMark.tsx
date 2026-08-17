/** The Orbit — a ring with a single body circling a fixed center. Primary logo mark. */
export function BrandMark({ size = 26, ring = "#3E6BAF", body = "#1B1F24" }: { size?: number; ring?: string; body?: string }) {
  return (
    <svg width={size} height={size} viewBox="0 0 64 64" className="brand-mark" aria-hidden="true">
      <circle cx="32" cy="32" r="22" fill="none" stroke={ring} strokeWidth="4" />
      <circle cx="32" cy="10" r="6" fill={ring} />
      <circle cx="32" cy="32" r="4" fill={body} />
    </svg>
  );
}
