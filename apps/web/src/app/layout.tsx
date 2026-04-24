import type { Metadata } from "next";
import type { ReactNode } from "react";
import "./globals.css";

export const metadata: Metadata = {
  title: "SFS Console",
  description: "Shortform Factory Studio production console"
};

export default function RootLayout({
  children
}: Readonly<{
  children: ReactNode;
}>) {
  return (
    <html lang="ko-KR">
      <body>{children}</body>
    </html>
  );
}
