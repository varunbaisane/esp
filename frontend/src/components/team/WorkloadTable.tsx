import { useNavigate } from "react-router-dom";
import { UserAvatar } from "../common/UserAvatar";
import type { EngineerWorkload } from "../../types/teamOperations";

export const WorkloadTable = ({ workloads }: { workloads: EngineerWorkload[] }) => {
  const navigate = useNavigate();
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Engineer
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Role
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Assigned
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Critical
            </th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Breached
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {workloads.map((workload) => (
            <tr 
              key={workload.user_id} 
              className="hover:bg-gray-50 cursor-pointer transition-colors"
              onClick={() => navigate(`/tickets?assigned_to=${workload.user_id}&status=ACTIVE`)}
            >
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                <div className="flex items-center gap-3">
                  <UserAvatar name={workload.full_name} size="sm" />
                  <span>{workload.full_name}</span>
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                  {workload.role.replace("SUPPORT_", "")}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-semibold">
                {workload.assigned_tickets}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-orange-600 font-medium">
                {workload.critical_tickets > 0 ? workload.critical_tickets : '-'}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-red-600 font-medium">
                {workload.breached_tickets > 0 ? workload.breached_tickets : '-'}
              </td>
            </tr>
          ))}
          {workloads.length === 0 && (
            <tr>
              <td colSpan={5} className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 text-center">
                No active engineer workloads found.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
};
