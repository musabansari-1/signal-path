import { PageHeader } from "@/components/app-shell";

const items = [
  ["CSV import", "Available now for job intake."],
  ["Google Sheets", "Planned for import/export after core workflow stability."],
  ["Apify/job sources", "Future integration boundary; no aggressive scraping in v1."],
  ["Gmail/Calendar", "Future draft/reminder integrations; no auto-send behavior."],
];

export default function IntegrationsPage() {
  return <><PageHeader eyebrow="Extension points" title="Integrations" description="The MVP favors safe manual input and CSV boundaries. Later connectors can slot into the same project-scoped domain model." /><section className="mt-8 grid gap-4 md:grid-cols-2">{items.map(([title, description]) => <article className="rounded-3xl border border-[#e4e7ec] bg-white p-6" key={title}><h2 className="font-semibold">{title}</h2><p className="mt-2 text-sm leading-6 text-[#667085]">{description}</p></article>)}</section></>;
}
