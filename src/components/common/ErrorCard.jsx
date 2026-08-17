export default function ErrorCard({ title, description, retryOnClick }) {
  return (
    <div className="bg-red-50 border-l-4 border-red-500 p-4 my-6">
      <div className="flex">
        <div className="flex-shrink-0">
          <!-- You can replace with an actual icon component -->
          <span className="flex-shrink-0 flex items-center justify-center h-8 w-8 rounded-md bg-red-100 text-red-500">
            !!
          </span>
        </div>
        <div className="ml-3">
          <h3 className="text-sm font-medium text-red-800">{title || 'Something went wrong'}</h3>
          <div className="mt-1 text-sm text-red-700">{description || 'Please try again later.'}</div>
          {retryOnClick && (
            <button
              onClick={retryOnClick}
              className="mt-2 inline-flex items-center px-3 py-1 text-sm font-medium text-red-600 border border-red-300 rounded-md hover:bg-red-50"
            >
              Retry
            </button>
          )}
        </div>
      </div>
    </div>
  );
}