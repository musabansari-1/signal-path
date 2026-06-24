import type { Metadata } from "next";
import { AuthForm } from "@/components/auth-form";

export const metadata: Metadata = { title: "Sign in" };

export default function LoginPage() {
  return <><p className="text-sm font-semibold text-[#5b4df5]">Welcome back</p><h1 className="mt-2 text-4xl font-semibold tracking-[-.04em]">Pick up where you left off.</h1><p className="mt-3 text-[#667085]">Your opportunities, drafts, and next actions are waiting.</p><AuthForm mode="login" /></>;
}

