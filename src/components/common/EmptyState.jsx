export default function EmptyState({ title, description, icon } = {}) {
  return (
    <div className="text-center py-12">
      {icon && <div className="mx-auto mb-4 h-12 w-12">{icon}</div>}
      <h3 className="text-lg font-medium text-gray-500">{title || 'No data available'}</h3>
      {description && (
        <p className="mt-2 text-sm text-gray-400">{description}</p>
      )}
    </div>
  );
}