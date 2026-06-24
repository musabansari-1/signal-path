import type { Metadata } from "next";
import { AuthForm } from "@/components/auth-form";

export const metadata: Metadata = { title: "Create account" };

export default function RegisterPage() {
  return <><p className="text-sm font-semibold text-[#5b4df5]">Start with your goals</p><h1 className="mt-2 text-4xl font-semibold tracking-[-.04em]">Build a calmer job search.</h1><p className="mt-3 text-[#667085]">Create a workspace that keeps the signal and loses the spreadsheet chaos.</p><AuthForm mode="register" /></>;
}

