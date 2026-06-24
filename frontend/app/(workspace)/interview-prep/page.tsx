"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { BrainCircuit, CheckCircle2, CircleAlert, LoaderCircle, Sparkles } from "lucide-react";
import { useState } from "react";

import { PageHeader } from "@/components/app-shell";
import { useAuth } from "@/components/auth-provider";
import { ProjectRequired } from "@/components/project-required";
import { apiRequest } from "@/lib/api";
import type { InterviewPrepPlan, Job } from "@/lib/types";

export default function InterviewPrepPage() {
  const { user } = useAuth();
  const projectId = user?.active_project_id;
  const queryClient = useQueryClient();
  const [jobId, setJobId] = useState("");
  const [stage, setStage] = useState("screening");
  const [activeId, setActiveId] = useState<string | null>(null);
  const jobs = useQuery({ queryKey: ["jobs", projectId], queryFn: () => apiRequest<Job[]>(`/jobs?project_id=${projectId}`), enabled: Boolean(projectId) });
  const plans = useQuery({ queryKey: ["interview-prep", projectId], queryFn: () => apiRequest<InterviewPrepPlan[]>(`/interview-prep?project_id=${projectId}`), enabled: Boolean(projectId) });
  const generate = useMutation({
    mutationFn: () => apiRequest<InterviewPrepPlan>("/interview-prep/generate", { method: "POST", body: JSON.stringify({ job_id: jobId, interview_stage: stage }) }),
    onSuccess: (plan) => {
      queryClient.setQueryData<InterviewPrepPlan[]>(["interview-prep", projectId], (current = []) => [plan, ...current]);
      setActiveId(plan.id);
    },
  });
  const active = plans.data?.find((plan) => plan.id === activeId) ?? plans.data?.[0];
  return <><PageHeader eyebrow="Practice from real evidence" title="Interview prep" description="Turn the role’s requirements into focused practice. Behavioral prompts point to verified source facts—or clearly ask you to add one." />{!projectId ? <ProjectRequired /> : <><section className="mt-8 rounded-3xl border border-[#e4e7ec] bg-white p-6"><div className="grid gap-4 sm:grid-cols-[1fr_220px_auto] sm:items-end"><label className="text-sm font-semibold">Target job<select className="mt-2 w-full rounded-xl border border-[#d0d5dd] bg-white px-4 py-3 font-normal" onChange={(event) => setJobId(event.target.value)} value={jobId}><option value="">Select a job</option>{jobs.data?.map((job) => <option key={job.id} value={job.id}>{job.title} · {job.company_name}</option>)}</select></label><label className="text-sm font-semibold">Interview stage<select className="mt-2 w-full rounded-xl border border-[#d0d5dd] bg-white px-4 py-3 font-normal capitalize" onChange={(event) => setStage(event.target.value)} value={stage}>{["screening", "technical", "behavioral", "system_design", "final"].map((item) => <option key={item} value={item}>{item.replace("_", " ")}</option>)}</select></label><button className="inline-flex items-center justify-center gap-2 rounded-xl bg-[#5b4df5] px-5 py-3 text-sm font-semibold text-white disabled:opacity-50" disabled={!jobId || generate.isPending} onClick={() => generate.mutate()}>{generate.isPending ? <LoaderCircle className="size-4 animate-spin" /> : <Sparkles className="size-4" />}Build plan</button></div>{generate.error && <p className="mt-3 text-sm text-red-600">{generate.error.message}</p>}</section><div className="mt-6 grid gap-6 xl:grid-cols-[280px_1fr]"><aside className="rounded-3xl border border-[#e4e7ec] bg-white p-4"><p className="px-2 pb-3 text-xs font-bold uppercase tracking-wider text-[#98a2b3]">Prep plans</p>{plans.data?.map((plan) => <button className={`mb-2 w-full rounded-2xl p-3 text-left ${active?.id === plan.id ? "bg-[#eeecff]" : "hover:bg-[#f7f8fb]"}`} key={plan.id} onClick={() => setActiveId(plan.id)}><p className="text-sm font-semibold capitalize">{plan.interview_stage.replace("_", " ")}</p><p className="mt-1 text-xs text-[#667085]">{plan.technical_questions.length} technical prompts</p></button>)}</aside>{active ? <PlanView plan={active} /> : <section className="rounded-3xl border border-dashed border-[#cfd3dc] bg-white p-14 text-center"><BrainCircuit className="mx-auto size-8 text-[#8c83f7]" /><h2 className="mt-4 font-semibold">Build your first practice plan</h2><p className="mx-auto mt-2 max-w-md text-sm leading-6 text-[#667085]">Choose a job and interview stage to create role-specific questions and research tasks.</p></section>}</div></>}</>;
}

function PlanView({ plan }: { plan: InterviewPrepPlan }) {
  return <section className="space-y-6"><article className="rounded-3xl border border-[#e4e7ec] bg-white p-6 sm:p-8"><div className="flex items-center gap-3"><BrainCircuit className="size-6 text-[#5b4df5]" /><div><h2 className="text-xl font-semibold capitalize">{plan.interview_stage.replace("_", " ")} plan</h2><p className="text-sm text-[#667085]">Questions reflect the saved job description.</p></div></div><h3 className="mt-7 text-sm font-bold uppercase tracking-wider text-[#667085]">Technical questions</h3><div className="mt-3 space-y-3">{plan.technical_questions.map((question, index) => <div className="rounded-2xl bg-[#f8f8fb] p-4" key={String(question.id ?? index)}><p className="text-sm font-semibold leading-6">{String(question.question)}</p><p className={`mt-2 flex items-center gap-1.5 text-xs ${question.candidate_has_verified_evidence ? "text-[#187957]" : "text-[#b54708]"}`}>{question.candidate_has_verified_evidence ? <CheckCircle2 className="size-3.5" /> : <CircleAlert className="size-3.5" />}{question.candidate_has_verified_evidence ? "Verified profile evidence exists" : "Treat this as a learning gap, not claimed experience"}</p></div>)}</div></article><article className="rounded-3xl border border-[#e4e7ec] bg-white p-6 sm:p-8"><h2 className="text-lg font-semibold">Behavioral evidence</h2><div className="mt-4 space-y-3">{plan.behavioral_questions.map((question, index) => <div className="rounded-2xl border border-[#edf0f3] p-4" key={String(question.id ?? index)}><p className="text-sm font-semibold">{String(question.question)}</p>{question.verified_source ? <p className="mt-2 text-sm leading-6 text-[#475467]">Verified source: {String(question.verified_source)}</p> : null}<p className="mt-2 text-xs leading-5 text-[#b54708]">{String(question.note)}</p></div>)}</div></article><article className="grid gap-5 sm:grid-cols-2"><Checklist title="Company research" items={plan.company_research} /><Checklist title="Questions to ask" items={plan.questions_to_ask} /></article></section>;
}

function Checklist({ title, items }: { title: string; items: string[] }) {
  return <div className="rounded-3xl border border-[#e4e7ec] bg-white p-6"><h2 className="font-semibold">{title}</h2><ul className="mt-4 space-y-3 text-sm leading-6 text-[#475467]">{items.map((item) => <li className="flex gap-2" key={item}><span className="text-[#8c83f7]">•</span>{item}</li>)}</ul></div>;
}
