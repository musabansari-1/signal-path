export type User = {
  id: string;
  email: string;
  full_name: string;
  avatar_url: string | null;
  active_project_id: string | null;
  created_at: string;
};

export type Project = {
  id: string;
  name: string;
  description: string | null;
  target_role: string;
  target_industry: string | null;
  target_location: string | null;
  status: "active" | "paused" | "archived";
  created_at: string;
  updated_at: string;
};

