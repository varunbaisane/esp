import { useEffect, useState } from "react";
import type { TicketFilters as FiltersType } from "../../types/ticket";
import { userService } from "../../services/userService";
import type { User } from "../../types/user";

interface TicketFiltersProps {
  filters: FiltersType;
  onChange: (filters: FiltersType) => void;
}

export const TicketFilters = ({ filters, onChange }: TicketFiltersProps) => {
  const [users, setUsers] = useState<User[]>([]);

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const data = await userService.getUsers();
        setUsers(data);
      } catch (err) {
        console.error("Failed to load users for filters", err);
      }
    };
    fetchUsers();
  }, []);

  const handleChange = (key: keyof FiltersType, value: string) => {
    const newFilters = { ...filters };
    if (value === "ALL") {
      delete newFilters[key];
    } else {
      newFilters[key] = value;
    }
    onChange(newFilters);
  };

  const getValue = (key: keyof FiltersType) => filters[key] || "ALL";

  const hasActiveFilters = Object.keys(filters).some(key => filters[key as keyof FiltersType] !== undefined && filters[key as keyof FiltersType] !== null);

  const FilterSelect = ({ label, valueKey, options }: { label: string, valueKey: keyof FiltersType, options: {value: string, label: string}[] }) => (
    <div className="flex flex-col gap-1.5 w-full sm:w-auto flex-1 min-w-[160px]">
      <label className="text-xs font-bold text-gray-500 uppercase tracking-widest pl-1">{label}</label>
      <div className="relative">
        <select 
          className="w-full appearance-none bg-gray-50/50 border border-gray-200 text-gray-700 py-2.5 px-4 pr-8 rounded-xl leading-tight focus:outline-none focus:bg-white focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 transition-all font-medium text-sm shadow-sm hover:border-gray-300"
          value={getValue(valueKey)}
          onChange={(e) => handleChange(valueKey, e.target.value)}
        >
          {options.map(opt => (
            <option key={opt.value} value={opt.value} className="font-medium">{opt.label}</option>
          ))}
        </select>
        <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3 text-gray-400">
          <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
            <path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z"/>
          </svg>
        </div>
      </div>
    </div>
  );

  return (
    <div className="bg-white p-5 rounded-2xl shadow-sm border border-gray-200 mb-8">
      <div className="flex flex-wrap items-end gap-4 sm:gap-6">
        <FilterSelect 
          label="Status" 
          valueKey="status" 
          options={[
            {value: "ALL", label: "All Statuses"},
            {value: "ACTIVE", label: "Active"},
            {value: "OPEN", label: "Open"},
            {value: "IN_PROGRESS", label: "In Progress"},
            {value: "RESOLVED", label: "Resolved"},
            {value: "CLOSED", label: "Closed"}
          ]} 
        />

        <FilterSelect 
          label="Priority" 
          valueKey="priority" 
          options={[
            {value: "ALL", label: "All Priorities"},
            {value: "LOW", label: "Low"},
            {value: "MEDIUM", label: "Medium"},
            {value: "HIGH", label: "High"},
            {value: "CRITICAL", label: "Critical"}
          ]} 
        />

        <FilterSelect 
          label="Level" 
          valueKey="level" 
          options={[
            {value: "ALL", label: "All Levels"},
            {value: "L1", label: "L1 Support"},
            {value: "L2", label: "L2 Support"},
            {value: "L3", label: "L3 Engineering"}
          ]} 
        />

        <FilterSelect 
          label="Assigned To" 
          valueKey="assigned_to" 
          options={[
            {value: "ALL", label: "Anyone"},
            {value: "assigned", label: "Assigned"},
            {value: "unassigned", label: "Unassigned"},
            {value: "mine", label: "Me"},
            ...users.map(u => ({ value: u.id.toString(), label: u.full_name }))
          ]} 
        />

        <FilterSelect 
          label="SLA Risk" 
          valueKey="sla_status" 
          options={[
            {value: "ALL", label: "All Statuses"},
            {value: "HEALTHY", label: "Healthy"},
            {value: "AT_RISK", label: "At Risk"},
            {value: "BREACHED", label: "Breached"}
          ]} 
        />

        {hasActiveFilters && (
          <div className="flex items-end pb-[2px]">
            <button 
              onClick={() => onChange({})} 
              className="text-xs font-bold text-indigo-600 hover:text-indigo-800 transition-colors flex items-center gap-1.5 bg-indigo-50/80 px-4 h-10 rounded-xl hover:bg-indigo-100 uppercase tracking-wider"
            >
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
              <span>Clear</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
