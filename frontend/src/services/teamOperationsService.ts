import { apiClient } from "../api/client";
import type { TeamOperationsResponse } from "../types/teamOperations";

export const teamOperationsService = {
  getTeamOperations: async (): Promise<TeamOperationsResponse> => {
    const response = await apiClient.get<TeamOperationsResponse>("/team-operations");
    return response.data;
  }
};
