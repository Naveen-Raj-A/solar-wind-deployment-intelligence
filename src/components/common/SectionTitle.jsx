export default function SectionTitle({ title, subtitle, className }) {
  return (
    <div className={className}>
      <h2 className="text-2xl font-bold text-gray-900">{title}</h2>
      {subtitle && <p className="mt-1 text-sm text-gray-500">{subtitle}</p>}
    </div>
  );
}