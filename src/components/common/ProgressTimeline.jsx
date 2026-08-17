export default function ProgressTimeline({ steps }) {
  return (
    <div className="space-y-6">
      {steps.map((step, index) => (
        <div key={index} className="flex items-start">
          <div className="flex-shrink-0">
            <div className="w-3 h-3 rounded-full bg-gray-300">
              {step.completed && (
                <div className="w-full h-full bg-bg-gradient-to-br from-green-500 to-green-600 rounded-full"></div>
              )}
            </div>
          </div>
          <div className="ml-4">
            <h3 className="font-medium text-gray-900">{step.label}</h3>
            {step.description && <p className="mt-1 text-sm text-gray-500">{step.description}</p>}
          </div>
        </div>
      ))}
    </div>
  );
}