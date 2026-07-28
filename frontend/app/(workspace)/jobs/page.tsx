"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  ArrowUpRight,
  BriefcaseBusiness,
  FileUp,
  Globe2,
  LoaderCircle,
  MapPin,
  Plus,
  Search,
  Sparkles,
} from "lucide-react";
import Link from "next/link";
import { useRef, useState } from "react";

import { PageHeader } from "@/components/app-shell";
import { useAuth } from "@/components/auth-provider";
import { ProjectRequired } from "@/components/project-required";
import { apiRequest } from "@/lib/api";
import type { Job, JobDiscoveryResult } from "@/lib/types";

const emptyForm = {
  company_name: "",
  title: "",
  description: "",
  source_url: "",
  location: "",
  work_mode: "",
};

export default function JobsPage() {
  const { user } = useAuth();
  const projectId = user?.active_project_id;
  const queryClient = useQueryClient();
  const csvInput = useRef<HTMLInputElement>(null);
  const [showForm, setShowForm] = useState(false);
  const [search, setSearch] = useState("");
  const [form, setForm] = useState(emptyForm);
  const jobs = useQuery({
    queryKey: ["jobs", projectId],
    queryFn: () => apiRequest<Job[]>(`/jobs?project_id=${projectId}`),
    enabled: Boolean(projectId),
  });
  const create = useMutation({
    mutationFn: async () => {
      const created = await apiRequest<Job>("/jobs", {
        method: "POST",
        body: JSON.stringify({
          ...form,
          project_id: projectId,
          source_url: form.source_url || null,
          location: form.location || null,
          work_mode: form.work_mode || null,
        }),
      });
      return apiRequest<Job>(`/jobs/${created.id}/parse`, { method: "POST" }).catch(() => created);
    },
    onSuccess: (job) => {
      queryClient.setQueryData<Job[]>(["jobs", projectId], (current = []) => [job, ...current]);
      setForm(emptyForm);
      setShowForm(false);
    },
  });
  const importCsv = useMutation({
    mutationFn: (file: File) => {
      const data = new FormData();
      data.append("project_id", projectId!);
      data.append("file", file);
      return apiRequest<{ imported: number; skipped: number; errors: string[] }>("/jobs/import-csv", {
        method: "POST",
        body: data,
      });
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["jobs", projectId] }),
  });
  const discover = useMutation({
    mutationFn: () =>
      apiRequest<JobDiscoveryResult>("/jobs/discover", {
        method: "POST",
        body: JSON.stringify({ project_id: projectId, limit: 15 }),
      }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["jobs", projectId] }),
  });
  const visible =
    jobs.data?.filter((job) =>
      `${job.title} ${job.company_name}`.toLowerCase().includes(search.toLowerCase()),
    ) ?? [];

  return (
    <>
      <PageHeader
        eyebrow="Opportunity signal"
        title="Job inbox"
        description="Discover remote roles from your confirmed profile, then use evidence and criteria to decide which deserve a careful application."
        action={
          <div className="flex flex-wrap gap-2">
            <button
              className="inline-flex items-center gap-2 rounded-xl border border-[#d0d5dd] bg-white px-4 py-2.5 text-sm font-semibold text-[#344054] disabled:opacity-50"
              disabled={!projectId || discover.isPending}
              onClick={() => discover.mutate()}
            >
              {discover.isPending ? <LoaderCircle className="size-4 animate-spin" /> : <Globe2 className="size-4" />}
              Find matching jobs
            </button>
            <button className="inline-flex items-center gap-2 rounded-xl border border-[#d0d5dd] bg-white px-4 py-2.5 text-sm font-semibold text-[#344054]" onClick={() => csvInput.current?.click()}>
              <FileUp className="size-4" />Import CSV
            </button>
            <input
              accept=".csv,text/csv"
              className="hidden"
              onChange={(event) => {
                const file = event.target.files?.[0];
                if (file) importCsv.mutate(file);
                event.target.value = "";
              }}
              ref={csvInput}
              type="file"
            />
            <button className="inline-flex items-center gap-2 rounded-xl bg-[#5b4df5] px-4 py-2.5 text-sm font-semibold text-white" onClick={() => setShowForm(true)}>
              <Plus className="size-4" />Add job
            </button>
          </div>
        }
      />
      {!projectId ? <ProjectRequired /> : <>
        {showForm && <JobForm create={create} form={form} setForm={setForm} onCancel={() => setShowForm(false)} />}
        <div className="mt-7 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <label className="relative block max-w-md flex-1">
            <Search className="absolute left-3.5 top-3 size-4 text-[#98a2b3]" />
            <input className="w-full rounded-xl border border-[#d0d5dd] bg-white py-2.5 pl-10 pr-4 text-sm outline-none focus:border-[#5b4df5]" onChange={(event) => setSearch(event.target.value)} placeholder="Search company or role" value={search} />
          </label>
          <p className="text-sm text-[#667085]">{visible.length} {visible.length === 1 ? "opportunity" : "opportunities"}</p>
        </div>
        {discover.data && <p className="mt-4 rounded-xl bg-[#eefbf6] px-4 py-3 text-sm text-[#187957]">Searched for “{discover.data.searched_for}”: added {discover.data.imported} matching jobs and skipped {discover.data.skipped} already saved listings.</p>}
        {discover.error && <p className="mt-4 text-sm text-red-600">{discover.error.message}</p>}
        {importCsv.data && <p className="mt-4 rounded-xl bg-[#eefbf6] px-4 py-3 text-sm text-[#187957]">Imported {importCsv.data.imported} jobs; skipped {importCsv.data.skipped}.</p>}
        {importCsv.error && <p className="mt-4 text-sm text-red-600">{importCsv.error.message}</p>}
        <section className="mt-5 overflow-hidden rounded-3xl border border-[#e4e7ec] bg-white">
          {jobs.isLoading ? <p className="p-8 text-sm text-[#667085]">Loading opportunities…</p> : visible.length ? <JobList jobs={visible} /> : <button className="w-full p-14 text-center disabled:opacity-50" disabled={discover.isPending} onClick={() => discover.mutate()}><Globe2 className="mx-auto size-8 text-[#8c83f7]" /><span className="mt-4 block font-semibold">Find roles that match your profile</span><span className="mt-2 block text-sm text-[#667085]">Search live remote listings using your target roles and confirmed skills.</span></button>}
        </section>
      </>}
    </>
  );
}

function JobForm({ create, form, setForm, onCancel }: { create: ReturnType<typeof useMutation<Job, Error, void>>; form: typeof emptyForm; setForm: (value: typeof emptyForm) => void; onCancel: () => void }) {
  return <form className="mt-7 rounded-3xl border border-[#dcd9ff] bg-white p-6 shadow-sm" onSubmit={(event) => { event.preventDefault(); create.mutate(); }}><div className="flex items-center justify-between"><div><h2 className="text-lg font-semibold">Add an opportunity</h2><p className="mt-1 text-sm text-[#667085]">Paste the employer’s description; Rolewise will structure only what it can find.</p></div><Sparkles className="size-5 text-[#8c83f7]" /></div><div className="mt-5 grid gap-4 sm:grid-cols-2"><Field label="Company" required value={form.company_name} onChange={(value) => setForm({ ...form, company_name: value })} placeholder="Acme" /><Field label="Role title" required value={form.title} onChange={(value) => setForm({ ...form, title: value })} placeholder="Backend engineer" /><Field label="Location" value={form.location} onChange={(value) => setForm({ ...form, location: value })} placeholder="Bengaluru or remote" /><Field label="Job URL" type="url" value={form.source_url} onChange={(value) => setForm({ ...form, source_url: value })} placeholder="https://…" /></div><label className="mt-4 block text-sm font-semibold">Job description<textarea className="mt-2 min-h-52 w-full rounded-xl border border-[#d0d5dd] px-4 py-3 font-normal leading-6 outline-none focus:border-[#5b4df5]" minLength={20} onChange={(event) => setForm({ ...form, description: event.target.value })} required value={form.description} /></label>{create.error && <p className="mt-3 text-sm text-red-600">{create.error.message}</p>}<div className="mt-5 flex justify-end gap-3"><button className="rounded-xl px-4 py-2.5 text-sm font-semibold text-[#475467]" onClick={onCancel} type="button">Cancel</button><button className="inline-flex items-center gap-2 rounded-xl bg-[#172033] px-5 py-2.5 text-sm font-semibold text-white disabled:opacity-50" disabled={create.isPending}>{create.isPending && <LoaderCircle className="size-4 animate-spin" />}Save and parse</button></div></form>;
}

function JobList({ jobs }: { jobs: Job[] }) {
  return <div className="divide-y divide-[#edf0f3]">{jobs.map((job) => <Link className="grid gap-4 p-5 transition hover:bg-[#fafaff] sm:grid-cols-[1fr_auto] sm:items-center" href={`/jobs/${job.id}`} key={job.id}><div className="flex min-w-0 items-start gap-4"><div className="grid size-11 shrink-0 place-items-center rounded-2xl bg-[#f0efff] text-[#5b4df5]"><BriefcaseBusiness className="size-5" /></div><div className="min-w-0"><div className="flex flex-wrap items-center gap-2"><h2 className="font-semibold">{job.title}</h2><span className="rounded-full bg-[#f2f4f7] px-2.5 py-1 text-[11px] font-semibold capitalize text-[#475467]">{job.status}</span></div><p className="mt-1 text-sm text-[#667085]">{job.company_name}</p><div className="mt-2 flex flex-wrap gap-3 text-xs text-[#667085]">{job.location && <span className="flex items-center gap-1"><MapPin className="size-3.5" />{job.location}</span>}{job.work_mode && <span className="capitalize">{job.work_mode}</span>}<span>{job.source_type}</span></div></div></div><div className="flex items-center justify-between gap-5 sm:justify-end">{job.latest_score !== null ? <div className="text-right"><p className={`text-2xl font-bold ${job.latest_score >= 80 ? "text-[#18835d]" : job.latest_score >= 60 ? "text-[#5b4df5]" : "text-[#b54708]"}`}>{job.latest_score}</p><p className="text-[11px] uppercase tracking-wider text-[#98a2b3]">Match</p></div> : <span className="text-xs font-semibold text-[#8c83f7]">Ready to score</span>}<ArrowUpRight className="size-5 text-[#98a2b3]" /></div></Link>)}</div>;
}

function Field({ label, value, onChange, placeholder, required, type = "text" }: { label: string; value: string; onChange: (value: string) => void; placeholder: string; required?: boolean; type?: string }) {
  return <label className="text-sm font-semibold">{label}<input className="mt-2 w-full rounded-xl border border-[#d0d5dd] px-4 py-3 font-normal outline-none focus:border-[#5b4df5]" onChange={(event) => onChange(event.target.value)} placeholder={placeholder} required={required} type={type} value={value} /></label>;
}
