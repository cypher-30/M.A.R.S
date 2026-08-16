"use client";

/** A dependency-free trend line with an area fill. Enough for a 90-day score or price series. */
export function Sparkline({
  values,
  width = 640,
  height = 200,
  stroke = "var(--calm)",
}: {
  values: number[];
  width?: number;
  height?: number;
  stroke?: string;
}) {
  if (values.length < 2) return null;

  const padTop = 12;
  const padBottom = 8;
  const plotHeight = height - padTop - padBottom;

  const min = Math.min(...values);
  const max = Math.max(...values);
  const span = max - min || 1;
  const step = width / (values.length - 1);

  const coords = values.map((value, index) => {
    const x = index * step;
    const y = padTop + plotHeight - ((value - min) / span) * plotHeight;
    return [x, y] as const;
  });

  const linePoints = coords.map(([x, y]) => `${x.toFixed(1)},${y.toFixed(1)}`).join(" ");
  const areaPoints = `0,${height} ${linePoints} ${width},${height}`;
  const [lastX, lastY] = coords[coords.length - 1];
  const gradientId = "sparkline-fill";

  return (
    <svg
      className="trend-chart"
      viewBox={`0 0 ${width} ${height}`}
      width="100%"
      height={height}
      preserveAspectRatio="none"
      aria-hidden="true"
    >
      <defs>
        <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={stroke} stopOpacity="0.22" />
          <stop offset="100%" stopColor={stroke} stopOpacity="0" />
        </linearGradient>
      </defs>
      {[0.25, 0.5, 0.75].map((fraction) => (
        <line
          key={fraction}
          x1="0"
          x2={width}
          y1={padTop + plotHeight * fraction}
          y2={padTop + plotHeight * fraction}
          stroke="var(--rule)"
          strokeWidth="1"
        />
      ))}
      <polygon points={areaPoints} fill={`url(#${gradientId})`} stroke="none" />
      <polyline points={linePoints} fill="none" stroke={stroke} strokeWidth="2" />
      <circle cx={lastX} cy={lastY} r="4" fill={stroke} />
    </svg>
  );
}
