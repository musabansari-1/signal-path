"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { CheckCircle2, Download, FileCheck2, LoaderCircle, Save, ShieldAlert, Sparkles } from "lucide-react";
import { useState } from "react";

import { PageHeader } from "@/components/app-shell";
import { useAuth } from "@/components/auth-provider";
import { ProjectRequired } from "@/components/project-required";
import { apiDownload, apiRequest } from "@/lib/api";
import type { GeneratedResume, Job } from "@/lib/types";

export function ResumeWorkspace({ initialJobId }: { initialJobId?: string }) {
  const { user } = useAuth();
  const projectId = user?.active_project_id;
  const queryClient = useQueryClient();
  const [jobId, setJobId] = useState(initialJobId ?? "");
  const [activeId, setActiveId] = useState<string | null>(null);
  const jobs = useQuery({ queryKey: ["jobs", projectId], queryFn: () => apiRequest<Job[]>(`/jobs?project_id=${projectId}`), enabled: Boolean(projectId) });
  const resumes = useQuery({ queryKey: ["resumes", projectId], queryFn: () => apiRequest<GeneratedResume[]>(`/resumes?project_id=${projectId}`), enabled: Boolean(projectId) });
  const generate = useMutation({
    mutationFn: () => apiRequest<GeneratedResume>("/resumes/generate", { method: "POST", body: JSON.stringify({ job_id: jobId }) }),
    onSuccess: (resume) => {
      queryClient.setQueryData<GeneratedResume[]>(["resumes", projectId], (current = []) => [resume, ...current]);
      setActiveId(resume.id);
    },
  });
  const active = resumes.data?.find((resume) => resume.id === activeId) ?? resumes.data?.[0];

  return <><PageHeader eyebrow="Grounded application assets" title="Tailored resumes" description="Tailor emphasis, never history. AI prose is held for review while the saved draft uses only exact source-backed or user-confirmed facts." />{!projectId ? <ProjectRequired /> : <><section className="mt-8 rounded-3xl border border-[#e4e7ec] bg-white p-6"><div className="flex flex-col gap-4 sm:flex-row sm:items-end"><label className="flex-1 text-sm font-semibold">Choose a target job<select className="mt-2 w-full rounded-xl border border-[#d0d5dd] bg-white px-4 py-3 font-normal outline-none focus:border-[#5b4df5]" onChange={(event) => setJobId(event.target.value)} value={jobId}><option value="">Select a job</option>{jobs.data?.map((job) => <option key={job.id} value={job.id}>{job.title} · {job.company_name}</option>)}</select></label><button className="inline-flex items-center justify-center gap-2 rounded-xl bg-[#5b4df5] px-5 py-3 text-sm font-semibold text-white disabled:opacity-50" disabled={!jobId || generate.isPending} onClick={() => generate.mutate()}>{generate.isPending ? <LoaderCircle className="size-4 animate-spin" /> : <Sparkles className="size-4" />}Generate grounded draft</button></div>{generate.error && <p className="mt-3 text-sm text-red-600">{generate.error.message}</p>}</section><div className="mt-6 grid gap-6 xl:grid-cols-[300px_1fr]"><aside className="rounded-3xl border border-[#e4e7ec] bg-white p-4"><p className="px-2 pb-3 text-xs font-bold uppercase tracking-[.15em] text-[#98a2b3]">Saved versions</p><div className="space-y-2">{resumes.data?.length ? resumes.data.map((resume) => <button className={`w-full rounded-2xl p-3 text-left ${active?.id === resume.id ? "bg-[#eeecff]" : "hover:bg-[#f7f8fb]"}`} key={resume.id} onClick={() => setActiveId(resume.id)}><p className="line-clamp-2 text-sm font-semibold">{resume.title}</p><p className="mt-1 text-xs text-[#667085]">{new Date(resume.updated_at).toLocaleDateString()}</p></button>) : <div className="px-2 py-8 text-center"><FileCheck2 className="mx-auto size-6 text-[#8c83f7]" /><p className="mt-3 text-sm text-[#667085]">No tailored resumes yet.</p></div>}</div></aside><section>{active ? <ResumeEditor key={active.id + active.updated_at} resume={active} /> : <div className="rounded-3xl border border-dashed border-[#cfd3dc] bg-white p-14 text-center"><FileCheck2 className="mx-auto size-8 text-[#8c83f7]" /><h2 className="mt-4 font-semibold">Your grounded draft will appear here</h2><p className="mx-auto mt-2 max-w-md text-sm leading-6 text-[#667085]">Choose a scored job and generate a version. Unsupported AI suggestions are shown in the checklist, not silently added.</p></div>}</section></div></>}</>;
}

function ResumeEditor({ resume }: { resume: GeneratedResume }) {
  const queryClient = useQueryClient();
  const [markdown, setMarkdown] = useState(resume.markdown_content);
  const [exportError, setExportError] = useState("");
  const save = useMutation({
    mutationFn: ({ confirm }: { confirm: boolean }) => apiRequest<GeneratedResume>(`/resumes/${resume.id}`, { method: "PATCH", body: JSON.stringify(confirm ? { confirm_truthfulness: true } : { markdown_content: markdown }) }),
    onSuccess: (updated) => {
      queryClient.setQueryData<GeneratedResume[]>(["resumes", resume.project_id], (current = []) => current.map((item) => item.id === updated.id ? updated : item));
    },
  });
  const checklist = resume.truthfulness_check_json;
  const exportFile = async (format: "pdf" | "docx") => {
    setExportError("");
    try { await apiDownload(`/resumes/${resume.id}/export-${format}`, `${resume.title}.${format}`); }
    catch (error) { setExportError(error instanceof Error ? error.message : "Unable to export"); }
  };
  return <article className="overflow-hidden rounded-3xl border border-[#e4e7ec] bg-white"><div className="flex flex-wrap items-center justify-between gap-3 border-b border-[#edf0f3] px-6 py-4"><div><h2 className="font-semibold">{resume.title}</h2><p className="mt-1 text-xs text-[#667085]">ATS-friendly single-column Markdown</p></div><button className="inline-flex items-center gap-2 rounded-xl border border-[#d0d5dd] px-4 py-2 text-sm font-semibold" disabled={save.isPending} onClick={() => save.mutate({ confirm: false })}><Save className="size-4" />Save edits</button></div><div className="grid lg:grid-cols-[1fr_320px]"><div className="p-6"><textarea aria-label="Resume content" className="min-h-[620px] w-full resize-y rounded-2xl border border-[#d0d5dd] bg-[#fcfcfd] p-5 font-mono text-sm leading-7 outline-none focus:border-[#5b4df5]" onChange={(event) => setMarkdown(event.target.value)} value={markdown} /></div><aside className="border-t border-[#edf0f3] bg-[#fafaff] p-6 lg:border-l lg:border-t-0"><div className="flex items-center gap-2"><ShieldAlert className="size-5 text-[#b54708]" /><h3 className="font-semibold">Truthfulness check</h3></div><p className="mt-2 text-xs leading-5 text-[#667085]">AI suggestions never enter the saved draft automatically. Review your own edits too.</p><Checklist title="Verified in draft" items={checklist.verified_claims ?? []} tone="green" /><Checklist title="Withheld for confirmation" items={checklist.needs_user_confirmation ?? []} tone="amber" /><Checklist title="Warnings" items={checklist.warnings ?? []} tone="neutral" />{checklist.ready_for_export ? <div className="mt-5 rounded-2xl bg-[#eafaf3] p-4 text-sm text-[#187957]"><p className="flex items-center gap-2 font-semibold"><CheckCircle2 className="size-4" />Reviewed and ready</p><div className="mt-3 flex gap-2"><button className="inline-flex items-center gap-1.5 rounded-lg bg-white px-3 py-2 text-xs font-semibold" onClick={() => exportFile("pdf")}><Download className="size-3.5" />PDF</button><button className="inline-flex items-center gap-1.5 rounded-lg bg-white px-3 py-2 text-xs font-semibold" onClick={() => exportFile("docx")}><Download className="size-3.5" />DOCX</button></div></div> : <button className="mt-5 w-full rounded-xl bg-[#172033] px-4 py-3 text-sm font-semibold text-white disabled:opacity-50" disabled={save.isPending} onClick={() => save.mutate({ confirm: true })}>I reviewed every claim</button>}{(save.error || exportError) && <p className="mt-3 text-xs text-red-600">{save.error?.message || exportError}</p>}</aside></div></article>;
}

function Checklist({ title, items, tone }: { title: string; items: string[]; tone: "green" | "amber" | "neutral" }) {
  if (!items.length) return null;
  const color = tone === "green" ? "text-[#187957]" : tone === "amber" ? "text-[#b54708]" : "text-[#667085]";
  return <div className="mt-5"><p className={`text-xs font-bold uppercase tracking-wider ${color}`}>{title}</p><ul className="mt-2 max-h-36 space-y-1.5 overflow-y-auto text-xs leading-5 text-[#475467]">{items.slice(0, 8).map((item, index) => <li key={`${item}-${index}`}>• {item}</li>)}</ul></div>;
}
