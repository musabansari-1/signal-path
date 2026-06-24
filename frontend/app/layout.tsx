import type { Metadata } from "next";
import type { ReactNode } from "react";

import "./globals.css";

const appName = process.env.NEXT_PUBLIC_APP_NAME ?? "Rolewise";

export const metadata: Metadata = {
  title: { default: appName, template: `%s · ${appName}` },
  description: "A truthful AI workspace for better job applications.",
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

