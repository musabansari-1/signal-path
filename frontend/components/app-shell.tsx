"use client";

import {
  BarChart3, BriefcaseBusiness, CalendarCheck2, ChevronDown, CircleUserRound,
  Files, FolderKanban, Gauge, LogOut, Menu, MessagesSquare, Search, Settings,
  Sparkles, Target, X,
} from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState, type ReactNode } from "react";

import { useAuth } from "@/components/auth-provider";

const nav = [
  { href: "/dashboard", label: "Dashboard", icon: Gauge },
  { href: "/career-profile", label: "Career profile", icon: CircleUserRound },
  { href: "/role-criteria", label: "Role criteria", icon: Target },
  { href: "/jobs", label: "Job inbox", icon: Search },
  { href: "/applications", label: "Applications", icon: FolderKanban },
  { href: "/resumes", label: "Resumes", icon: Files },
  { href: "/outreach", label: "Outreach", icon: MessagesSquare },
  { href: "/interview-prep", label: "Interview prep", icon: Sparkles },
  { href: "/portfolio-review", label: "Portfolio review", icon: BriefcaseBusiness },
  { href: "/weekly-plan", label: "Weekly plan", icon: CalendarCheck2 },
];

export function AppShell({ children }: { children: ReactNode }) {
  const { user, isLoading, logout } = useAuth();
  const router = useRouter();
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    if (!isLoading && !user) router.replace(`/login?next=${encodeURIComponent(pathname)}`);
  }, [isLoading, pathname, router, user]);

  if (isLoading || !user) {
    return <div className="grid min-h-screen place-items-center bg-[#f7f8fb]"><div className="size-8 animate-spin rounded-full border-2 border-[#d9d6ff] border-t-[#5b4df5]" /></div>;
  }

  const signOut = async () => {
    await logout();
    router.replace("/login");
  };

  return (
    <div className="min-h-screen bg-[#f7f8fb] lg:grid lg:grid-cols-[252px_1fr]">
      <button aria-label="Open navigation" className="fixed left-4 top-4 z-40 rounded-xl border bg-white p-2 shadow-sm lg:hidden" onClick={() => setMobileOpen(true)}><Menu className="size-5" /></button>
      {mobileOpen && <button aria-label="Close navigation" className="fixed inset-0 z-40 bg-black/30 lg:hidden" onClick={() => setMobileOpen(false)} />}
      <aside className={`fixed inset-y-0 left-0 z-50 flex w-[252px] flex-col border-r border-[#e4e7ec] bg-white transition-transform lg:sticky lg:top-0 lg:h-screen lg:translate-x-0 ${mobileOpen ? "translate-x-0" : "-translate-x-full"}`}>
        <div className="flex h-20 items-center justify-between px-5">
          <Link className="flex items-center gap-2 text-lg font-bold" href="/dashboard"><span className="grid size-8 place-items-center rounded-xl bg-[#5b4df5] text-sm text-white">R</span>{process.env.NEXT_PUBLIC_APP_NAME ?? "Rolewise"}</Link>
          <button aria-label="Close navigation" className="lg:hidden" onClick={() => setMobileOpen(false)}><X className="size-5" /></button>
        </div>
        <div className="mx-3 mb-4 rounded-2xl border border-[#e4e7ec] bg-[#fafafa] p-3">
          <div className="flex items-center gap-3"><div className="grid size-9 place-items-center rounded-xl bg-[#eceaff] text-sm font-bold text-[#5b4df5]">{user.full_name.charAt(0).toUpperCase()}</div><div className="min-w-0 flex-1"><p className="truncate text-sm font-semibold">{user.full_name}</p><p className="truncate text-xs text-[#667085]">Personal workspace</p></div><ChevronDown className="size-4 text-[#98a2b3]" /></div>
        </div>
        <nav className="flex-1 space-y-1 overflow-y-auto px-3 pb-4">
          {nav.map(({ href, label, icon: Icon }) => {
            const active = pathname === href || (href !== "/dashboard" && pathname.startsWith(href));
            return <Link className={`flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition ${active ? "bg-[#eeecff] text-[#4b3ed0]" : "text-[#475467] hover:bg-[#f5f6f8]"}`} href={href} key={href} onClick={() => setMobileOpen(false)}><Icon className="size-[18px]" />{label}</Link>;
          })}
        </nav>
        <div className="space-y-1 border-t border-[#e4e7ec] p-3">
          <Link className="flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-[#475467] hover:bg-[#f5f6f8]" href="/settings"><Settings className="size-[18px]" />Settings</Link>
          <button className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-[#475467] hover:bg-[#fff0f0] hover:text-red-700" onClick={signOut}><LogOut className="size-[18px]" />Sign out</button>
        </div>
      </aside>
      <main className="min-w-0 px-5 pb-12 pt-20 sm:px-8 lg:px-10 lg:pt-9 xl:px-12">{children}</main>
    </div>
  );
}

export function PageHeader({ eyebrow, title, description, action }: { eyebrow?: string; title: string; description: string; action?: ReactNode }) {
  return <header className="flex flex-col gap-5 sm:flex-row sm:items-end sm:justify-between"><div>{eyebrow && <p className="mb-2 text-xs font-bold uppercase tracking-[.16em] text-[#5b4df5]">{eyebrow}</p>}<h1 className="text-3xl font-semibold tracking-[-.035em] text-[#182036] sm:text-4xl">{title}</h1><p className="mt-2 max-w-2xl text-sm leading-6 text-[#667085]">{description}</p></div>{action}</header>;
}

export function PlaceholderPage({ title, description }: { title: string; description: string }) {
  return <><PageHeader title={title} description={description} /><section className="mt-8 rounded-3xl border border-dashed border-[#cfd3dc] bg-white p-12 text-center"><BarChart3 className="mx-auto size-8 text-[#8c83f7]" /><h2 className="mt-4 font-semibold">This workspace is next in the build</h2><p className="mx-auto mt-2 max-w-md text-sm leading-6 text-[#667085]">Its API and workflow will arrive as the related domain increment is completed.</p></section></>;
}

