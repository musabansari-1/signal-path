import type { ReactNode } from "react";
import Link from "next/link";

export default function AuthLayout({ children }: { children: ReactNode }) {
  const appName = process.env.NEXT_PUBLIC_APP_NAME ?? "Rolewise";
  return (
    <main className="grid min-h-screen bg-white lg:grid-cols-[.9fr_1.1fr]">
      <section className="flex min-h-screen flex-col px-6 py-7 sm:px-12 lg:px-16">
        <Link className="flex items-center gap-2 text-lg font-bold" href="/"><span className="grid size-8 place-items-center rounded-xl bg-[#5b4df5] text-sm text-white">R</span>{appName}</Link>
        <div className="my-auto w-full max-w-md self-center py-12">{children}</div>
        <p className="text-xs text-[#98a2b3]">Your career data stays private and under your control.</p>
      </section>
      <aside className="relative hidden overflow-hidden bg-[#18172a] p-16 text-white lg:block">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_75%_25%,rgba(91,77,245,.55),transparent_38%),radial-gradient(circle_at_20%_80%,rgba(65,211,157,.22),transparent_34%)]" />
        <div className="relative flex h-full max-w-xl flex-col justify-center">
          <p className="text-sm font-bold uppercase tracking-[.18em] text-[#9c94ff]">Built for considered searches</p>
          <blockquote className="mt-6 text-4xl font-medium leading-[1.18] tracking-[-.035em]">“Make every application more intentional, more honest, and much easier to manage.”</blockquote>
          <div className="mt-12 grid grid-cols-3 gap-3 text-sm text-[#c9c7d8]"><span>Explainable fit</span><span>Truthful tailoring</span><span>Human approval</span></div>
        </div>
      </aside>
    </main>
  );
}

