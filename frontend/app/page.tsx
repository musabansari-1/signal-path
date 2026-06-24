import { ArrowRight, CheckCircle2, Compass, FileCheck2, ShieldCheck } from "lucide-react";
import Link from "next/link";

const appName = process.env.NEXT_PUBLIC_APP_NAME ?? "Rolewise";

const features = [
  { icon: Compass, title: "Choose the right roles", text: "Compare each opportunity with your real goals, skills, and constraints." },
  { icon: FileCheck2, title: "Build stronger applications", text: "Tailor honest, ATS-friendly materials without manufacturing experience." },
  { icon: ShieldCheck, title: "Stay in control", text: "Review every suggestion. Nothing is submitted or sent behind your back." },
];

export default function LandingPage() {
  return (
    <main className="min-h-screen overflow-hidden bg-[#f8f8fc]">
      <nav className="mx-auto flex max-w-7xl items-center justify-between px-6 py-6 lg:px-8">
        <Link className="flex items-center gap-2 text-lg font-bold tracking-tight" href="/">
          <span className="grid size-8 place-items-center rounded-xl bg-[#5b4df5] text-sm text-white">R</span>
          {appName}
        </Link>
        <div className="flex items-center gap-3">
          <Link className="rounded-xl px-4 py-2 text-sm font-semibold text-[#475467] hover:bg-white" href="/login">Sign in</Link>
          <Link className="rounded-xl bg-[#172033] px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-black" href="/register">Start your search</Link>
        </div>
      </nav>

      <section className="relative mx-auto grid max-w-7xl gap-14 px-6 pb-24 pt-16 lg:grid-cols-[1.05fr_.95fr] lg:px-8 lg:pt-24">
        <div className="relative z-10">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-[#ddd9ff] bg-white px-3 py-1.5 text-sm font-medium text-[#4b3ed0] shadow-sm">
            <CheckCircle2 className="size-4" /> Thoughtful applications beat more applications
          </div>
          <h1 className="max-w-3xl text-5xl font-semibold leading-[1.02] tracking-[-0.055em] text-[#182036] sm:text-6xl lg:text-7xl">
            Run your job search with <span className="text-[#5b4df5]">clarity.</span>
          </h1>
          <p className="mt-7 max-w-xl text-lg leading-8 text-[#667085]">
            Score opportunities, tailor truthful applications, track every conversation, and walk into interviews prepared.
          </p>
          <div className="mt-9 flex flex-wrap items-center gap-4">
            <Link className="inline-flex items-center gap-2 rounded-2xl bg-[#5b4df5] px-6 py-3.5 font-semibold text-white shadow-[0_12px_30px_rgba(91,77,245,.25)] hover:bg-[#493bdb]" href="/register">
              Build my workspace <ArrowRight className="size-4" />
            </Link>
            <span className="text-sm text-[#667085]">No auto-apply. No invented claims.</span>
          </div>
        </div>

        <div className="relative">
          <div className="absolute -inset-20 -z-10 rounded-full bg-[radial-gradient(circle,#ddd9ff_0,transparent_65%)] opacity-80" />
          <div className="rotate-1 rounded-[2rem] border border-white bg-white/90 p-4 shadow-[0_32px_80px_rgba(38,34,82,.16)] backdrop-blur">
            <div className="rounded-[1.5rem] bg-[#172033] p-6 text-white">
              <div className="flex items-center justify-between text-sm text-[#adb5c7]"><span>Opportunity fit</span><span>Just now</span></div>
              <div className="mt-8 flex items-end justify-between">
                <div><p className="text-sm text-[#adb5c7]">Product engineer · Loomly</p><p className="mt-1 text-2xl font-semibold">Strong match</p></div>
                <div className="grid size-20 place-items-center rounded-full border-[7px] border-[#77e4ba] text-2xl font-bold">87</div>
              </div>
            </div>
            <div className="grid gap-3 p-3 pt-4 sm:grid-cols-2">
              <div className="rounded-2xl bg-[#eefbf6] p-4"><p className="text-xs font-bold uppercase tracking-wider text-[#187957]">Your edge</p><p className="mt-2 text-sm leading-6 text-[#344054]">Strong TypeScript, API, and product delivery alignment.</p></div>
              <div className="rounded-2xl bg-[#fff7ed] p-4"><p className="text-xs font-bold uppercase tracking-wider text-[#b54708]">Prepare for</p><p className="mt-2 text-sm leading-6 text-[#344054]">Role asks for GraphQL; your profile does not claim it.</p></div>
            </div>
          </div>
        </div>
      </section>

      <section className="border-y border-[#e8e9ef] bg-white px-6 py-20 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <p className="text-sm font-bold uppercase tracking-[.18em] text-[#5b4df5]">One focused system</p>
          <h2 className="mt-4 max-w-2xl text-3xl font-semibold tracking-[-.035em] sm:text-4xl">From “should I apply?” to “I’m ready for the interview.”</h2>
          <div className="mt-10 grid gap-5 md:grid-cols-3">
            {features.map(({ icon: Icon, title, text }) => (
              <article className="rounded-3xl border border-[#e7e8ee] bg-[#fbfbfd] p-6" key={title}>
                <div className="grid size-11 place-items-center rounded-2xl bg-[#eceaff] text-[#5b4df5]"><Icon className="size-5" /></div>
                <h3 className="mt-5 text-lg font-semibold">{title}</h3>
                <p className="mt-2 text-sm leading-6 text-[#667085]">{text}</p>
              </article>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}

