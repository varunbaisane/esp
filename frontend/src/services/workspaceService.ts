import { cachedGet } from "../api/client";
import type { WorkspaceResponse } from "../types/workspace";

export const workspaceService = {
  getWorkspace: async (): Promise<WorkspaceResponse> => {
    return cachedGet<WorkspaceResponse>("/workspace");
  },
};
