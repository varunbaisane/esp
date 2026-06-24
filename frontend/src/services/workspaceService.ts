import { apiClient } from "../api/client";
import type { WorkspaceResponse } from "../types/workspace";

export const workspaceService = {
  getWorkspace: async (): Promise<WorkspaceResponse> => {
    const response = await apiClient.get<WorkspaceResponse>("/workspace");
    return response.data;
  },
};
