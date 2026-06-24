"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Check, LoaderCircle, MapPin, Plus, Target } from "lucide-react";
import { useState } from "react";

import { useAuth } from "@/components/auth-provider";
import { PageHeader } from "@/components/app-shell";
import { apiRequest } from "@/lib/api";
import type { Project, User } from "@/lib/types";

export default function ProjectsPage() {
  const { user, setUser } = useAuth();
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: "", target_role: "", target_location: "", target_industry: "", description: "" });
  const projects = useQuery({ queryKey: ["projects"], queryFn: () => apiRequest<Project[]>("/projects") });
  const create = useMutation({
    mutationFn: () => apiRequest<Project>("/projects", { method: "POST", body: JSON.stringify(form) }),
    onSuccess: (project) => {
      queryClient.setQueryData<Project[]>(["projects"], (current = []) => [project, ...current]);
      if (user && !user.active_project_id) setUser({ ...user, active_project_id: project.id });
      setForm({ name: "", target_role: "", target_location: "", target_industry: "", description: "" });
      setShowForm(false);
    },
  });
  const activate = useMutation({
    mutationFn: (id: string) => apiRequest<Project>(`/projects/${id}/activate`, { method: "POST" }),
    onSuccess: (project) => {
      if (user) setUser({ ...user, active_project_id: project.id } as User);
    },
  });

  return <><PageHeader eyebrow="Search directions" title="Projects" description="Keep distinct role searches focused. Every profile, criterion, job, and application will belong to one project." action={<button className="inline-flex items-center gap-2 rounded-xl bg-[#5b4df5] px-4 py-2.5 text-sm font-semibold text-white" onClick={() => setShowForm(true)}><Plus className="size-4" />New project</button>} />{showForm && <form className="mt-7 rounded-3xl border border-[#dcd9ff] bg-white p-6 shadow-sm" onSubmit={(event) => { event.preventDefault(); create.mutate(); }}><h2 className="text-lg font-semibold">Create a focused search</h2><div className="mt-5 grid gap-4 sm:grid-cols-2"><Input label="Project name" required value={form.name} onChange={(value) => setForm({ ...form, name: value })} placeholder="Backend roles · Summer 2026" /><Input label="Target role" required value={form.target_role} onChange={(value) => setForm({ ...form, target_role: value })} placeholder="Backend engineer" /><Input label="Location" value={form.target_location} onChange={(value) => setForm({ ...form, target_location: value })} placeholder="Remote · India" /><Input label="Industry" value={form.target_industry} onChange={(value) => setForm({ ...form, target_industry: value })} placeholder="Developer tools" /></div><label className="mt-4 block text-sm font-semibold">What would make this search successful?<textarea className="mt-2 min-h-24 w-full rounded-xl border border-[#d0d5dd] px-4 py-3 font-normal outline-none focus:border-[#5b4df5]" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} /></label>{create.error && <p className="mt-3 text-sm text-red-600">{create.error.message}</p>}<div className="mt-5 flex justify-end gap-3"><button className="rounded-xl px-4 py-2.5 text-sm font-semibold text-[#475467]" onClick={() => setShowForm(false)} type="button">Cancel</button><button className="inline-flex items-center gap-2 rounded-xl bg-[#172033] px-4 py-2.5 text-sm font-semibold text-white disabled:opacity-50" disabled={create.isPending || !form.name || !form.target_role}>{create.isPending && <LoaderCircle className="size-4 animate-spin" />}Create project</button></div></form>}
  <section className="mt-7 grid gap-4 lg:grid-cols-2">{projects.isLoading ? <p className="text-sm text-[#667085]">Loading projects…</p> : projects.data?.length ? projects.data.map((project) => { const active = user?.active_project_id === project.id; return <article className={`rounded-3xl border bg-white p-6 ${active ? "border-[#8c83f7] shadow-[0_10px_30px_rgba(91,77,245,.08)]" : "border-[#e4e7ec]"}`} key={project.id}><div className="flex items-start justify-between gap-4"><div><div className="flex items-center gap-2"><h2 className="text-lg font-semibold">{project.name}</h2>{active && <span className="rounded-full bg-[#eeecff] px-2.5 py-1 text-[11px] font-bold uppercase tracking-wider text-[#4b3ed0]">Active</span>}</div><p className="mt-2 text-sm leading-6 text-[#667085]">{project.description || "A focused search workspace ready for your profile and criteria."}</p></div><span className="rounded-full bg-[#eefbf6] px-2.5 py-1 text-xs font-semibold text-[#187957]">{project.status}</span></div><div className="mt-5 flex flex-wrap gap-4 border-t border-[#edf0f3] pt-4 text-sm text-[#475467]"><span className="flex items-center gap-2"><Target className="size-4 text-[#8c83f7]" />{project.target_role}</span>{project.target_location && <span className="flex items-center gap-2"><MapPin className="size-4 text-[#8c83f7]" />{project.target_location}</span>}</div>{!active && <button className="mt-5 inline-flex items-center gap-2 text-sm font-semibold text-[#4b3ed0]" onClick={() => activate.mutate(project.id)}><Check className="size-4" />Make active</button>}</article>; }) : <button className="rounded-3xl border border-dashed border-[#cfd3dc] bg-white p-12 text-center lg:col-span-2" onClick={() => setShowForm(true)}><Plus className="mx-auto size-7 text-[#8c83f7]" /><span className="mt-3 block font-semibold">Create your first project</span><span className="mt-1 block text-sm text-[#667085]">Give this job search a clear role and outcome.</span></button>}</section></>;
}

function Input({ label, value, onChange, placeholder, required }: { label: string; value: string; onChange: (value: string) => void; placeholder: string; required?: boolean }) {
  return <label className="text-sm font-semibold">{label}<input className="mt-2 w-full rounded-xl border border-[#d0d5dd] px-4 py-3 font-normal outline-none focus:border-[#5b4df5]" onChange={(event) => onChange(event.target.value)} placeholder={placeholder} required={required} value={value} /></label>;
}

