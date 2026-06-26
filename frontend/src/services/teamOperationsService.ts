import { cachedGet } from "../api/client";
import type { TeamOperationsResponse } from "../types/teamOperations";

export const teamOperationsService = {
  getTeamOperations: async (): Promise<TeamOperationsResponse> => {
    return cachedGet<TeamOperationsResponse>("/team-operations");
  }
};
