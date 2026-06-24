"use client";

import { ArrowRight, BriefcaseBusiness, CalendarClock, Target } from "lucide-react";
import Link from "next/link";

import { useAuth } from "@/components/auth-provider";
import { PageHeader } from "@/components/app-shell";

export default function DashboardPage() {
  const { user } = useAuth();
  const firstName = user?.full_name.split(" ")[0] ?? "there";
  return <><PageHeader eyebrow="Your command centre" title={`Good to see you, ${firstName}.`} description="Start with one focused search project. Your fit scores, application activity, follow-ups, and weekly plan will gather here." action={<Link className="inline-flex items-center gap-2 rounded-xl bg-[#5b4df5] px-4 py-2.5 text-sm font-semibold text-white" href="/dashboard/projects">Manage projects <ArrowRight className="size-4" /></Link>} /><section className="mt-8 grid gap-4 sm:grid-cols-3">{[{ label: "Active applications", value: "—", icon: BriefcaseBusiness }, { label: "Average match", value: "—", icon: Target }, { label: "Follow-ups due", value: "—", icon: CalendarClock }].map(({ label, value, icon: Icon }) => <article className="rounded-3xl border border-[#e4e7ec] bg-white p-5" key={label}><div className="flex items-center justify-between"><p className="text-sm text-[#667085]">{label}</p><Icon className="size-5 text-[#8c83f7]" /></div><p className="mt-5 text-3xl font-semibold">{value}</p></article>)}</section><section className="mt-5 rounded-3xl border border-[#e4e7ec] bg-white p-7"><p className="text-sm font-semibold text-[#5b4df5]">Recommended next action</p><h2 className="mt-2 text-xl font-semibold">Create your first job-search project</h2><p className="mt-2 max-w-xl text-sm leading-6 text-[#667085]">A project keeps one role direction, candidate profile, criteria, and pipeline together.</p><Link className="mt-5 inline-flex items-center gap-2 text-sm font-semibold text-[#4b3ed0]" href="/dashboard/projects">Set up a project <ArrowRight className="size-4" /></Link></section></>;
}

