import type { Metadata, Viewport } from "next";
import { Newsreader, Manrope, DM_Mono } from "next/font/google";
import "./globals.css";

const newsreader = Newsreader({
  subsets: ["latin"],
  style: ["normal", "italic"],
  variable: "--font-newsreader",
  display: "swap",
});

const manrope = Manrope({
  subsets: ["latin"],
  variable: "--font-manrope",
  display: "swap",
});

const dmMono = DM_Mono({
  weight: ["400", "500"],
  subsets: ["latin"],
  variable: "--font-dm-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Obsidian Ledger — Personal Finance AI Advisor",
  description:
    "An intelligent financial advisory system for Indian markets. Live spot bullion pricing in INR, grounded GST & SEBI reference retrieval, and Gemini-powered orchestration.",
  keywords: ["Finance Advisor", "Gold Price INR", "Silver Spot Rate", "GST India", "SEBI Regulations"],
  authors: [{ name: "Finance Advisor Team" }],
};

export const viewport: Viewport = {
  themeColor: "#111713",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`${newsreader.variable} ${manrope.variable} ${dmMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-[#F5F3EC] text-[#252B27] selection:bg-[#D8FF57] selection:text-[#111713]">
        {children}
      </body>
    </html>
  );
}
