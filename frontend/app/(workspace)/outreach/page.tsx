import { OutreachWorkspace } from "@/components/outreach-workspace";

export default async function OutreachPage({
  searchParams,
}: {
  searchParams: Promise<{ job?: string }>;
}) {
  const { job } = await searchParams;
  return <OutreachWorkspace initialJobId={job} />;
}

