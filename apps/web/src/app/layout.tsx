import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Zylora",
  description: "Managed websites, leads, WhatsApp follow-up, and SEO.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
