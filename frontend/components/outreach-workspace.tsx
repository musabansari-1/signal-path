"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Check, Copy, LoaderCircle, MessageSquareText, Save, ShieldCheck, Sparkles } from "lucide-react";
import { useState } from "react";

import { PageHeader } from "@/components/app-shell";
import { useAuth } from "@/components/auth-provider";
import { ProjectRequired } from "@/components/project-required";
import { apiRequest } from "@/lib/api";
import type { GeneratedMessage, Job } from "@/lib/types";

export function OutreachWorkspace({ initialJobId }: { initialJobId?: string }) {
  const { user } = useAuth();
  const projectId = user?.active_project_id;
  const queryClient = useQueryClient();
  const [jobId, setJobId] = useState(initialJobId ?? "");
  const [messageType, setMessageType] = useState("recruiter_dm");
  const [tone, setTone] = useState("professional");
  const [activeId, setActiveId] = useState<string | null>(null);
  const jobs = useQuery({ queryKey: ["jobs", projectId], queryFn: () => apiRequest<Job[]>(`/jobs?project_id=${projectId}`), enabled: Boolean(projectId) });
  const messages = useQuery({ queryKey: ["messages", projectId], queryFn: () => apiRequest<GeneratedMessage[]>(`/messages?project_id=${projectId}`), enabled: Boolean(projectId) });
  const generate = useMutation({
    mutationFn: () => apiRequest<GeneratedMessage>("/messages/generate", { method: "POST", body: JSON.stringify({ job_id: jobId, message_type: messageType, tone, length: "concise" }) }),
    onSuccess: (message) => {
      queryClient.setQueryData<GeneratedMessage[]>(["messages", projectId], (current = []) => [message, ...current]);
      setActiveId(message.id);
    },
  });
  const active = messages.data?.find((message) => message.id === activeId) ?? messages.data?.[0];

  return <><PageHeader eyebrow="Human-reviewed communication" title="Outreach" description="Create job-specific drafts from verified candidate facts. Nothing is sent automatically, and every draft stays editable." />{!projectId ? <ProjectRequired /> : <><section className="mt-8 rounded-3xl border border-[#e4e7ec] bg-white p-6"><div className="grid gap-4 lg:grid-cols-[1.4fr_1fr_1fr_auto] lg:items-end"><Select label="Target job" onChange={setJobId} value={jobId} options={[{ value: "", label: "Select a job" }, ...(jobs.data ?? []).map((job) => ({ value: job.id, label: `${job.title} · ${job.company_name}` }))]} /><Select label="Message type" onChange={setMessageType} value={messageType} options={[{ value: "recruiter_dm", label: "Recruiter DM" }, { value: "cover_letter", label: "Cover letter" }, { value: "hiring_manager_message", label: "Hiring manager" }, { value: "referral_request", label: "Referral request" }, { value: "follow_up", label: "Follow-up" }, { value: "fit_summary", label: "Why I’m a fit" }]} /><Select label="Tone" onChange={setTone} value={tone} options={["professional", "warm", "concise", "confident", "friendly", "startup"].map((value) => ({ value, label: value.replace("_", " ") }))} /><button className="inline-flex items-center justify-center gap-2 rounded-xl bg-[#5b4df5] px-5 py-3 text-sm font-semibold text-white disabled:opacity-50" disabled={!jobId || generate.isPending} onClick={() => generate.mutate()}>{generate.isPending ? <LoaderCircle className="size-4 animate-spin" /> : <Sparkles className="size-4" />}Generate draft</button></div>{generate.error && <p className="mt-3 text-sm text-red-600">{generate.error.message}</p>}</section><div className="mt-6 grid gap-6 xl:grid-cols-[300px_1fr]"><aside className="rounded-3xl border border-[#e4e7ec] bg-white p-4"><p className="px-2 pb-3 text-xs font-bold uppercase tracking-[.15em] text-[#98a2b3]">Saved drafts</p><div className="space-y-2">{messages.data?.length ? messages.data.map((message) => <button className={`w-full rounded-2xl p-3 text-left ${active?.id === message.id ? "bg-[#eeecff]" : "hover:bg-[#f7f8fb]"}`} key={message.id} onClick={() => setActiveId(message.id)}><p className="text-sm font-semibold capitalize">{message.message_type.replaceAll("_", " ")}</p><p className="mt-1 line-clamp-2 text-xs text-[#667085]">{message.subject_line || message.content}</p></button>) : <div className="px-2 py-8 text-center"><MessageSquareText className="mx-auto size-6 text-[#8c83f7]" /><p className="mt-3 text-sm text-[#667085]">No outreach drafts yet.</p></div>}</div></aside><section>{active ? <MessageEditor key={active.id + active.updated_at} message={active} /> : <div className="rounded-3xl border border-dashed border-[#cfd3dc] bg-white p-14 text-center"><MessageSquareText className="mx-auto size-8 text-[#8c83f7]" /><h2 className="mt-4 font-semibold">Write from evidence, not invention</h2><p className="mx-auto mt-2 max-w-md text-sm leading-6 text-[#667085]">Choose a job and message type. The final draft uses controlled language around exact verified facts.</p></div>}</section></div></>}</>;
}

function MessageEditor({ message }: { message: GeneratedMessage }) {
  const queryClient = useQueryClient();
  const [subject, setSubject] = useState(message.subject_line ?? "");
  const [content, setContent] = useState(message.content);
  const [copied, setCopied] = useState(false);
  const save = useMutation({
    mutationFn: () => apiRequest<GeneratedMessage>(`/messages/${message.id}`, { method: "PATCH", body: JSON.stringify({ subject_line: subject || null, content }) }),
    onSuccess: (updated) => queryClient.setQueryData<GeneratedMessage[]>(["messages", message.project_id], (current = []) => current.map((item) => item.id === updated.id ? updated : item)),
  });
  const copy = async () => {
    await navigator.clipboard.writeText([subject, content].filter(Boolean).join("\n\n"));
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1800);
  };
  return <article className="overflow-hidden rounded-3xl border border-[#e4e7ec] bg-white"><div className="flex flex-wrap items-center justify-between gap-3 border-b border-[#edf0f3] px-6 py-4"><div><h2 className="font-semibold capitalize">{message.message_type.replaceAll("_", " ")}</h2><p className="mt-1 text-xs capitalize text-[#667085]">{message.tone} tone · editable draft</p></div><div className="flex gap-2"><button className="inline-flex items-center gap-2 rounded-xl border border-[#d0d5dd] px-4 py-2 text-sm font-semibold" onClick={copy}>{copied ? <Check className="size-4 text-[#18835d]" /> : <Copy className="size-4" />}{copied ? "Copied" : "Copy"}</button><button className="inline-flex items-center gap-2 rounded-xl bg-[#172033] px-4 py-2 text-sm font-semibold text-white" disabled={save.isPending} onClick={() => save.mutate()}><Save className="size-4" />Save</button></div></div><div className="p-6 sm:p-8">{message.subject_line !== null && <label className="block text-sm font-semibold">Subject<input className="mt-2 w-full rounded-xl border border-[#d0d5dd] px-4 py-3 font-normal outline-none focus:border-[#5b4df5]" onChange={(event) => setSubject(event.target.value)} value={subject} /></label>}<label className="mt-5 block text-sm font-semibold">Message<textarea className="mt-2 min-h-72 w-full rounded-2xl border border-[#d0d5dd] bg-[#fcfcfd] p-5 font-normal leading-7 outline-none focus:border-[#5b4df5]" onChange={(event) => setContent(event.target.value)} value={content} /></label>{save.error && <p className="mt-3 text-sm text-red-600">{save.error.message}</p>}<div className="mt-6 rounded-2xl bg-[#eefbf6] p-5"><p className="flex items-center gap-2 text-sm font-semibold text-[#187957]"><ShieldCheck className="size-4" />Grounding report</p><p className="mt-2 text-sm text-[#476c5f]">{message.claims_used_json.length} verified candidate {message.claims_used_json.length === 1 ? "fact" : "facts"} used. Review before sending.</p>{message.review_warnings_json.length > 0 && <ul className="mt-3 space-y-1 text-xs leading-5 text-[#5f736c]">{message.review_warnings_json.map((warning) => <li key={warning}>• {warning}</li>)}</ul>}</div></div></article>;
}

function Select({ label, value, onChange, options }: { label: string; value: string; onChange: (value: string) => void; options: Array<{ value: string; label: string }> }) {
  return <label className="text-sm font-semibold">{label}<select className="mt-2 w-full rounded-xl border border-[#d0d5dd] bg-white px-4 py-3 font-normal capitalize outline-none focus:border-[#5b4df5]" onChange={(event) => onChange(event.target.value)} value={value}>{options.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}</select></label>;
}
