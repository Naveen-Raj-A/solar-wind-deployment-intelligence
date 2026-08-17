export default function StatCard({ title, value, description, icon, trend }) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="flex items-center mb-4">
        {icon && <div className="mr-3 h-5 w-5">{icon}</div>}
        <h3 className="text-sm font-medium text-gray-500">{title}</h3>
      </div>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
      {description && <p className="mt-1 text-sm text-gray-500">{description}</p>}
      {trend && (
        <span className={`mt-2 inline-flex items-center text-sm font-medium ${
          trend > 0 ? 'text-green-600' : 'text-red-600'
        }`}>
          {trend > 0 ? '▲' : '▼'} {Math.abs(tride)}%
        </span>
      )}
    </div>
  );
}