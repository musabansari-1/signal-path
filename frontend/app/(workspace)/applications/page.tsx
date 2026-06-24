"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { BarChart3, BriefcaseBusiness, CalendarClock, Kanban, Plus, Table2 } from "lucide-react";
import { useState } from "react";

import { PageHeader } from "@/components/app-shell";
import { useAuth } from "@/components/auth-provider";
import { ProjectRequired } from "@/components/project-required";
import { apiRequest } from "@/lib/api";
import type { Application, ApplicationAnalytics, Job } from "@/lib/types";

const statuses = ["saved", "shortlisted", "applied", "outreach_sent", "follow_up_due", "recruiter_replied", "interview_scheduled", "technical_interview", "final_interview", "offer", "rejected", "no_response", "withdrawn"];
const columns = [
  { title: "Considering", statuses: ["saved", "shortlisted"] },
  { title: "In motion", statuses: ["applied", "outreach_sent", "follow_up_due"] },
  { title: "Conversation", statuses: ["recruiter_replied", "interview_scheduled", "technical_interview", "final_interview"] },
  { title: "Outcome", statuses: ["offer", "rejected", "no_response", "withdrawn"] },
];

export default function ApplicationsPage() {
  const { user } = useAuth();
  const projectId = user?.active_project_id;
  const queryClient = useQueryClient();
  const [view, setView] = useState<"kanban" | "table">("kanban");
  const [showAdd, setShowAdd] = useState(false);
  const [jobId, setJobId] = useState("");
  const applications = useQuery({ queryKey: ["applications", projectId], queryFn: () => apiRequest<Application[]>(`/applications?project_id=${projectId}`), enabled: Boolean(projectId) });
  const analytics = useQuery({ queryKey: ["application-analytics", projectId], queryFn: () => apiRequest<ApplicationAnalytics>(`/applications/analytics?project_id=${projectId}`), enabled: Boolean(projectId) });
  const jobs = useQuery({ queryKey: ["jobs", projectId], queryFn: () => apiRequest<Job[]>(`/jobs?project_id=${projectId}`), enabled: Boolean(projectId) });
  const create = useMutation({
    mutationFn: () => apiRequest<Application>("/applications", { method: "POST", body: JSON.stringify({ job_id: jobId, status: "saved" }) }),
    onSuccess: (application) => {
      queryClient.setQueryData<Application[]>(["applications", projectId], (current = []) => [application, ...current]);
      queryClient.invalidateQueries({ queryKey: ["application-analytics", projectId] });
      setJobId(""); setShowAdd(false);
    },
  });
  const update = useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) => apiRequest<Application>(`/applications/${id}`, { method: "PATCH", body: JSON.stringify({ status }) }),
    onSuccess: (updated) => {
      queryClient.setQueryData<Application[]>(["applications", projectId], (current = []) => current.map((item) => item.id === updated.id ? updated : item));
      queryClient.invalidateQueries({ queryKey: ["application-analytics", projectId] });
    },
  });
  const trackedJobs = new Set(applications.data?.map((item) => item.job_id));
  const availableJobs = jobs.data?.filter((job) => !trackedJobs.has(job.id)) ?? [];

  return <><PageHeader eyebrow="Your search pipeline" title="Applications" description="Treat each opportunity like a relationship: record the next step, close follow-up loops, and learn from outcomes." action={<button className="inline-flex items-center gap-2 rounded-xl bg-[#5b4df5] px-4 py-2.5 text-sm font-semibold text-white" onClick={() => setShowAdd(true)}><Plus className="size-4" />Track a job</button>} />{!projectId ? <ProjectRequired /> : <>{showAdd && <section className="mt-7 rounded-3xl border border-[#dcd9ff] bg-white p-6"><h2 className="font-semibold">Add from your job inbox</h2><div className="mt-4 flex flex-col gap-3 sm:flex-row"><select className="flex-1 rounded-xl border border-[#d0d5dd] bg-white px-4 py-3 text-sm" onChange={(event) => setJobId(event.target.value)} value={jobId}><option value="">Choose a saved job</option>{availableJobs.map((job) => <option key={job.id} value={job.id}>{job.title} · {job.company_name}</option>)}</select><button className="rounded-xl bg-[#172033] px-5 py-3 text-sm font-semibold text-white disabled:opacity-50" disabled={!jobId || create.isPending} onClick={() => create.mutate()}>Add to tracker</button><button className="px-3 text-sm font-semibold text-[#667085]" onClick={() => setShowAdd(false)}>Cancel</button></div>{create.error && <p className="mt-3 text-sm text-red-600">{create.error.message}</p>}</section>}<section className="mt-7 grid gap-4 sm:grid-cols-2 xl:grid-cols-4"><Metric label="Total applications" value={analytics.data?.total_applications ?? 0} icon={BriefcaseBusiness} /><Metric label="Interviews" value={analytics.data?.interviews ?? 0} icon={Kanban} /><Metric label="Response rate" value={`${analytics.data?.response_rate ?? 0}%`} icon={BarChart3} /><Metric label="Follow-ups due" value={analytics.data?.follow_ups_due ?? 0} icon={CalendarClock} /></section><div className="mt-6 flex justify-end"><div className="flex rounded-xl border border-[#d0d5dd] bg-white p-1"><button className={`rounded-lg p-2 ${view === "kanban" ? "bg-[#eeecff] text-[#5b4df5]" : "text-[#667085]"}`} onClick={() => setView("kanban")} title="Kanban view"><Kanban className="size-4" /></button><button className={`rounded-lg p-2 ${view === "table" ? "bg-[#eeecff] text-[#5b4df5]" : "text-[#667085]"}`} onClick={() => setView("table")} title="Table view"><Table2 className="size-4" /></button></div></div>{applications.isLoading ? <p className="mt-8 text-sm text-[#667085]">Loading pipeline…</p> : view === "kanban" ? <div className="mt-4 grid gap-4 xl:grid-cols-4">{columns.map((column) => <section className="min-h-72 rounded-3xl bg-[#eef0f5] p-3" key={column.title}><div className="flex items-center justify-between px-2 py-2"><h2 className="text-sm font-semibold">{column.title}</h2><span className="rounded-full bg-white px-2 py-0.5 text-xs text-[#667085]">{applications.data?.filter((item) => column.statuses.includes(item.status)).length ?? 0}</span></div><div className="mt-2 space-y-3">{applications.data?.filter((item) => column.statuses.includes(item.status)).map((application) => <ApplicationCard application={application} key={application.id} onStatus={(status) => update.mutate({ id: application.id, status })} />)}</div></section>)}</div> : <div className="mt-4 overflow-x-auto rounded-3xl border border-[#e4e7ec] bg-white"><table className="w-full min-w-[760px] text-left text-sm"><thead className="border-b bg-[#fafafa] text-xs uppercase tracking-wider text-[#667085]"><tr><th className="px-5 py-4">Company & role</th><th>Status</th><th>Applied</th><th>Follow-up</th><th>Contact</th></tr></thead><tbody className="divide-y divide-[#edf0f3]">{applications.data?.map((application) => <tr key={application.id}><td className="px-5 py-4"><p className="font-semibold">{application.role_title}</p><p className="text-[#667085]">{application.company_name}</p></td><td><StatusSelect status={application.status} onChange={(status) => update.mutate({ id: application.id, status })} /></td><td>{application.date_applied ?? "—"}</td><td>{application.follow_up_date ?? "—"}</td><td>{application.contact_name ?? "—"}</td></tr>)}</tbody></table></div>}{!applications.data?.length && <button className="mt-5 w-full rounded-3xl border border-dashed border-[#cfd3dc] bg-white p-14 text-center" onClick={() => setShowAdd(true)}><BriefcaseBusiness className="mx-auto size-8 text-[#8c83f7]" /><span className="mt-4 block font-semibold">Turn a promising job into an application</span><span className="mt-2 block text-sm text-[#667085]">Track the next action before it disappears into a browser tab.</span></button>}</>}</>;
}

function Metric({ label, value, icon: Icon }: { label: string; value: string | number; icon: typeof BriefcaseBusiness }) {
  return <article className="rounded-3xl border border-[#e4e7ec] bg-white p-5"><div className="flex items-center justify-between"><p className="text-sm text-[#667085]">{label}</p><Icon className="size-5 text-[#8c83f7]" /></div><p className="mt-4 text-3xl font-semibold">{value}</p></article>;
}

function ApplicationCard({ application, onStatus }: { application: Application; onStatus: (status: string) => void }) {
  return <article className="rounded-2xl border border-[#e4e7ec] bg-white p-4 shadow-sm"><p className="text-sm font-semibold">{application.role_title}</p><p className="mt-1 text-xs text-[#667085]">{application.company_name}</p><div className="mt-4"><StatusSelect status={application.status} onChange={onStatus} /></div>{application.follow_up_date && <p className="mt-3 flex items-center gap-1.5 text-xs text-[#b54708]"><CalendarClock className="size-3.5" />Follow up {application.follow_up_date}</p>}</article>;
}

function StatusSelect({ status, onChange }: { status: string; onChange: (status: string) => void }) {
  return <select aria-label="Application status" className="max-w-48 rounded-lg border border-[#d0d5dd] bg-white px-2.5 py-2 text-xs font-semibold capitalize text-[#475467]" onChange={(event) => onChange(event.target.value)} value={status}>{statuses.map((item) => <option key={item} value={item}>{item.replaceAll("_", " ")}</option>)}</select>;
}
