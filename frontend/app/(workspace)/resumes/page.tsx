import { ResumeWorkspace } from "@/components/resume-workspace";

export default async function ResumesPage({
  searchParams,
}: {
  searchParams: Promise<{ job?: string }>;
}) {
  const { job } = await searchParams;
  return <ResumeWorkspace initialJobId={job} />;
}

