import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Government Service Router",
  description:
    "Find the right government office for your needs — powered by AI",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50 text-gray-900 antialiased">
        {children}
      </body>
    </html>
  );
}
