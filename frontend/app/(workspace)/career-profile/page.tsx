"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { CheckCircle2, FileText, LoaderCircle, ShieldCheck, Sparkles, Trash2, UploadCloud } from "lucide-react";
import { useRef, useState } from "react";

import { PageHeader } from "@/components/app-shell";
import { useAuth } from "@/components/auth-provider";
import { ProjectRequired } from "@/components/project-required";
import { apiRequest } from "@/lib/api";
import type { CandidateProfile, CareerAsset } from "@/lib/types";

export default function CareerProfilePage() {
  const { user } = useAuth();
  const projectId = user?.active_project_id;
  const queryClient = useQueryClient();
  const fileInput = useRef<HTMLInputElement>(null);
  const [uploadError, setUploadError] = useState("");
  const assets = useQuery({
    queryKey: ["career-assets", projectId],
    queryFn: () => apiRequest<CareerAsset[]>(`/career-assets?project_id=${projectId}`),
    enabled: Boolean(projectId),
  });
  const profile = useQuery({
    queryKey: ["candidate-profile", projectId],
    queryFn: () => apiRequest<CandidateProfile | null>(`/candidate-profile?project_id=${projectId}`),
    enabled: Boolean(projectId),
  });
  const upload = useMutation({
    mutationFn: async (file: File) => {
      const data = new FormData();
      data.append("project_id", projectId!);
      data.append("file", file);
      data.append("asset_type", "resume");
      data.append("is_primary", String(!(assets.data?.length)));
      return apiRequest<CareerAsset>("/career-assets/upload", { method: "POST", body: data });
    },
    onSuccess: () => {
      setUploadError("");
      queryClient.invalidateQueries({ queryKey: ["career-assets", projectId] });
    },
    onError: (error) => setUploadError(error.message),
  });
  const analyze = useMutation({
    mutationFn: () => apiRequest<CandidateProfile>("/candidate-profile/analyze", { method: "POST", body: JSON.stringify({ project_id: projectId }) }),
    onSuccess: (data) => queryClient.setQueryData(["candidate-profile", projectId], data),
  });
  const remove = useMutation({
    mutationFn: (id: string) => apiRequest<void>(`/career-assets/${id}`, { method: "DELETE" }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["career-assets", projectId] }),
  });

  return <><PageHeader eyebrow="Your source of truth" title="Career profile" description="Upload the material you trust. Rolewise separates evidence-backed facts from suggestions before anything can reach a resume or message." action={assets.data?.length ? <button className="inline-flex items-center gap-2 rounded-xl bg-[#172033] px-4 py-2.5 text-sm font-semibold text-white disabled:opacity-50" disabled={analyze.isPending} onClick={() => analyze.mutate()}>{analyze.isPending ? <LoaderCircle className="size-4 animate-spin" /> : <Sparkles className="size-4" />}Analyze materials</button> : undefined} />{!projectId ? <ProjectRequired /> : <div className="mt-8 grid gap-6 xl:grid-cols-[.72fr_1.28fr]"><section className="space-y-5"><article className="rounded-3xl border border-[#e4e7ec] bg-white p-6"><div className="flex items-center gap-3"><div className="grid size-11 place-items-center rounded-2xl bg-[#eeecff] text-[#5b4df5]"><UploadCloud className="size-5" /></div><div><h2 className="font-semibold">Career materials</h2><p className="text-sm text-[#667085]">PDF, DOCX, TXT, or Markdown · up to 8 MB</p></div></div><button className="mt-5 w-full rounded-2xl border border-dashed border-[#b9b4f9] bg-[#faf9ff] px-5 py-8 text-sm font-semibold text-[#4b3ed0] hover:bg-[#f3f1ff]" onClick={() => fileInput.current?.click()}>{upload.isPending ? "Reading your file…" : "Choose a resume or career file"}</button><input accept=".pdf,.docx,.txt,.md" className="hidden" onChange={(event) => { const file = event.target.files?.[0]; if (file) upload.mutate(file); event.target.value = ""; }} ref={fileInput} type="file" />{uploadError && <p className="mt-3 text-sm text-red-600">{uploadError}</p>}<div className="mt-5 space-y-3">{assets.data?.map((asset) => <div className="flex items-center gap-3 rounded-2xl border border-[#edf0f3] p-3" key={asset.id}><FileText className="size-5 shrink-0 text-[#8c83f7]" /><div className="min-w-0 flex-1"><p className="truncate text-sm font-semibold">{asset.title}</p><p className="text-xs text-[#667085]">{asset.is_primary ? "Primary resume" : asset.asset_type.replace("_", " ")}</p></div><button aria-label={`Delete ${asset.title}`} className="rounded-lg p-2 text-[#98a2b3] hover:bg-red-50 hover:text-red-600" onClick={() => remove.mutate(asset.id)}><Trash2 className="size-4" /></button></div>)}</div></article><article className="rounded-3xl bg-[#182036] p-6 text-white"><ShieldCheck className="size-6 text-[#77e4ba]" /><h2 className="mt-4 font-semibold">Evidence before eloquence</h2><p className="mt-2 text-sm leading-6 text-[#bdc4d4]">AI-extracted facts are accepted only when their supporting quote exists in the uploaded source. You still review the result.</p></article></section><section>{profile.isLoading ? <div className="rounded-3xl border bg-white p-10 text-sm text-[#667085]">Loading profile…</div> : profile.data ? <ProfileEditor key={profile.data.updated_at} profile={profile.data} /> : <div className="rounded-3xl border border-dashed border-[#cfd3dc] bg-white p-12 text-center"><Sparkles className="mx-auto size-8 text-[#8c83f7]" /><h2 className="mt-4 text-lg font-semibold">Turn your materials into a profile</h2><p className="mx-auto mt-2 max-w-lg text-sm leading-6 text-[#667085]">Upload at least one readable file, then analyze it. Without an AI key, a conservative local extractor identifies only explicitly named technical skills.</p><button className="mt-5 rounded-xl bg-[#5b4df5] px-4 py-2.5 text-sm font-semibold text-white disabled:opacity-50" disabled={!assets.data?.length || analyze.isPending} onClick={() => analyze.mutate()}>Analyze my materials</button>{analyze.error && <p className="mt-3 text-sm text-red-600">{analyze.error.message}</p>}</div>}</section></div>}</>;
}

function ProfileEditor({ profile }: { profile: CandidateProfile }) {
  const queryClient = useQueryClient();
  const [draft, setDraft] = useState({ headline: profile.headline ?? "", summary: profile.summary ?? "", location: profile.location ?? "", skills: profile.skills_json.join(", ") });
  const save = useMutation({
    mutationFn: () => apiRequest<CandidateProfile>(`/candidate-profile?project_id=${profile.project_id}`, { method: "PATCH", body: JSON.stringify({ headline: draft.headline || null, summary: draft.summary || null, location: draft.location || null, skills_json: draft.skills.split(",").map((item) => item.trim()).filter(Boolean) }) }),
    onSuccess: (data) => queryClient.setQueryData(["candidate-profile", profile.project_id], data),
  });
  const verifiedCount = profile.verified_facts_json.filter((fact) => fact.verification === "source_quote").length;
  return <article className="rounded-3xl border border-[#e4e7ec] bg-white p-6 sm:p-8"><div className="flex flex-wrap items-start justify-between gap-3"><div><p className="text-xs font-bold uppercase tracking-[.15em] text-[#5b4df5]">Editable profile</p><h2 className="mt-2 text-2xl font-semibold">What employers should know</h2></div><span className="inline-flex items-center gap-1.5 rounded-full bg-[#eefbf6] px-3 py-1.5 text-xs font-semibold text-[#187957]"><CheckCircle2 className="size-4" />{verifiedCount} source-verified facts</span></div><div className="mt-7 grid gap-5"><TextField label="Headline" value={draft.headline} onChange={(value) => setDraft({ ...draft, headline: value })} placeholder="Your professional headline" /><TextField label="Location" value={draft.location} onChange={(value) => setDraft({ ...draft, location: value })} placeholder="City, country, or remote preference" /><label className="text-sm font-semibold">Summary<textarea className="mt-2 min-h-28 w-full rounded-xl border border-[#d0d5dd] px-4 py-3 font-normal leading-6 outline-none focus:border-[#5b4df5]" onChange={(event) => setDraft({ ...draft, summary: event.target.value })} value={draft.summary} /></label><TextField label="Confirmed skills · comma separated" value={draft.skills} onChange={(value) => setDraft({ ...draft, skills: value })} placeholder="TypeScript, React, FastAPI" /></div><div className="mt-6 flex items-center justify-between gap-3 border-t border-[#edf0f3] pt-5"><p className="text-xs leading-5 text-[#667085]">Saving marks your edits as user-confirmed facts.</p><button className="rounded-xl bg-[#172033] px-4 py-2.5 text-sm font-semibold text-white disabled:opacity-50" disabled={save.isPending} onClick={() => save.mutate()}>{save.isPending ? "Saving…" : "Save profile"}</button></div>{save.error && <p className="mt-3 text-sm text-red-600">{save.error.message}</p>}{profile.suggestions_json.length > 0 && <div className="mt-7 rounded-2xl bg-[#fff9ed] p-5"><p className="text-sm font-semibold text-[#9a5b13]">Questions and suggestions for review</p><ul className="mt-3 space-y-2 text-sm leading-6 text-[#6b4b20]">{profile.suggestions_json.slice(0, 6).map((item, index) => <li key={index}>• {String(item.text ?? item.reason ?? "Review an unsupported extracted claim")}</li>)}</ul></div>}</article>;
}

function TextField({ label, value, onChange, placeholder }: { label: string; value: string; onChange: (value: string) => void; placeholder: string }) {
  return <label className="text-sm font-semibold">{label}<input className="mt-2 w-full rounded-xl border border-[#d0d5dd] px-4 py-3 font-normal outline-none focus:border-[#5b4df5]" onChange={(event) => onChange(event.target.value)} placeholder={placeholder} value={value} /></label>;
}
