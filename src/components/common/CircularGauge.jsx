export default function CircularGauge({ value, size = 100, label }) {
  const radius = 50;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (value / 100) * circumference;
  const strokeDashoffset = offset < 0 ? 0 : offset;

  return (
    <div className="flex flex-col items-center">
      <svg width={size} height={size} className="mb-2">
        <circle
          cx={radius}
          cy={radius}
          r={radius}
          fill="none"
          strokeWidth="10"
          stroke="#eee"
        />
        <circle
          cx={radius}
          cy={radius}
          r={radius}
          fill="none"
          strokeWidth="10"
          stroke="url(#gradient)"
          strokeDashoffset={strokeDashoffset}
          strokeDasharray={circumference}
          strokeLinecap="round"
        />
        <defs>
          <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#4f46e5" />
            <stop offset="100%" stopColor="#7c3aed" />
          </linearGradient>
        </defs>
      </svg>
      {label && <span className="text-center text-sm">{label}</span>}
    </div>
  );
}