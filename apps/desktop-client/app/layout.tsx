import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ATLAS AI-OS | Personal Cognitive Console",
  description: "Autonomous Thinking Learning Assistance System — Control Deck",
  applicationName: "A.T.L.A.S",
  authors: [{ name: "ATLAS" }],
  keywords: ["atlas", "ai", "assistant", "cognitive", "jarvis"],
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className="dark">
      <body className="font-display antialiased">{children}</body>
    </html>
  );
}
