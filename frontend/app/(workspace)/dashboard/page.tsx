"use client";

import { useQuery } from "@tanstack/react-query";
import { ArrowRight, BriefcaseBusiness, CalendarClock, CheckCircle2, Target, TrendingUp } from "lucide-react";
import Link from "next/link";

import { useAuth } from "@/components/auth-provider";
import { PageHeader } from "@/components/app-shell";
import { apiRequest } from "@/lib/api";
import type { ApplicationAnalytics, Job } from "@/lib/types";

type WeeklySummary = { total: number; complete: number; skipped: number; completion_rate: number };

export default function DashboardPage() {
  const { user } = useAuth();
  const firstName = user?.full_name.split(" ")[0] ?? "there";
  const projectId = user?.active_project_id;
  const analytics = useQuery({ queryKey: ["application-analytics", projectId], queryFn: () => apiRequest<ApplicationAnalytics>(`/applications/analytics?project_id=${projectId}`), enabled: Boolean(projectId) });
  const jobs = useQuery({ queryKey: ["jobs", projectId], queryFn: () => apiRequest<Job[]>(`/jobs?project_id=${projectId}`), enabled: Boolean(projectId) });
  const weekly = useQuery({ queryKey: ["weekly-summary", projectId], queryFn: () => apiRequest<WeeklySummary>(`/weekly-plan/summary?project_id=${projectId}`), enabled: Boolean(projectId) });
  const next = !projectId ? { title: "Create your first search project", text: "Give one role direction a clear home before adding jobs.", href: "/dashboard/projects", action: "Set up a project" } : !jobs.data?.length ? { title: "Add an opportunity worth considering", text: "Paste a real job description to see its requirements and fit.", href: "/jobs", action: "Open job inbox" } : !(analytics.data?.total_applications) ? { title: "Move a strong match into your pipeline", text: "Review your scored jobs and track the one you plan to pursue.", href: "/jobs", action: "Review opportunities" } : { title: "Keep the week moving", text: "Use your current pipeline to focus today’s highest-leverage action.", href: "/weekly-plan", action: "Open weekly plan" };

  return <><PageHeader eyebrow="Your command centre" title={`Good to see you, ${firstName}.`} description="Fit, follow-ups, interviews, and weekly progress—grounded in the work actually inside your search." action={<Link className="inline-flex items-center gap-2 rounded-xl bg-[#5b4df5] px-4 py-2.5 text-sm font-semibold text-white" href="/jobs">Add a job <ArrowRight className="size-4" /></Link>} /><section className="mt-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-4"><Metric label="Active applications" value={analytics.data?.total_applications ?? 0} icon={BriefcaseBusiness} /><Metric label="Average match" value={analytics.data?.average_match_score !== null && analytics.data?.average_match_score !== undefined ? `${analytics.data.average_match_score}` : "—"} icon={Target} /><Metric label="Follow-ups due" value={analytics.data?.follow_ups_due ?? 0} icon={CalendarClock} /><Metric label="Weekly progress" value={`${weekly.data?.completion_rate ?? 0}%`} icon={CheckCircle2} /></section><div className="mt-5 grid gap-5 xl:grid-cols-[1.25fr_.75fr]"><section className="rounded-3xl border border-[#e4e7ec] bg-white p-7"><p className="text-sm font-semibold text-[#5b4df5]">Recommended next action</p><h2 className="mt-2 text-xl font-semibold">{next.title}</h2><p className="mt-2 max-w-xl text-sm leading-6 text-[#667085]">{next.text}</p><Link className="mt-5 inline-flex items-center gap-2 text-sm font-semibold text-[#4b3ed0]" href={next.href}>{next.action} <ArrowRight className="size-4" /></Link></section><section className="rounded-3xl bg-[#182036] p-7 text-white"><TrendingUp className="size-6 text-[#77e4ba]" /><h2 className="mt-5 text-lg font-semibold">Pipeline signal</h2><div className="mt-5 grid grid-cols-2 gap-4"><div><p className="text-2xl font-semibold">{analytics.data?.response_rate ?? 0}%</p><p className="mt-1 text-xs text-[#aeb6c8]">Response rate</p></div><div><p className="text-2xl font-semibold">{analytics.data?.interview_rate ?? 0}%</p><p className="mt-1 text-xs text-[#aeb6c8]">Interview rate</p></div><div><p className="text-2xl font-semibold">{analytics.data?.offers ?? 0}</p><p className="mt-1 text-xs text-[#aeb6c8]">Offers</p></div><div><p className="text-2xl font-semibold">{jobs.data?.filter((job) => (job.latest_score ?? 0) >= 80).length ?? 0}</p><p className="mt-1 text-xs text-[#aeb6c8]">Strong matches</p></div></div></section></div></>;
}

function Metric({ label, value, icon: Icon }: { label: string; value: string | number; icon: typeof BriefcaseBusiness }) {
  return <article className="rounded-3xl border border-[#e4e7ec] bg-white p-5"><div className="flex items-center justify-between"><p className="text-sm text-[#667085]">{label}</p><Icon className="size-5 text-[#8c83f7]" /></div><p className="mt-5 text-3xl font-semibold">{value}</p></article>;
}
