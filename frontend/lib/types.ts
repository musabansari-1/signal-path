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

export type CareerAsset = {
  id: string;
  project_id: string;
  asset_type: string;
  title: string;
  url: string | null;
  file_name: string | null;
  mime_type: string | null;
  is_primary: boolean;
  created_at: string;
};

export type CandidateProfile = {
  id: string;
  project_id: string;
  headline: string | null;
  summary: string | null;
  years_experience: number | null;
  location: string | null;
  work_authorization: string | null;
  skills_json: string[];
  experience_json: Record<string, unknown>[];
  projects_json: Record<string, unknown>[];
  education_json: Record<string, unknown>[];
  certifications_json: Record<string, unknown>[];
  achievements_json: Record<string, unknown>[];
  strengths_json: string[];
  gaps_json: string[];
  best_fit_roles_json: string[];
  verified_facts_json: Array<Record<string, unknown>>;
  suggestions_json: Array<Record<string, unknown>>;
  reviewed_at: string | null;
  updated_at: string;
};

export type RoleCriteria = {
  id: string;
  project_id: string;
  job_titles: string[];
  industries: string[];
  salary_min: number | null;
  salary_max: number | null;
  currency: string;
  locations: string[];
  work_modes: string[];
  experience_levels: string[];
  required_skills: string[];
  nice_to_have_skills: string[];
  company_sizes: string[];
  roles_to_avoid: string[];
  industries_to_avoid: string[];
  visa_preference: string | null;
  company_stage_preference: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
};
