import { apiClient } from "../api/client";
import type { User } from "../types/user";

export const userService = {
  getUsers: async (): Promise<User[]> => {
    const response = await apiClient.get<User[]>("/users");
    return response.data;
  }
};
