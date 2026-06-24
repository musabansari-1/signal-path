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

export type Job = {
  id: string;
  project_id: string;
  source_type: string;
  source_url: string | null;
  company_name: string;
  title: string;
  description: string;
  location: string | null;
  work_mode: string | null;
  employment_type: string | null;
  experience_level: string | null;
  minimum_years_experience: number | null;
  salary_min: number | null;
  salary_max: number | null;
  currency: string | null;
  required_skills: string[];
  nice_to_have_skills: string[];
  responsibilities: string[];
  qualifications: string[];
  benefits: string[];
  red_flags: string[];
  missing_information: string[];
  application_url: string | null;
  parsed_json: Record<string, unknown>;
  status: "saved" | "shortlisted" | "skipped" | "applied";
  latest_score: number | null;
  created_at: string;
  updated_at: string;
};

export type JobScore = {
  id: string;
  job_id: string;
  total_score: number;
  skill_match_score: number;
  experience_match_score: number;
  criteria_match_score: number;
  keyword_match_score: number;
  location_fit_score: number;
  growth_potential_score: number;
  difficulty_score: number;
  recommendation: "strong_apply" | "apply" | "maybe" | "skip";
  strengths: string[];
  gaps: string[];
  keywords_to_add: string[];
  explanation: string;
  application_strategy: string;
  scored_at: string;
};

export type GeneratedResume = {
  id: string;
  project_id: string;
  job_id: string;
  title: string;
  content_json: Record<string, unknown>;
  markdown_content: string;
  export_pdf_path: string | null;
  export_docx_path: string | null;
  truthfulness_check_json: {
    verified_claims?: string[];
    needs_user_confirmation?: string[];
    removed_or_avoided_claims?: string[];
    warnings?: string[];
    ready_for_export?: boolean;
    user_confirmed_at?: string | null;
  };
  created_at: string;
  updated_at: string;
};

export type GeneratedMessage = {
  id: string;
  project_id: string;
  job_id: string | null;
  message_type: string;
  tone: string;
  subject_line: string | null;
  content: string;
  claims_used_json: Array<Record<string, unknown>>;
  review_warnings_json: string[];
  created_at: string;
  updated_at: string;
};

export type Application = {
  id: string;
  project_id: string;
  job_id: string;
  company_name: string;
  role_title: string;
  status: string;
  date_applied: string | null;
  contact_name: string | null;
  contact_email: string | null;
  contact_linkedin_url: string | null;
  follow_up_date: string | null;
  resume_id: string | null;
  notes: string | null;
  interview_stage: string | null;
  interview_date: string | null;
  created_at: string;
  updated_at: string;
};

export type ApplicationAnalytics = {
  total_applications: number;
  applied_this_week: number;
  interviews: number;
  offers: number;
  rejections: number;
  response_rate: number;
  interview_rate: number;
  average_match_score: number | null;
  follow_ups_due: number;
};

export type InterviewPrepPlan = {
  id: string;
  project_id: string;
  job_id: string;
  application_id: string | null;
  interview_stage: string;
  interview_date: string | null;
  technical_questions: Array<Record<string, unknown>>;
  behavioral_questions: Array<Record<string, unknown>>;
  company_research: string[];
  mock_interview_plan: string[];
  questions_to_ask: string[];
  focus_areas: string[];
  practice_answers: Record<string, string>;
  created_at: string;
  updated_at: string;
};

export type PortfolioProject = {
  id: string;
  project_id: string | null;
  name: string;
  description: string;
  github_url: string | null;
  live_url: string | null;
  tech_stack: string[];
  role_alignment: string[];
  audit_json: Record<string, unknown>;
  improvement_tasks: Array<{ title: string; priority: string; status: string }>;
  codex_prompt: string | null;
  created_at: string;
  updated_at: string;
};

export type WeeklyTask = {
  id: string;
  project_id: string;
  task_date: string;
  day_label: string;
  task_type: string;
  title: string;
  description: string;
  status: "pending" | "in_progress" | "complete" | "skipped";
  related_job_id: string | null;
  related_application_id: string | null;
  created_at: string;
  updated_at: string;
};
