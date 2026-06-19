export const EmptySearchResults = () => {
  return (
    <div className="py-12 text-center">
      <svg
        className="mx-auto h-12 w-12 text-gray-400"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        aria-hidden="true"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1}
          d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
        />
      </svg>
      <h3 className="mt-4 text-sm font-medium text-gray-900">No matching tickets found.</h3>
      <p className="mt-1 text-sm text-gray-500">
        Try adjusting your search query to find what you're looking for.
      </p>
    </div>
  );
};
