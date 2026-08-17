export default function MetricCard({ title, value, suffix, prefix, icon }) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <div className="flex items-center mb-2">
        {icon && <div className="mr-2 h-5 w-5">{icon}</div>}
        <h3 className="text-sm font-medium text-gray-500">{title}</h3>
      </div>
      <p className="text-2xl font-bold text-gray-900">
        {prefix || ''}{value}{suffix || ''}
      </p>
    </div>
    </div>
  );
}