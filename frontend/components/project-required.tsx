import { FolderPlus } from "lucide-react";
import Link from "next/link";

export function ProjectRequired() {
  return <section className="mt-8 rounded-3xl border border-dashed border-[#cfd3dc] bg-white p-12 text-center"><FolderPlus className="mx-auto size-8 text-[#8c83f7]" /><h2 className="mt-4 text-lg font-semibold">Choose a search project first</h2><p className="mx-auto mt-2 max-w-md text-sm leading-6 text-[#667085]">Your candidate profile and criteria stay attached to a specific search direction.</p><Link className="mt-5 inline-flex rounded-xl bg-[#5b4df5] px-4 py-2.5 text-sm font-semibold text-white" href="/dashboard/projects">Manage projects</Link></section>;
}
