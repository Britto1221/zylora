import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  metadataBase: new URL(
    process.env.NEXT_PUBLIC_APP_URL ?? "http://localhost:3000",
  ),
  title: {
    default: "Zylora — Digital Business Infrastructure",
    template: "%s | Zylora",
  },
  description:
    "Premium websites, lead operations, AI knowledge, communication, publishing, and growth infrastructure for modern businesses.",
  keywords: [
    "business website platform",
    "lead management",
    "AI business assistant",
    "managed websites",
    "business automation",
    "Zylora",
  ],
  openGraph: {
    title: "Zylora — Digital Business Infrastructure",
    description:
      "Turn your digital presence into a connected business system.",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Zylora — Digital Business Infrastructure",
    description:
      "Premium websites, leads, AI knowledge, communication, and growth operations.",
  },
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
