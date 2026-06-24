"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { CalendarDays, Check, LoaderCircle, RefreshCw } from "lucide-react";

import { PageHeader } from "@/components/app-shell";
import { useAuth } from "@/components/auth-provider";
import { ProjectRequired } from "@/components/project-required";
import { apiRequest } from "@/lib/api";
import type { WeeklyTask } from "@/lib/types";

export default function WeeklyPlanPage() {
  const { user } = useAuth();
  const projectId = user?.active_project_id;
  const queryClient = useQueryClient();
  const tasks = useQuery({ queryKey: ["weekly-plan", projectId], queryFn: () => apiRequest<WeeklyTask[]>(`/weekly-plan?project_id=${projectId}`), enabled: Boolean(projectId) });
  const generate = useMutation({ mutationFn: () => apiRequest<WeeklyTask[]>("/weekly-plan/generate", { method: "POST", body: JSON.stringify({ project_id: projectId }) }), onSuccess: (data) => queryClient.setQueryData(["weekly-plan", projectId], data) });
  const update = useMutation({ mutationFn: ({ id, status }: { id: string; status: WeeklyTask["status"] }) => apiRequest<WeeklyTask>(`/weekly-tasks/${id}`, { method: "PATCH", body: JSON.stringify({ status }) }), onSuccess: (updated) => queryClient.setQueryData<WeeklyTask[]>(["weekly-plan", projectId], (current = []) => current.map((task) => task.id === updated.id ? updated : task)) });
  const complete = tasks.data?.filter((task) => task.status === "complete").length ?? 0;
  const total = tasks.data?.length ?? 0;
  const progress = total ? Math.round(complete / total * 100) : 0;
  return <><PageHeader eyebrow="A repeatable search rhythm" title="Weekly plan" description="One realistic action per day, generated from the jobs, applications, and follow-ups already in your workspace." action={<button className="inline-flex items-center gap-2 rounded-xl bg-[#5b4df5] px-4 py-2.5 text-sm font-semibold text-white disabled:opacity-50" disabled={!projectId || generate.isPending} onClick={() => generate.mutate()}>{generate.isPending ? <LoaderCircle className="size-4 animate-spin" /> : <RefreshCw className="size-4" />}{total ? "Refresh this week" : "Build this week"}</button>} />{!projectId ? <ProjectRequired /> : <><section className="mt-8 rounded-3xl bg-[#182036] p-7 text-white"><div className="flex flex-wrap items-end justify-between gap-4"><div><p className="text-sm text-[#aeb6c8]">Weekly completion</p><p className="mt-2 text-4xl font-semibold">{progress}%</p></div><p className="text-sm text-[#c7cddb]">{complete} of {total || 7} actions complete</p></div><div className="mt-5 h-2 rounded-full bg-white/15"><div className="h-full rounded-full bg-[#77e4ba] transition-all" style={{ width: `${progress}%` }} /></div></section>{tasks.data?.length ? <section className="mt-6 grid gap-4 lg:grid-cols-2">{tasks.data.map((task) => <article className={`rounded-3xl border p-5 transition ${task.status === "complete" ? "border-[#b7ead7] bg-[#f2fbf7]" : "border-[#e4e7ec] bg-white"}`} key={task.id}><div className="flex items-start gap-4"><button aria-label={`Mark ${task.title} complete`} className={`mt-0.5 grid size-7 shrink-0 place-items-center rounded-full border ${task.status === "complete" ? "border-[#18835d] bg-[#18835d] text-white" : "border-[#cfd3dc] bg-white"}`} onClick={() => update.mutate({ id: task.id, status: task.status === "complete" ? "pending" : "complete" })}>{task.status === "complete" && <Check className="size-4" />}</button><div><div className="flex flex-wrap items-center gap-2"><p className="text-xs font-bold uppercase tracking-wider text-[#5b4df5]">{task.day_label}</p><span className="text-xs text-[#98a2b3]">{new Date(`${task.task_date}T00:00:00`).toLocaleDateString(undefined, { month: "short", day: "numeric" })}</span></div><h2 className={`mt-2 font-semibold ${task.status === "complete" ? "text-[#587066] line-through" : ""}`}>{task.title}</h2><p className="mt-2 text-sm leading-6 text-[#667085]">{task.description}</p></div></div></article>)}</section> : <button className="mt-6 w-full rounded-3xl border border-dashed border-[#cfd3dc] bg-white p-14 text-center" onClick={() => generate.mutate()}><CalendarDays className="mx-auto size-8 text-[#8c83f7]" /><span className="mt-4 block font-semibold">Turn your pipeline into a week you can execute</span><span className="mt-2 block text-sm text-[#667085]">Generate seven focused actions, then adjust them as your search changes.</span></button>}{generate.error && <p className="mt-4 text-sm text-red-600">{generate.error.message}</p>}</>}</>;
}
