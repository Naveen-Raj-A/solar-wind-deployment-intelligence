export default function StatusBadge({ status, className }) {
  // Map status to colors and labels
  const getVariant = (status) => {
    switch (status) {
      case 'pending':
        return { bg: 'bg-yellow-100', text: 'text-yellow-800', label: 'Pending' };
      case 'completed':
        return { bg: 'bg-green-100', text: 'text-green-800', label: 'Completed' };
      case 'failed':
        return { bg: 'bg-red-100', text: 'text-red-800', label: 'Failed' };
      case 'processing':
        return { bg: 'bg-blue-100', text: 'text-blue-800', label: 'Processing' };
      default:
        return { bg: 'bg-gray-100', text: 'text-gray-800', label: status || 'Unknown' };
    }
  };

  const { bg, text, label } = getVariant(status);

  return (
    <span
      className={`px-2 py-1 text-xs rounded-full font-medium ${bg} ${text} ${className || ''}`}
    >
      {label}
    </span>
  );
}