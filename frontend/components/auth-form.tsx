"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { ArrowRight, LoaderCircle } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { cloneElement, useState, type ReactElement } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { useAuth } from "@/components/auth-provider";
import { apiRequest } from "@/lib/api";
import type { User } from "@/lib/types";

const schema = z.object({
  full_name: z.string().min(2, "Enter your name").optional(),
  email: z.email("Enter a valid email"),
  password: z.string().min(8, "Use at least 8 characters"),
});
type FormValues = z.infer<typeof schema>;

export function AuthForm({ mode }: { mode: "login" | "register" }) {
  const router = useRouter();
  const { setUser } = useAuth();
  const [serverError, setServerError] = useState("");
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<FormValues>({
    resolver: zodResolver(schema),
  });

  const onSubmit = async (values: FormValues) => {
    setServerError("");
    try {
      const user = await apiRequest<User>(`/auth/${mode}`, {
        method: "POST",
        body: JSON.stringify(values),
      });
      setUser(user);
      router.push("/dashboard");
    } catch (error) {
      setServerError(error instanceof Error ? error.message : "Unable to continue");
    }
  };

  return (
    <form className="mt-8 space-y-5" onSubmit={handleSubmit(onSubmit)}>
      {mode === "register" && <Field label="Full name" error={errors.full_name?.message}><input autoComplete="name" {...register("full_name")} /></Field>}
      <Field label="Email" error={errors.email?.message}><input autoComplete="email" type="email" {...register("email")} /></Field>
      <Field label="Password" error={errors.password?.message}><input autoComplete={mode === "login" ? "current-password" : "new-password"} type="password" {...register("password")} /></Field>
      {serverError && <p className="rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700" role="alert">{serverError}</p>}
      <button className="flex w-full items-center justify-center gap-2 rounded-2xl bg-[#5b4df5] px-5 py-3.5 font-semibold text-white hover:bg-[#493bdb] disabled:opacity-60" disabled={isSubmitting} type="submit">
        {isSubmitting ? <LoaderCircle className="size-4 animate-spin" /> : <ArrowRight className="size-4" />}
        {mode === "login" ? "Sign in" : "Create my workspace"}
      </button>
      <p className="text-center text-sm text-[#667085]">
        {mode === "login" ? "New to Rolewise? " : "Already have an account? "}
        <Link className="font-semibold text-[#5b4df5]" href={mode === "login" ? "/register" : "/login"}>{mode === "login" ? "Create an account" : "Sign in"}</Link>
      </p>
    </form>
  );
}

function Field({ label, error, children }: { label: string; error?: string; children: ReactElement<{ className?: string }> }) {
  return (
    <label className="block text-sm font-semibold text-[#344054]">
      {label}
      <span className="mt-2 block">{cloneElement(children, { className: "w-full rounded-xl border border-[#d0d5dd] bg-white px-4 py-3 outline-none transition focus:border-[#5b4df5] focus:ring-4 focus:ring-[#eeecff]" })}</span>
      {error && <span className="mt-1.5 block text-xs font-medium text-red-600">{error}</span>}
    </label>
  );
}
