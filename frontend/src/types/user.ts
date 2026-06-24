export interface User {
  id: number;
  full_name: string;
  email: string;
  created_at: string;
  roles?: { name: string }[];
}
