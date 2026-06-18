export const EmptyTickets = () => {
  return (
    <div className="flex flex-col items-center justify-center p-12 bg-white rounded-lg border border-gray-200">
      <div className="text-4xl mb-4">📋</div>
      <h3 className="text-lg font-medium text-gray-900">No tickets found</h3>
      <p className="text-gray-500 mt-1">There are currently no tickets in the system.</p>
    </div>
  );
};
